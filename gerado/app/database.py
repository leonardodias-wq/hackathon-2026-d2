import os
from pathlib import Path

try:
    import pysqlite3 as sqlite3  # type: ignore
except ImportError:  # pragma: no cover
    import sqlite3

DEFAULT_DB = Path(__file__).resolve().parent.parent / "horas.db"

SEED_PROJETOS = [
    ("Portal Cliente", "Acme Corp", "#1B6B4A"),
    ("App Mobile", "Beta Indústria", "#C45C26"),
    ("Infra Interna", "Ideen", "#2C4A6E"),
]


def db_path() -> Path:
    env = os.environ.get("HORAS_DB")
    return Path(env) if env else DEFAULT_DB


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cliente TEXT NOT NULL,
            cor TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS lancamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER NOT NULL REFERENCES projetos(id),
            colaborador_nome TEXT NOT NULL,
            colaborador_email TEXT NOT NULL,
            descricao TEXT NOT NULL,
            inicio TEXT NOT NULL,
            fim TEXT,
            status TEXT NOT NULL CHECK (status IN ('FINALIZADO', 'EM_ANDAMENTO'))
        );
        """
    )
    count = conn.execute("SELECT COUNT(*) FROM projetos").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO projetos (nome, cliente, cor) VALUES (?, ?, ?)",
            SEED_PROJETOS,
        )
    conn.commit()
