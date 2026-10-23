import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Isolar DB antes de importar a app
@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_reservas.db"
    monkeypatch.setenv("RESERVAS_DB", str(db_file))

    from app.database import init_db
    from app.main import app

    init_db()
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sala_id(client):
    salas = client.get("/api/salas").json()
    assert len(salas) >= 1
    return salas[0]["id"]
