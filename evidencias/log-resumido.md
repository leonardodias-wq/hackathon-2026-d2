# Log resumido

```bash
cd gerado
python3 -m venv .venv          # já existia; reutilizado
source .venv/bin/activate
pip install -r requirements.txt
python -m compileall -q app
pytest -q
# 10 passed
uvicorn app.main:app --host 127.0.0.1 --port 8000
# GET /api/salas → 6 salas seed (SP Sala A …)
# GET / → 200 · GET /static/styles.css → 200
```

## Comandos úteis

```bash
cd gerado
source .venv/bin/activate
pytest -q
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Docker (opcional)

```bash
cd gerado
docker compose up --build
```

## Notas

- Pedido: `PEDIDO-TREINO.md` (reserva de salas). Sistema anterior (horas) substituído.
- Banco de teste isolado: `RESERVAS_DB` (fixture por teste).
- `pytest.ini` limita coleta a `tests/`.
