# Portabilidade · usar a fábrica em qualquer agente

O formato `SKILL.md` é nativo do **Cursor**. Nos outros ambientes, a mesma lógica está em `prompts/`.

## Entrada rápida

Pedidos ficam em [`pedidos/`](../pedidos/). Na raiz do repositório:

```bash
./scripts/usar-agente.sh                          # lista agentes + arquivos em pedidos/
./scripts/usar-agente.sh chatgpt PEDIDO-TREINO.md # passos + blocos ──── COPIAR ────
./scripts/usar-agente.sh colar PEDIDO.md            # um único bloco (chat com terminal)
```

| Ambiente | Exemplo |
|---|---|
| Cursor | `./scripts/usar-agente.sh cursor PEDIDO-TREINO.md` |
| ChatGPT | `./scripts/usar-agente.sh chatgpt PEDIDO-TREINO.md` |
| Claude | `./scripts/usar-agente.sh claude PEDIDO-TREINO.md` |
| Gemini | `./scripts/usar-agente.sh gemini PEDIDO-TREINO.md` |
| Copilot | `./scripts/usar-agente.sh copilot PEDIDO-TREINO.md` |
| Colar tudo | `./scripts/usar-agente.sh colar PEDIDO-TREINO.md` |

Mapa machine-readable: [`prompts/agentes.json`](../prompts/agentes.json).  
Só o prompt grande: `./scripts/montar-prompt.sh PEDIDO-TREINO.md` → `prompts/PROMPT-COMPLETO.md`.

## Reaproveitabilidade (critério da banca)

1. Clonar o repo.
2. `./scripts/usar-agente.sh <agente> PEDIDO-TREINO.md` ou seguir [`README.md`](../README.md) §03.
3. Obter sistema em `gerado/` + testes + `evidencias/`.

**Limitação honesta:** modelos só-chat (sem terminal) não executam `pytest`; a prova exige agente com execução local.

## Manter sincronizado

- Regra nova → `skills/fabrique-sistema/SKILL.md` **e** `prompts/INSTRUCOES-UNIVERSAIS.md` (ou regerar PROMPT-COMPLETO).
- Novo pedido → adicionar `pedidos/<nome>.md` e rodar o script com esse nome.
