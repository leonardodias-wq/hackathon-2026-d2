# Erros da IA

Log append-only. A regra do projeto (`.cursor/rules/erros-ia.mdc`) manda registrar aqui assim que um erro for identificado.

---

### E-001 · 2026-10-23 16:15
- **Etapa:** construção
- **Sintoma:** `pytest` falhou com `ModuleNotFoundError: No module named '_sqlite3'` no Python 3.14 do ambiente.
- **Causa:** build do Python sem extensão sqlite; import padrão `sqlite3` quebra antes de usar alternativa.
- **Correção:** `pysqlite3-binary` em `requirements.txt` e import prioritário em `gerado/app/database.py`.
- **Melhoria no processo:** skill atualizada com stack padrão e nota de SQLite; `gerado/README.md` documenta dependência.

### E-002 · 2026-10-23 16:20
- **Etapa:** construção
- **Sintoma:** testes passavam isolados e falhavam em conjunto (`no such table: salas`, conflitos 409).
- **Causa:** `DB_PATH` fixo no import ignorava `RESERVAS_DB` da fixture; `startup` do FastAPI não inicializava DB nos testes.
- **Correção:** `db_path()` lido a cada conexão; `conftest.py` chama `init_db` e usa `TestClient` com DB temporário por teste.
- **Melhoria no processo:** skill atualizada com `pysqlite3-binary` e testes com `RESERVAS_DB` isolado.

### E-003 · 2026-10-23 17:45
- **Etapa:** construção / revisão
- **Sintoma:** auditoria apontou XSS médio: agenda usava `innerHTML` com `titulo` da API.
- **Causa:** UI mínima gerada sem considerar escape de HTML em dados do usuário.
- **Correção:** `gerado/static/index.html` reescrito com `createElement` + `textContent`; README de segurança em `gerado/README.md`.
- **Melhoria no processo:** skill `revisao-seguranca` já cobre categoria 5; fabrique-sistema poderia citar “sem innerHTML em dados da API”.
