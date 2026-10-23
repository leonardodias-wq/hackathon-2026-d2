# Critérios de aceite — PEDIDO-TREINO.md (reserva de salas)

Data: 2026-10-23  
Comando: `cd gerado && . .venv/bin/activate && pytest -q`  
Resultado: **10 passed**

| Código | Resultado | Observação |
|---|---|---|
| CA-01 | PASS | Reserva válida → 201, `status=ATIVA` |
| CA-02 | PASS | Sobreposição → 409 com mensagem de conflito |
| CA-03 | PASS | Encostados (fim == início seguinte) → 201 |
| CA-04 | PASS | 10 min e 4h01 → 400 por duração |
| CA-05 | PASS | Início no passado → 400 |
| CA-06 | PASS | Participantes > capacidade → 400 |
| CA-07 | PASS | Cancelar futura → `CANCELADA`; horário liberado |
| CA-08 | PASS | Cancelar passada → 400 |
| CA-09 | PASS | Salas livres com filtro local + capacidade_min |
| CA-10 | PASS | Ocupação: canceladas não entram (120 min / 600) |

**Resumo:** 10/10 PASS (`tests/test_acceptance.py`).
