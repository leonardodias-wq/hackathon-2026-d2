# Reserva de Salas

Sistema local de reserva de salas (São Paulo, Araraquara, coworking) sem conflito de horário.

## Requisitos

- Python 3.11+ (testado também em 3.14 com `pysqlite3-binary`)
- Dependências em `requirements.txt`

## Instalar e testar

```bash
cd gerado
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Rodar o servidor

```bash
cd gerado
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abra http://127.0.0.1:8000 — formulário de reserva e agenda do dia.

Banco padrão: `reservas.db` (override com `RESERVAS_DB=/caminho/arquivo.db`).

## Docker (opcional)

```bash
docker compose up --build
```

## Segurança

- Sem login / sem segredos.
- SQL parametrizado.
- UI usa `textContent` / DOM API (sem `innerHTML` com dados da API).
