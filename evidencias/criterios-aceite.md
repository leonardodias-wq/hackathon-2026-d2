# Critérios de aceite — PEDIDO.md (controle de horas)

Data: 2026-10-23  
Comando: `cd gerado && . .venv/bin/activate && pytest -q`  
Resultado: **10 passed**

| Código | Resultado | Observação |
|---|---|---|
| CA-01 | PASS | Lançamento 1h → `FINALIZADO`, `duracao_minutos=60` |
| CA-02 | PASS | Fim ≤ início → 4xx |
| CA-03 | PASS | Sobreposição → 409 com mensagem de conflito |
| CA-04 | PASS | Encostados 10h–11h / 11h–12h → ambos 201 |
| CA-05 | PASS | Cronômetro → `EM_ANDAMENTO` |
| CA-06 | PASS | Segundo cronômetro mesmo e-mail → 409 |
| CA-07 | PASS | Parar → `FINALIZADO` com fim (início backdatado no teste) |
| CA-08 | PASS | Relatório soma só `FINALIZADO` |
| CA-09 | PASS | CSV com colunas exigidas; sem `EM_ANDAMENTO` |
| CA-10 | PASS | DELETE `EM_ANDAMENTO` → novo iniciar OK |

**Resumo:** 10/10 PASS (`tests/test_acceptance.py`).
