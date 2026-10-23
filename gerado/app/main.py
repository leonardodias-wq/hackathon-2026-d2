import csv
import io
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.business import (
    find_em_andamento,
    find_overlap,
    normalize_email,
    parse_dt,
    row_to_lancamento,
    row_to_projeto,
    validate_cor,
    validate_finalizado,
)
from app.database import get_connection, init_db

app = FastAPI(title="Controle de Horas")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class ProjetoCreate(BaseModel):
    nome: str = Field(min_length=1)
    cliente: str = Field(min_length=1)
    cor: str


class LancamentoCreate(BaseModel):
    projeto_id: int
    colaborador_nome: str = Field(min_length=1)
    colaborador_email: str = Field(min_length=1)
    descricao: str = Field(min_length=1)
    inicio: str
    fim: str


class LancamentoUpdate(BaseModel):
    projeto_id: int | None = None
    descricao: str | None = None
    inicio: str | None = None
    fim: str | None = None


class CronometroIniciar(BaseModel):
    projeto_id: int
    colaborador_nome: str = Field(min_length=1)
    colaborador_email: str = Field(min_length=1)
    descricao: str = Field(min_length=1)


class CronometroParar(BaseModel):
    email: str = Field(min_length=1)


def _projeto_or_404(conn, projeto_id: int) -> dict:
    row = conn.execute("SELECT * FROM projetos WHERE id = ?", (projeto_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Projeto não encontrado")
    return row_to_projeto(row)


def _lancamento_or_404(conn, lancamento_id: int):
    row = conn.execute("SELECT * FROM lancamentos WHERE id = ?", (lancamento_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Lançamento não encontrado")
    return row


def _periodo_finalizados(conn, data_inicio: str, data_fim: str):
    """Lançamentos FINALIZADOS cujo início cai no intervalo de datas (inclusivo)."""
    try:
        di = datetime.fromisoformat(data_inicio).date()
        df = datetime.fromisoformat(data_fim).date()
    except ValueError as exc:
        raise HTTPException(400, "Datas inválidas; use YYYY-MM-DD") from exc
    if df < di:
        raise HTTPException(400, "data_fim deve ser >= data_inicio")

    rows = conn.execute(
        """
        SELECT l.*, p.nome AS projeto_nome, p.cliente AS projeto_cliente
        FROM lancamentos l
        JOIN projetos p ON p.id = l.projeto_id
        WHERE l.status = 'FINALIZADO'
          AND date(l.inicio) >= date(?)
          AND date(l.inicio) <= date(?)
        ORDER BY l.inicio
        """,
        (di.isoformat(), df.isoformat()),
    ).fetchall()
    return rows


@app.on_event("startup")
def startup() -> None:
    conn = get_connection()
    init_db(conn)
    conn.close()


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/projetos")
def list_projetos():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM projetos ORDER BY id").fetchall()
    conn.close()
    return [row_to_projeto(r) for r in rows]


@app.post("/api/projetos", status_code=201)
def create_projeto(body: ProjetoCreate):
    try:
        cor = validate_cor(body.cor)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO projetos (nome, cliente, cor) VALUES (?, ?, ?)",
        (body.nome.strip(), body.cliente.strip(), cor),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM projetos WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_projeto(row)


@app.get("/api/lancamentos")
def list_lancamentos(
    email: str = Query(...),
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
):
    try:
        di = datetime.fromisoformat(data_inicio).date()
        df = datetime.fromisoformat(data_fim).date()
    except ValueError as exc:
        raise HTTPException(400, "Datas inválidas; use YYYY-MM-DD") from exc
    if df < di:
        raise HTTPException(400, "data_fim deve ser >= data_inicio")

    conn = get_connection()
    rows = conn.execute(
        """
        SELECT * FROM lancamentos
        WHERE lower(colaborador_email) = ?
          AND date(inicio) >= date(?)
          AND date(inicio) <= date(?)
        ORDER BY inicio
        """,
        (normalize_email(email), di.isoformat(), df.isoformat()),
    ).fetchall()
    result = [row_to_lancamento(r) for r in rows]
    conn.close()
    return result


@app.post("/api/lancamentos", status_code=201)
def create_lancamento(body: LancamentoCreate):
    try:
        inicio = parse_dt(body.inicio)
        fim = parse_dt(body.fim)
        validate_finalizado(inicio, fim)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    conn = get_connection()
    _projeto_or_404(conn, body.projeto_id)
    conflict = find_overlap(conn, body.colaborador_email, inicio, fim)
    if conflict:
        conn.close()
        raise HTTPException(
            409,
            f"Conflito de horário com lançamento #{conflict['id']}",
        )

    cur = conn.execute(
        """
        INSERT INTO lancamentos
        (projeto_id, colaborador_nome, colaborador_email, descricao, inicio, fim, status)
        VALUES (?, ?, ?, ?, ?, ?, 'FINALIZADO')
        """,
        (
            body.projeto_id,
            body.colaborador_nome.strip(),
            body.colaborador_email.strip(),
            body.descricao.strip(),
            inicio.isoformat(timespec="seconds"),
            fim.isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    row = _lancamento_or_404(conn, cur.lastrowid)
    result = row_to_lancamento(row)
    conn.close()
    return result


@app.patch("/api/lancamentos/{lancamento_id}")
def update_lancamento(lancamento_id: int, body: LancamentoUpdate):
    conn = get_connection()
    row = _lancamento_or_404(conn, lancamento_id)
    if row["status"] != "FINALIZADO":
        conn.close()
        raise HTTPException(400, "Só lançamentos FINALIZADO podem ser editados")

    projeto_id = body.projeto_id if body.projeto_id is not None else row["projeto_id"]
    descricao = body.descricao.strip() if body.descricao is not None else row["descricao"]
    inicio_s = body.inicio if body.inicio is not None else row["inicio"]
    fim_s = body.fim if body.fim is not None else row["fim"]

    if body.projeto_id is not None:
        _projeto_or_404(conn, projeto_id)

    try:
        inicio = parse_dt(inicio_s)
        fim = parse_dt(fim_s)
        # Edição: não revalida "início no futuro" com agora se já era passado;
        # mas se o usuário setar início futuro, recusa.
        validate_finalizado(inicio, fim)
    except ValueError as exc:
        conn.close()
        raise HTTPException(400, str(exc)) from exc

    conflict = find_overlap(
        conn, row["colaborador_email"], inicio, fim, exclude_id=lancamento_id
    )
    if conflict:
        conn.close()
        raise HTTPException(
            409,
            f"Conflito de horário com lançamento #{conflict['id']}",
        )

    conn.execute(
        """
        UPDATE lancamentos
        SET projeto_id = ?, descricao = ?, inicio = ?, fim = ?
        WHERE id = ?
        """,
        (
            projeto_id,
            descricao,
            inicio.isoformat(timespec="seconds"),
            fim.isoformat(timespec="seconds"),
            lancamento_id,
        ),
    )
    conn.commit()
    updated = _lancamento_or_404(conn, lancamento_id)
    result = row_to_lancamento(updated)
    conn.close()
    return result


@app.delete("/api/lancamentos/{lancamento_id}", status_code=204)
def delete_lancamento(lancamento_id: int):
    conn = get_connection()
    row = _lancamento_or_404(conn, lancamento_id)
    if row["status"] != "EM_ANDAMENTO":
        conn.close()
        raise HTTPException(400, "Só lançamentos EM_ANDAMENTO podem ser excluídos")
    conn.execute("DELETE FROM lancamentos WHERE id = ?", (lancamento_id,))
    conn.commit()
    conn.close()
    return None


@app.post("/api/cronometro/iniciar", status_code=201)
def cronometro_iniciar(body: CronometroIniciar):
    conn = get_connection()
    _projeto_or_404(conn, body.projeto_id)
    existing = find_em_andamento(conn, body.colaborador_email)
    if existing:
        conn.close()
        raise HTTPException(
            409,
            f"Já existe lançamento EM_ANDAMENTO (#{existing['id']}) para este e-mail",
        )

    agora = datetime.now().replace(microsecond=0)
    cur = conn.execute(
        """
        INSERT INTO lancamentos
        (projeto_id, colaborador_nome, colaborador_email, descricao, inicio, fim, status)
        VALUES (?, ?, ?, ?, ?, NULL, 'EM_ANDAMENTO')
        """,
        (
            body.projeto_id,
            body.colaborador_nome.strip(),
            body.colaborador_email.strip(),
            body.descricao.strip(),
            agora.isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    row = _lancamento_or_404(conn, cur.lastrowid)
    result = row_to_lancamento(row)
    conn.close()
    return result


@app.post("/api/cronometro/parar")
def cronometro_parar(body: CronometroParar):
    conn = get_connection()
    row = conn.execute(
        """
        SELECT * FROM lancamentos
        WHERE lower(colaborador_email) = ? AND status = 'EM_ANDAMENTO'
        LIMIT 1
        """,
        (normalize_email(body.email),),
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Nenhum cronômetro EM_ANDAMENTO para este e-mail")

    agora = datetime.now().replace(microsecond=0)
    try:
        inicio = parse_dt(row["inicio"])
        validate_finalizado(inicio, agora)
    except ValueError as exc:
        conn.close()
        raise HTTPException(400, str(exc)) from exc

    conflict = find_overlap(conn, row["colaborador_email"], inicio, agora)
    if conflict:
        conn.close()
        raise HTTPException(
            409,
            f"Conflito de horário com lançamento #{conflict['id']}",
        )

    conn.execute(
        """
        UPDATE lancamentos
        SET fim = ?, status = 'FINALIZADO'
        WHERE id = ?
        """,
        (agora.isoformat(timespec="seconds"), row["id"]),
    )
    conn.commit()
    updated = _lancamento_or_404(conn, row["id"])
    result = row_to_lancamento(updated)
    conn.close()
    return result


@app.get("/api/relatorio")
def relatorio(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
):
    conn = get_connection()
    rows = _periodo_finalizados(conn, data_inicio, data_fim)

    por_projeto: dict[str, dict] = {}
    por_colaborador: dict[str, dict] = {}

    for row in rows:
        inicio = parse_dt(row["inicio"])
        fim = parse_dt(row["fim"])
        mins = int((fim - inicio).total_seconds() // 60)

        key_p = row["projeto_id"]
        if key_p not in por_projeto:
            por_projeto[key_p] = {
                "projeto_id": row["projeto_id"],
                "projeto": row["projeto_nome"],
                "cliente": row["projeto_cliente"],
                "total_minutos": 0,
            }
        por_projeto[key_p]["total_minutos"] += mins

        email = normalize_email(row["colaborador_email"])
        if email not in por_colaborador:
            por_colaborador[email] = {
                "colaborador": row["colaborador_nome"],
                "email": row["colaborador_email"],
                "total_minutos": 0,
            }
        por_colaborador[email]["total_minutos"] += mins

    conn.close()
    return {
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "por_projeto": list(por_projeto.values()),
        "por_colaborador": list(por_colaborador.values()),
    }


@app.get("/api/relatorio/csv")
def relatorio_csv(
    data_inicio: str = Query(...),
    data_fim: str = Query(...),
):
    conn = get_connection()
    rows = _periodo_finalizados(conn, data_inicio, data_fim)
    conn.close()

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "projeto",
            "cliente",
            "colaborador",
            "email",
            "descricao",
            "inicio",
            "fim",
            "duracao_minutos",
            "status",
        ]
    )
    for row in rows:
        inicio = parse_dt(row["inicio"])
        fim = parse_dt(row["fim"])
        mins = int((fim - inicio).total_seconds() // 60)
        writer.writerow(
            [
                row["projeto_nome"],
                row["projeto_cliente"],
                row["colaborador_nome"],
                row["colaborador_email"],
                row["descricao"],
                row["inicio"],
                row["fim"],
                mins,
                row["status"],
            ]
        )

    buf.seek(0)
    filename = f"horas_{data_inicio}_{data_fim}.csv"
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
