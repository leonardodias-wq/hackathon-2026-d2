from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import business
from .database import BASE_DIR, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Reserva de Salas", lifespan=lifespan)

static_dir = BASE_DIR / "static"
if static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


class SalaIn(BaseModel):
    nome: str
    local: str
    capacidade: int = Field(ge=1)
    recursos: list[str] = Field(default_factory=list)


class ReservaIn(BaseModel):
    sala_id: int
    responsavel_nome: str
    responsavel_email: str
    titulo: str
    participantes: int = Field(ge=1)
    inicio: str
    fim: str


@app.get("/")
def index():
    index_path = static_dir / "index.html"
    return FileResponse(index_path)


@app.get("/api/salas")
def api_listar_salas():
    return business.listar_salas()


@app.post("/api/salas", status_code=201)
def api_criar_sala(body: SalaIn):
    return business.criar_sala(body.nome, body.local, body.capacidade, body.recursos)


@app.get("/api/salas/livres")
def api_salas_livres(
    inicio: str = Query(...),
    fim: str = Query(...),
    local: Optional[str] = None,
    capacidade_min: Optional[int] = Query(None, ge=1),
):
    return business.salas_livres(inicio, fim, local=local, capacidade_min=capacidade_min)


@app.get("/api/reservas")
def api_listar_reservas(
    data: Optional[str] = None,
    sala_id: Optional[int] = None,
):
    return business.listar_reservas(data=data, sala_id=sala_id)


@app.post("/api/reservas", status_code=201)
def api_criar_reserva(body: ReservaIn):
    return business.criar_reserva(
        body.sala_id,
        body.responsavel_nome,
        body.responsavel_email,
        body.titulo,
        body.participantes,
        body.inicio,
        body.fim,
    )


@app.post("/api/reservas/{reserva_id}/cancelar")
def api_cancelar(reserva_id: int):
    return business.cancelar_reserva(reserva_id)


@app.get("/api/relatorios/ocupacao")
def api_ocupacao(data: str = Query(...)):
    return business.relatorio_ocupacao(data)
