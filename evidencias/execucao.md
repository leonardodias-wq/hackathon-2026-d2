# Evidência de execução

## Agente

Cursor Agent (Composer)

## Modelo

Composer (sessão hackathon 2026-10-23)

## Prompt de entrada

> Usando as skills disponíveis, construa o sistema descrito em pedidos/PEDIDO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.

## Pedido

`pedidos/PEDIDO.md` — Controle de horas (projetos, lançamentos, cronômetro, relatório CSV).

## Pipeline executado

1. **Concepção:** `gerado/docs/PRD.md`
2. **Especificação:** `gerado/docs/SPEC.md`
3. **Construção:** API FastAPI + SQLite (`HORAS_DB`, `pysqlite3-binary`) + UI `gerado/static/` (skill `interface-agradavel`)
4. **Revisão:** `pytest` — 10 testes de aceite verdes; smoke do servidor em `:8000`

## Artefatos

- Skills: `fabrique-sistema`, `interface-agradavel`
- Sistema: `gerado/`
- Critérios: `evidencias/criterios-aceite.md`
