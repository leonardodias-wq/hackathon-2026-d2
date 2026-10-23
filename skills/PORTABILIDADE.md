# Portabilidade · usar a fábrica em qualquer agente

O formato `SKILL.md` é nativo do **Cursor**. Para outros ambientes, use os artefatos em `prompts/` — são a **mesma lógica**, sem depender de `/skill`.

## Escolha rápida

| Ambiente | O que fazer |
|---|---|
| **Cursor** | Skill em `.cursor/skills/fabrique-sistema` → `/fabrique-sistema` + prompt em `prompts/mensagem-banca.txt` |
| **ChatGPT** | Project → colar `prompts/INSTRUCOES-UNIVERSAIS.md` nas instruções; anexar repo; enviar `prompts/mensagem-usuario-iniciar.txt` |
| **Claude** | Project knowledge: `INSTRUCOES-UNIVERSAIS.md` + `skills/fabrique-sistema/SKILL.md` + pedido; mesma mensagem inicial |
| **Gemini** | Contexto do chat / Gem com `INSTRUCOES-UNIVERSAIS.md` + repo |
| **Copilot (VS Code)** | Abrir este repo; no chat referenciar `@workspace` e `prompts/INSTRUCOES-UNIVERSAIS.md` |
| **Qualquer chat sem arquivos** | Rode `./scripts/montar-prompt.sh` e cole `prompts/PROMPT-COMPLETO.md` |

Mapa machine-readable: [`prompts/agentes.json`](../prompts/agentes.json).

## Dois pedidos (apresentação)

| Arquivo | Uso |
|---|---|
| `PEDIDO-TREINO.md` | Calibrar pacote + evidências no hackathon |
| `PEDIDO.md` | Pedido oculto da banca (finalistas) — mesma skill, mesmo fluxo |

A detecção automática está nas instruções universais e na skill `fabrique-sistema`.

## Reaproveitabilidade (critério da banca)

Outra pessoa deve conseguir:

1. Clonar o repo.
2. Seguir [`README.md`](../README.md) § Como reproduzir **ou** esta tabela.
3. Obter sistema em `gerado/` + testes + `evidencias/` equivalentes.

**Limitação honesta:** modelos só-chat (sem terminal) não executam `pytest`; o pacote ainda especifica o processo, mas a prova exige agente com execução local (Cursor, Claude Code, Codex, etc.).

## Manter sincronizado

- Regra de negócio nova → atualizar `skills/fabrique-sistema/SKILL.md` **e** `prompts/INSTRUCOES-UNIVERSAIS.md` (ou regerar PROMPT-COMPLETO).
- Bônus segurança → `skills/revisao-seguranca/SKILL.md` (opcional após etapa 04).
