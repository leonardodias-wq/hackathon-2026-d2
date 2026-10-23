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
    os.environ["RESERVAS_DB"] = path
    if Path(path).exists():
        Path(path).unlink()
    conn = get_connection()
    init_db(conn)
    conn.close()
    with TestClient(app) as test_client:
        yield test_client
    Path(path).unlink(missing_ok=True)
