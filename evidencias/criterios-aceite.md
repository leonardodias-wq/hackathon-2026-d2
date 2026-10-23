# Critérios de aceite — execução treino

Data: 2026-10-23  
Comando: `cd gerado && pip install -r requirements.txt && PYTHONPATH=_deps:. python3 -m pytest -q` (ou venv conforme `gerado/README.md`)

| Código | Resultado | Prova |
|---|---|---|
| CA-01 | PASS | `tests/test_acceptance.py::test_ca01_reserva_valida` |
| CA-02 | PASS | `test_ca02_conflito_sobreposicao` |
| CA-03 | PASS | `test_ca03_horarios_encostados` |
| CA-04 | PASS | `test_ca04_duracao_invalida` |
| CA-05 | PASS | `test_ca05_inicio_passado` |
| CA-06 | PASS | `test_ca06_capacidade` |
| CA-07 | PASS | `test_ca07_cancelar_futura` |
| CA-08 | PASS | `test_ca08_cancelar_passada` |
| CA-09 | PASS | `test_ca09_salas_livres_filtro` |
| CA-10 | PASS | `test_ca10_relatorio_ocupacao` |

**Resumo:** 10/10 PASS (`pytest` verde na suíte `tests/test_acceptance.py`).
