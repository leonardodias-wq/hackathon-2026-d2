# Log resumido

```bash
cd gerado
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
# 10 passed
uvicorn app.main:app --host 127.0.0.1 --port 8000
# GET /api/projetos → 3 projetos seed
```

## Comandos úteis

```bash
cd gerado
source .venv/bin/activate   # ou: ./run-tests.sh
pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Docker (opcional)

```bash
cd gerado
docker compose up --build app
docker compose run --rm tests
docker compose down
```

## Notas

- Banco de teste isolado: `HORAS_DB` (fixture por teste).
- `pytest.ini` limita coleta a `tests/` (evita `_deps`).
