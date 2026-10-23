import json
import os
from pathlib import Path

try:
    import pysqlite3 as sqlite3  # type: ignore
except ImportError:
    import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent

LOCAIS = ("SAO_PAULO", "ARARAQUARA", "COWORKING")
RECURSOS = ("TV", "VIDEOCONFERENCIA", "QUADRO")
STATUS = ("ATIVA", "CANCELADA")

SEED_SALAS = [
    ("SP Sala A", "SAO_PAULO", 8, ["TV", "VIDEOCONFERENCIA"]),
    ("SP Sala B", "SAO_PAULO", 4, ["QUADRO"]),
    ("AQ Sala A", "ARARAQUARA", 10, ["TV", "QUADRO"]),
    ("AQ Sala B", "ARARAQUARA", 6, ["VIDEOCONFERENCIA"]),
    ("CW Sala A", "COWORKING", 12, ["TV", "VIDEOCONFERENCIA", "QUADRO"]),
    ("CW Sala B", "COWORKING", 2, []),
]


def db_path() -> Path:
    env = os.environ.get("RESERVAS_DB")
    if env:
        return Path(env)
    return BASE_DIR / "reservas.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS salas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                local TEXT NOT NULL,
                capacidade INTEGER NOT NULL,
                recursos TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sala_id INTEGER NOT NULL REFERENCES salas(id),
                responsavel_nome TEXT NOT NULL,
                responsavel_email TEXT NOT NULL,
                titulo TEXT NOT NULL,
                participantes INTEGER NOT NULL,
                inicio TEXT NOT NULL,
                fim TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ATIVA'
            );
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM salas").fetchone()[0]
        if count == 0:
            for nome, local, cap, recursos in SEED_SALAS:
                conn.execute(
                    "INSERT INTO salas (nome, local, capacidade, recursos) VALUES (?, ?, ?, ?)",
                    (nome, local, cap, json.dumps(recursos)),
                )
            conn.commit()


def row_sala(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "local": row["local"],
        "capacidade": row["capacidade"],
        "recursos": json.loads(row["recursos"]),
    }


def row_reserva(row: sqlite3.Row) -> dict:
    data = {
        "id": row["id"],
        "sala_id": row["sala_id"],
        "responsavel_nome": row["responsavel_nome"],
        "responsavel_email": row["responsavel_email"],
        "titulo": row["titulo"],
        "participantes": row["participantes"],
        "inicio": row["inicio"],
        "fim": row["fim"],
        "status": row["status"],
    }
    keys = row.keys()
    if "sala_nome" in keys:
        data["sala_nome"] = row["sala_nome"]
    return data
