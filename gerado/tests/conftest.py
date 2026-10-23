import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.database import get_connection, init_db
from app.main import app


@pytest.fixture
def client() -> TestClient:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["HORAS_DB"] = path
    if Path(path).exists():
        Path(path).unlink()
    conn = get_connection()
    init_db(conn)
    conn.close()
    with TestClient(app) as test_client:
        yield test_client
    Path(path).unlink(missing_ok=True)


@pytest.fixture
def projeto_id(client: TestClient) -> int:
    projetos = client.get("/api/projetos").json()
    assert len(projetos) >= 1
    return projetos[0]["id"]
