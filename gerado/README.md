# Sistema gerado · Reserva de salas

API REST + UI simples para reserva de salas (pedido de treino).

## Pré-requisitos

- Python 3.11+

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
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Abra http://127.0.0.1:8000/ para a interface web.

## API

- `GET /api/salas`
- `POST /api/reservas`
- `POST /api/reservas/{id}/cancelar`
- `GET /api/salas/livres?inicio=&fim=&local=&capacidade_min=`
- `GET /api/relatorios/ocupacao?data=YYYY-MM-DD`

Banco SQLite: `gerado/reservas.db` (variável `RESERVAS_DB` para sobrescrever).

## Segurança (escopo do PRD)

- **Sem login:** qualquer cliente na rede pode ler/criar/cancelar reservas se conhecer a URL e o `id` (limitação conhecida; ver auditoria em `docs/security-audit/`).
- **UI:** agenda renderizada com `textContent` / DOM API (sem `innerHTML` em dados da API) — mitiga XSS em títulos de reserva.
- **Produção:** exigir autenticação, autorização por responsável e rate limiting antes de expor publicamente.
