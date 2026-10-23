from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException

from .database import LOCAIS, RECURSOS, connect, row_reserva, row_sala

DURACAO_MIN = timedelta(minutes=15)
DURACAO_MAX = timedelta(hours=4)
JANELA_INICIO = 8  # 08:00
JANELA_FIM = 18  # 18:00
MINUTOS_JANELA = (JANELA_FIM - JANELA_INICIO) * 60  # 600


def parse_dt(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", ""))
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Data/hora inválida (use ISO).") from exc


def to_iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def validar_local(local: str) -> None:
    if local not in LOCAIS:
        raise HTTPException(
            status_code=400,
            detail=f"Local inválido. Use: {', '.join(LOCAIS)}",
        )


def validar_recursos(recursos: list) -> list:
    if not isinstance(recursos, list):
        raise HTTPException(status_code=400, detail="recursos deve ser uma lista.")
    limpos = []
    for r in recursos:
        if r not in RECURSOS:
            raise HTTPException(
                status_code=400,
                detail=f"Recurso inválido: {r}. Use: {', '.join(RECURSOS)}",
            )
        if r not in limpos:
            limpos.append(r)
    return limpos


def get_sala(sala_id: int) -> dict:
    with connect() as conn:
        row = conn.execute("SELECT * FROM salas WHERE id = ?", (sala_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sala não encontrada.")
    return row_sala(row)


def listar_salas() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM salas ORDER BY id").fetchall()
    return [row_sala(r) for r in rows]


def criar_sala(nome: str, local: str, capacidade: int, recursos: list) -> dict:
    nome = (nome or "").strip()
    if not nome:
        raise HTTPException(status_code=400, detail="Nome da sala é obrigatório.")
    validar_local(local)
    if not isinstance(capacidade, int) or capacidade < 1:
        raise HTTPException(status_code=400, detail="Capacidade deve ser inteiro ≥ 1.")
    recursos = validar_recursos(recursos or [])
    import json

    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO salas (nome, local, capacidade, recursos) VALUES (?, ?, ?, ?)",
            (nome, local, capacidade, json.dumps(recursos)),
        )
        conn.commit()
        sala_id = cur.lastrowid
        row = conn.execute("SELECT * FROM salas WHERE id = ?", (sala_id,)).fetchone()
    return row_sala(row)


def _conflito(sala_id: int, inicio: datetime, fim: datetime, excluir_id: Optional[int] = None) -> bool:
    sql = """
        SELECT id FROM reservas
        WHERE sala_id = ? AND status = 'ATIVA'
          AND inicio < ? AND fim > ?
    """
    params: list = [sala_id, to_iso(fim), to_iso(inicio)]
    if excluir_id is not None:
        sql += " AND id != ?"
        params.append(excluir_id)
    with connect() as conn:
        row = conn.execute(sql, params).fetchone()
    return row is not None


def validar_reserva(
    sala_id: int,
    participantes: int,
    inicio: datetime,
    fim: datetime,
    agora: Optional[datetime] = None,
) -> dict:
    agora = agora or datetime.now()
    sala = get_sala(sala_id)

    if inicio >= fim:
        raise HTTPException(status_code=400, detail="Início deve ser anterior ao fim.")
    if inicio < agora:
        raise HTTPException(status_code=400, detail="Não é possível reservar no passado.")

    duracao = fim - inicio
    if duracao < DURACAO_MIN:
        raise HTTPException(
            status_code=400,
            detail="Duração mínima é de 15 minutos.",
        )
    if duracao > DURACAO_MAX:
        raise HTTPException(
            status_code=400,
            detail="Duração máxima é de 4 horas.",
        )

    if not isinstance(participantes, int) or participantes < 1:
        raise HTTPException(status_code=400, detail="Participantes deve ser inteiro ≥ 1.")
    if participantes > sala["capacidade"]:
        raise HTTPException(
            status_code=400,
            detail=f"Participantes ({participantes}) excedem a capacidade ({sala['capacidade']}).",
        )

    if _conflito(sala_id, inicio, fim):
        raise HTTPException(
            status_code=409,
            detail="Conflito de horário: a sala já possui reserva ativa neste intervalo.",
        )
    return sala


def criar_reserva(
    sala_id: int,
    responsavel_nome: str,
    responsavel_email: str,
    titulo: str,
    participantes: int,
    inicio_str: str,
    fim_str: str,
    agora: Optional[datetime] = None,
) -> dict:
    nome = (responsavel_nome or "").strip()
    email = (responsavel_email or "").strip()
    titulo = (titulo or "").strip()
    if not nome or not email or not titulo:
        raise HTTPException(
            status_code=400,
            detail="responsável (nome e e-mail) e título são obrigatórios.",
        )
    inicio = parse_dt(inicio_str)
    fim = parse_dt(fim_str)
    validar_reserva(sala_id, participantes, inicio, fim, agora=agora)

    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO reservas
            (sala_id, responsavel_nome, responsavel_email, titulo, participantes, inicio, fim, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ATIVA')
            """,
            (sala_id, nome, email, titulo, participantes, to_iso(inicio), to_iso(fim)),
        )
        conn.commit()
        rid = cur.lastrowid
        row = conn.execute("SELECT * FROM reservas WHERE id = ?", (rid,)).fetchone()
    return row_reserva(row)


def listar_reservas(data: Optional[str] = None, sala_id: Optional[int] = None) -> list[dict]:
    sql = """
        SELECT r.*, s.nome AS sala_nome
        FROM reservas r
        JOIN salas s ON s.id = r.sala_id
        WHERE 1=1
    """
    params: list = []
    if data:
        try:
            datetime.strptime(data, "%Y-%m-%d")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="data deve ser YYYY-MM-DD.") from exc
        sql += " AND date(r.inicio) = ?"
        params.append(data)
    if sala_id is not None:
        sql += " AND r.sala_id = ?"
        params.append(sala_id)
    sql += " ORDER BY r.inicio"
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_reserva(r) for r in rows]


def cancelar_reserva(reserva_id: int, agora: Optional[datetime] = None) -> dict:
    agora = agora or datetime.now()
    with connect() as conn:
        row = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Reserva não encontrada.")
        if row["status"] == "CANCELADA":
            raise HTTPException(status_code=400, detail="Reserva já está cancelada.")
        fim = parse_dt(row["fim"])
        if fim <= agora:
            raise HTTPException(
                status_code=400,
                detail="Não é possível cancelar reserva que já passou.",
            )
        conn.execute(
            "UPDATE reservas SET status = 'CANCELADA' WHERE id = ?",
            (reserva_id,),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,)).fetchone()
    return row_reserva(row)


def salas_livres(
    inicio_str: str,
    fim_str: str,
    local: Optional[str] = None,
    capacidade_min: Optional[int] = None,
) -> list[dict]:
    inicio = parse_dt(inicio_str)
    fim = parse_dt(fim_str)
    if inicio >= fim:
        raise HTTPException(status_code=400, detail="Início deve ser anterior ao fim.")
    if local:
        validar_local(local)
    if capacidade_min is not None and capacidade_min < 1:
        raise HTTPException(status_code=400, detail="capacidade_min deve ser ≥ 1.")

    sql = "SELECT * FROM salas WHERE 1=1"
    params: list = []
    if local:
        sql += " AND local = ?"
        params.append(local)
    if capacidade_min is not None:
        sql += " AND capacidade >= ?"
        params.append(capacidade_min)
    sql += " ORDER BY id"

    livres = []
    with connect() as conn:
        salas = conn.execute(sql, params).fetchall()
        for sala in salas:
            conflito = conn.execute(
                """
                SELECT id FROM reservas
                WHERE sala_id = ? AND status = 'ATIVA'
                  AND inicio < ? AND fim > ?
                """,
                (sala["id"], to_iso(fim), to_iso(inicio)),
            ).fetchone()
            if not conflito:
                livres.append(row_sala(sala))
    return livres


def _clip_minutos(inicio: datetime, fim: datetime, dia: datetime) -> int:
    janela_ini = dia.replace(hour=JANELA_INICIO, minute=0, second=0, microsecond=0)
    janela_fim = dia.replace(hour=JANELA_FIM, minute=0, second=0, microsecond=0)
    start = max(inicio, janela_ini)
    end = min(fim, janela_fim)
    if end <= start:
        return 0
    return int((end - start).total_seconds() // 60)


def relatorio_ocupacao(data: str) -> list[dict]:
    try:
        dia = datetime.strptime(data, "%Y-%m-%d")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="data deve ser YYYY-MM-DD.") from exc

    resultado = []
    with connect() as conn:
        salas = conn.execute("SELECT * FROM salas ORDER BY id").fetchall()
        for sala in salas:
            reservas = conn.execute(
                """
                SELECT inicio, fim FROM reservas
                WHERE sala_id = ? AND status = 'ATIVA'
                  AND date(inicio) <= ? AND date(fim) >= ?
                """,
                (sala["id"], data, data),
            ).fetchall()
            minutos = 0
            for r in reservas:
                minutos += _clip_minutos(parse_dt(r["inicio"]), parse_dt(r["fim"]), dia)
            minutos = min(minutos, MINUTOS_JANELA)
            taxa = round(minutos / MINUTOS_JANELA, 4) if MINUTOS_JANELA else 0.0
            resultado.append(
                {
                    "sala_id": sala["id"],
                    "nome": sala["nome"],
                    "minutos_ocupados": minutos,
                    "taxa_ocupacao": taxa,
                }
            )
    return resultado
