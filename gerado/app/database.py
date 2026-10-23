import json
from pathlib import Path

try:
    from pysqlite3 import dbapi2 as sqlite3
except ImportError:
    import sqlite3  # type: ignore

import os

_default = Path(__file__).resolve().parent.parent / "reservas.db"


def db_path() -> Path:
    return Path(os.environ.get("RESERVAS_DB", str(_default)))

LOCALS = ("SAO_PAULO", "ARARAQUARA", "COWORKING")
RECURSOS = ("TV", "VIDEOCONFERENCIA", "QUADRO")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS salas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            local TEXT NOT NULL,
            capacidade INTEGER NOT NULL,
            recursos TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sala_id INTEGER NOT NULL,
            responsavel_nome TEXT NOT NULL,
            responsavel_email TEXT NOT NULL,
            titulo TEXT NOT NULL,
            participantes INTEGER NOT NULL,
            inicio TEXT NOT NULL,
            fim TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (sala_id) REFERENCES salas(id)
        );
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM salas").fetchone()[0]
    if count == 0:
        seed_salas(conn)
    conn.commit()


def seed_salas(conn: sqlite3.Connection) -> None:
    salas = []
    for local in LOCALS:
        for i in (1, 2):
            salas.append(
                (
                    f"Sala {local} {i}",
                    local,
                    10 if i == 1 else 6,
                    json.dumps(["TV", "QUADRO"]),
                )
            )
    conn.executemany(
        "INSERT INTO salas (nome, local, capacidade, recursos) VALUES (?, ?, ?, ?)",
        salas,
    )
