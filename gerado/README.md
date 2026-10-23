# Ponto Fiel · Controle de horas

Sistema local: projetos, lançamentos manuais, cronômetro, relatório e CSV.

## Requisitos

- Python 3.11+ (ou 3.12+)
- Dependências em `requirements.txt` (inclui `pysqlite3-binary` se o Python local não tiver `_sqlite3`)

## Instalar e testar

```bash
cd gerado
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Os testes usam banco isolado via variável `HORAS_DB` (fixture por teste).

## Rodar a API + UI

```bash
cd gerado
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abra http://127.0.0.1:8000/

## Docker (opcional)

```bash
docker compose up --build app
docker compose run --rm tests
```

## Segurança básica

- Sem login / sem segredos reais
- Validação de entrada na API
- SQL parametrizado
- UI sem `innerHTML` com dados da API (`textContent` / DOM API)
