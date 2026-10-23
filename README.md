# Hackathon Ideen 2026 · Desafio 2 · Desenvolvimento agêntico

Pacote de skills que leva um agente de um pedido em linguagem natural até um sistema funcionando.

## 01 · O problema

Dupla reserva de salas em planilha compartilhada — precisamos de um fluxo repetível (skills) que gere um sistema simples de reservas sem conflito.

## 02 · O que você fez

- **Pacote:** [`skills/fabrique-sistema/SKILL.md`](skills/fabrique-sistema/SKILL.md) — orquestra concepção, especificação, construção e revisão.
- **Espelho Cursor:** [`.cursor/skills/fabrique-sistema/`](.cursor/skills/fabrique-sistema/) (mesmo conteúdo).
- **Regra de erros:** [`.cursor/rules/erros-ia.mdc`](.cursor/rules/erros-ia.mdc) — registra falhas da IA em tempo real.
- **Treino:** sistema gerado em [`gerado/`](gerado/) a partir de [`PEDIDO-TREINO.md`](PEDIDO-TREINO.md) (API REST + UI + SQLite).
- **Checklist apresentação:** [`evidencias/checklist-apresentacao.md`](evidencias/checklist-apresentacao.md).
- **Entrega base confirmada:** [`evidencias/entrega-base-confirmada.md`](evidencias/entrega-base-confirmada.md) (testes verdes antes do bônus).
- **Bônus · segurança:** skill [`skills/revisao-seguranca/`](skills/revisao-seguranca/) + [`evidencias/auditoria-seguranca-resumo.md`](evidencias/auditoria-seguranca-resumo.md).

## 03 · Como reproduzir

### 1. Clonar e abrir no Cursor

Repositório alvo: `ideen-tech/hackathon-2026-d2-[seu-usuário]`.

### 2. Instalar a skill (Cursor) ou instruções universais (outros)

- **Cursor:** skill em `.cursor/skills/fabrique-sistema/` (ou copie `skills/fabrique-sistema` para `.cursor/skills/`).
- **ChatGPT / Claude / Gemini / Copilot / chat genérico:** [`skills/PORTABILIDADE.md`](skills/PORTABILIDADE.md) e [`prompts/INSTRUCOES-UNIVERSAIS.md`](prompts/INSTRUCOES-UNIVERSAIS.md).  
  Um único bloco para colar: gere com `./scripts/montar-prompt.sh` → [`prompts/PROMPT-COMPLETO.md`](prompts/PROMPT-COMPLETO.md).

### 3. Rodar a fábrica (prompt da banca)

```text
Usando as skills disponíveis, construa o sistema descrito em PEDIDO-TREINO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.
```

(Para desempate de finalistas, troque por `PEDIDO.md`.)

### 4. Validar o sistema gerado

```bash
cd gerado
python3 -m pip install -r requirements.txt
# Se venv não estiver disponível: python3 -m pip install --target ./_deps -r requirements.txt
PYTHONPATH=. python3 -m pytest -q
# ou: PYTHONPATH=_deps:. python3 -m pytest -q
```

Servidor local:

```bash
cd gerado
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Detalhes: [`gerado/README.md`](gerado/README.md).

## 04 · Evidências

| Item | Arquivo |
|---|---|
| Checklist apresentação | [`evidencias/checklist-apresentacao.md`](evidencias/checklist-apresentacao.md) |
| Contrato CA (Given/When/Then) | [`evidencias/contrato-ca.md`](evidencias/contrato-ca.md) |
| Agente, modelo, prompt | [`evidencias/execucao.md`](evidencias/execucao.md) |
| Log de comandos | [`evidencias/log-resumido.md`](evidencias/log-resumido.md) |
| CA-01..CA-10 | [`evidencias/criterios-aceite.md`](evidencias/criterios-aceite.md) |
| Ensaio de banca | [`evidencias/ensaio-banca.md`](evidencias/ensaio-banca.md) |
| Erros (detalhe) | [`evidencias/erros-ia.md`](evidencias/erros-ia.md) |

## 05 · Onde a IA errou

- **E-001:** Python sem `_sqlite3` quebrou testes → `pysqlite3-binary` + import em `database.py`.
- **E-002:** DB de teste não isolado / path cacheado → `db_path()` dinâmico + `conftest` com `init_db`.
- **E-003:** XSS na agenda (`innerHTML`) → DOM API + `textContent` após auditoria.

Detalhes em [`evidencias/erros-ia.md`](evidencias/erros-ia.md).
