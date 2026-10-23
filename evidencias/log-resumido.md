# Log resumido

```bash
cd /home/leonardo/projects/ideen/hackathon/gerado
python3 -m pip install --target ./_deps -r requirements.txt
PYTHONPATH=_deps:. python3 -m pytest -q
# 13 passed
```

## Comandos úteis

```bash
cd gerado
python3 -m pip install -r requirements.txt   # ou venv
PYTHONPATH=. python3 -m pytest -q          # após deps instaladas
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Reruns

- Ajuste `RESERVAS_DB` nos testes (fixture isolada por teste).
- Correção de `db_path()` dinâmico após falhas de isolamento (ver `evidencias/erros-ia.md` E-002).
