# Ensaio de banca (terceiro)

Simulação: avaliador clona o repo, segue apenas o README raiz e `gerado/README.md`.

## Passos executados

1. Ler `README.md` → localizar skill e prompt da banca.
2. `cd gerado && pip install -r requirements.txt` (ou `--target ./_deps` se venv indisponível).
3. `PYTHONPATH=_deps:. python3 -m pytest -q` → **13 passed**.
4. Conferir `evidencias/criterios-aceite.md` → 10/10 CA.
5. (Opcional) `uvicorn app.main:app --port 8000` → UI em `/`.
6. (Opcional) `cd gerado && docker compose up --build app` e `docker compose run --rm tests`.

## Fricções encontradas e mitigação

| Fricção | Mitigação |
|---|---|
| Python 3.14 sem `_sqlite3` no ambiente WSL | `pysqlite3-binary` em `requirements.txt` + import em `app/database.py` |
| `python3 -m venv` falhou (sem python3-venv no sistema) | Documentado `pip install --target ./_deps` no log |
| Espelho skill em `.cursor/skills/` | README explica copiar ou usar pasta do projeto |

## Resultado do ensaio

**Aprovado** para reprodução técnica: testes verdes, CA mapeados, pastas obrigatórias presentes.
