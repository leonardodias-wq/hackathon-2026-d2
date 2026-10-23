# Auditoria de segurança (bônus) — Reserva de salas

Data: 2026-10-23 · Escopo: `gerado/`

## Resumo

| Severidade | Qtd | Status |
|---|---|---|
| Crítico | 0 | — |
| Alto | 0 | — |
| Médio | 0 | mitigado (XSS UI) |
| Baixo / info | 2 | aceitos no escopo |

## Achados

1. **Sem autenticação** (info) — pedido exige “sem login”. Aceito.
2. **SQLite local** (info) — sem dados reais; path via `RESERVAS_DB`.
3. **XSS na UI** — mitigado: `static/app.js` usa `textContent` / `createElement`, sem `innerHTML` com dados da API.
4. **SQL injection** — queries parametrizadas em `database.py` / `business.py`.
5. **Validação de input** — enums de local/recursos, duração, capacidade e datas na camada de negócio + Pydantic.

## Conclusão

Adequado ao escopo local do hackathon. Não há segredos no repositório.
