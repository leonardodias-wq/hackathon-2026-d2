# Hackathon Ideen 2026 · Desafio 2 · Desenvolvimento agêntico

Pacote de skills que leva um agente de um pedido em linguagem natural até um sistema funcionando.

## 01 · O problema

Reservas de salas em planilha compartilhada geram conflito de horário. O desafio exige um pacote de skills repetível que produza um sistema local de reservas sem sobreposição.

## 02 · Solução

- **Pacote:** [`skills/fabrique-sistema/SKILL.md`](skills/fabrique-sistema/SKILL.md) — concepção, especificação, construção e revisão.
- **Treino:** [`pedidos/PEDIDO-TREINO.md`](pedidos/PEDIDO-TREINO.md) → sistema em [`gerado/`](gerado/) (API REST, UI, SQLite, CA-01..CA-10).
- **Bônus:** [`revisao-seguranca`](skills/revisao-seguranca/SKILL.md), [`interface-agradavel`](skills/interface-agradavel/SKILL.md).

## 03 · Como reproduzir

Clonar [github.com/leonardodias-wq/hackathon-2026-d2](https://github.com/leonardodias-wq/hackathon-2026-d2).

**Um comando por agente** — passos curtos e blocos prontos para copiar:

```bash
./scripts/usar-agente.sh                          # lista agentes e pedidos em pedidos/
./scripts/usar-agente.sh claude PEDIDO-TREINO.md
./scripts/usar-agente.sh colar PEDIDO.md
```

- **Cursor:** skill em `.cursor/skills/fabrique-sistema/`; o script imprime o prompt.
- **Sem arquivos no chat:** use `colar` (equivale a `montar-prompt.sh` + texto único).
- **Detalhes:** [`skills/PORTABILIDADE.md`](skills/PORTABILIDADE.md) · mapa [`prompts/agentes.json`](prompts/agentes.json)

Requer agente com terminal para `pytest` e `evidencias/`.

### Validar

[`gerado/README.md`](gerado/README.md) — testes, servidor e Docker.

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
- **E-004:** Typo `parse:dt` no handler de lançamentos → corrigido para `parse_dt` antes do pytest.

Detalhes em [`evidencias/erros-ia.md`](evidencias/erros-ia.md).
