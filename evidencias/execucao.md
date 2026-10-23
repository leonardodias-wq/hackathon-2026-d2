# Evidência de execução

## Agente

Cursor Agent (Composer)

## Modelo

Composer (sessão hackathon 2026-10-23)

## Prompt de entrada (treino)

> Usando as skills disponíveis, construa o sistema descrito em PEDIDO-TREINO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.

## Resumo

1. **Concepção:** `gerado/docs/PRD.md`
2. **Especificação:** `gerado/docs/SPEC.md`
3. **Construção:** API FastAPI + SQLite (`pysqlite3-binary` quando necessário) + UI em `gerado/static/index.html`
4. **Revisão:** `pytest` com 10 testes de aceite; todos passando

## Artefatos

- Pacote: `skills/fabrique-sistema/SKILL.md`
- Sistema: `gerado/`
- Critérios: `evidencias/criterios-aceite.md`
