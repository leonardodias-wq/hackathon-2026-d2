import json
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.business import (
    occupancy_minutes,
    overlaps,
    parse_dt,
    row_to_reserva,
    row_to_sala,
    validate_reservation,
)
from app.database import LOCALS, get_connection, init_db

app = FastAPI(title="Reserva de Salas")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


class SalaCreate(BaseModel):
    nome: str
    local: str
    capacidade: int = Field(gt=0)
    recursos: list[str] = []


class ReservaCreate(BaseModel):
    sala_id: int
    responsavel_nome: str
    responsavel_email: str
    titulo: str
    participantes: int = Field(gt=0)
    inicio: str
    fim: str


@app.on_event("startup")
def startup() -> None:
    conn = get_connection()
    init_db(conn)
    conn.close()


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/salas")
def list_salas():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM salas ORDER BY id").fetchall()
    conn.close()
    return [row_to_sala(r) for r in rows]


@app.post("/api/salas", status_code=201)
def create_sala(body: SalaCreate):
    if body.local not in LOCALS:
        raise HTTPException(400, "Local inválido")
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO salas (nome, local, capacidade, recursos) VALUES (?, ?, ?, ?)",
        (body.nome, body.local, body.capacidade, json.dumps(body.recursos)),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM salas WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_sala(row)


@app.get("/api/reservas")
def list_reservas(data: str | None = None):
    conn = get_connection()
    if data:
        rows = conn.execute(
            """
            SELECT * FROM reservas
            WHERE date(inicio) <= date(?) AND date(fim) >= date(?)
            ORDER BY inicio
            """,
            (data, data),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM reservas ORDER BY inicio").fetchall()
    conn.close()
    return [row_to_reserva(r) for r in rows]


@app.post("/api/reservas", status_code=201)
def create_reserva(body: ReservaCreate):
    now = datetime.utcnow()
    inicio = parse_dt(body.inicio)
    fim = parse_dt(body.fim)
    conn = get_connection()
    sala = conn.execute("SELECT * FROM salas WHERE id = ?", (body.sala_id,)).fetchone()
    if not sala:
        conn.close()
        raise HTTPException(404, "Sala não encontrada")

    err = validate_reservation(sala["capacidade"], body.participantes, inicio, fim, now)
    if err:
        conn.close()
        raise HTTPException(400, err)

    ativas = conn.execute(
        "SELECT * FROM reservas WHERE sala_id = ? AND status = 'ATIVA'",
        (body.sala_id,),
    ).fetchall()
    for r in ativas:
        if overlaps(inicio, fim, parse_dt(r["inicio"]), parse_dt(r["fim"])):
            conn.close()
            raise HTTPException(409, "Conflito de horário: sala já ocupada neste intervalo")

    cur = conn.execute(
        """
        INSERT INTO reservas
        (sala_id, responsavel_nome, responsavel_email, titulo, participantes, inicio, fim, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'ATIVA')
        """,
        (
            body.sala_id,
            body.responsavel_nome,
            body.responsavel_email,
            body.titulo,
            body.participantes,
            inicio.isoformat(),
            fim.isoformat(),
        ),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM reservas WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return row_to_reserva(row)


@app.post("/api/reservas/{reserva_id}/cancelar")
def cancelar_reserva(reserva_id: int):
    now = datetime.utcnow()
    conn = get_connection()
    row = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Reserva não encontrada")
    fim = parse_dt(row["fim"])
    if fim <= now:
        conn.close()
        raise HTTPException(400, "Não é possível cancelar reserva que já passou")
    if row["status"] == "CANCELADA":
        conn.close()
        return row_to_reserva(row)
    conn.execute("UPDATE reservas SET status = 'CANCELADA' WHERE id = ?", (reserva_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM reservas WHERE id = ?", (reserva_id,)).fetchone()
    conn.close()
    return row_to_reserva(row)


@app.get("/api/salas/livres")
def salas_livres(
    inicio: str = Query(...),
    fim: str = Query(...),
    local: str | None = None,
    capacidade_min: int | None = None,
):
    ini = parse_dt(inicio)
    end = parse_dt(fim)
    conn = get_connection()
    salas = conn.execute("SELECT * FROM salas").fetchall()
    livres = []
    for sala in salas:
        if local and sala["local"] != local:
            continue
        if capacidade_min and sala["capacidade"] < capacidade_min:
            continue
        ativas = conn.execute(
            "SELECT * FROM reservas WHERE sala_id = ? AND status = 'ATIVA'",
            (sala["id"],),
        ).fetchall()
        ocupada = any(overlaps(ini, end, parse_dt(r["inicio"]), parse_dt(r["fim"])) for r in ativas)
        if not ocupada:
            livres.append(row_to_sala(sala))
    conn.close()
    return livres


@app.get("/api/relatorios/ocupacao")
def relatorio_ocupacao(data: str = Query(..., description="YYYY-MM-DD")):
    day = datetime.fromisoformat(data)
    conn = get_connection()
    salas = conn.execute("SELECT * FROM salas").fetchall()
    window_minutes = (18 - 8) * 60
    result = []
    for sala in salas:
        reservas = conn.execute(
            """
            SELECT * FROM reservas
            WHERE sala_id = ? AND status = 'ATIVA'
              AND date(inicio) <= date(?) AND date(fim) >= date(?)
            """,
            (sala["id"], data, data),
        ).fetchall()
        used = sum(
            occupancy_minutes(parse_dt(r["inicio"]), parse_dt(r["fim"]), day) for r in reservas
        )
        taxa = used / window_minutes if window_minutes else 0.0
        result.append(
            {
                "sala_id": sala["id"],
                "nome": sala["nome"],
                "data": data,
                "minutos_ocupados": round(used, 2),
                "minutos_janela": window_minutes,
                "taxa_ocupacao": round(taxa, 4),
            }
        )
    conn.close()
    return result
