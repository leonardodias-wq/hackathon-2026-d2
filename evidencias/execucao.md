# Evidência de execução

## Agente

Cursor Agent (Composer)

## Modelo

Composer (sessão hackathon 2026-10-23)

## Prompt de entrada

> Siga integralmente prompts/INSTRUCOES-UNIVERSAIS.md deste repositório.
>
> Usando as skills disponíveis, construa o sistema descrito em pedidos/PEDIDO-TREINO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.
>
> Não pare entre etapas. Registre em evidencias/erros-ia.md qualquer erro seu antes de corrigir.

## Pedido

`pedidos/PEDIDO-TREINO.md` — Reserva de salas (cadastro, conflito, salas livres, ocupação).

## Pipeline executado

1. **Concepção:** `gerado/docs/PRD.md`
2. **Especificação:** `gerado/docs/SPEC.md`
3. **Construção:** API FastAPI + SQLite (`RESERVAS_DB`, `pysqlite3-binary`) + UI `gerado/static/` (skill `interface-agradavel`); substituiu o sistema anterior (controle de horas) em `gerado/`
4. **Revisão:** `pytest` — 10 testes de aceite verdes; smoke do servidor em `:8000`

## Artefatos

- Skills: `fabrique-sistema`, `interface-agradavel`
- Sistema: `gerado/`
- Critérios: `evidencias/criterios-aceite.md`
