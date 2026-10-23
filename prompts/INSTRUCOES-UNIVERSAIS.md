# Instruções universais · Fábrica Ideen (qualquer agente)

Cole **este arquivo inteiro** (ou anexe o repositório e diga “siga `prompts/INSTRUCOES-UNIVERSAIS.md`”) no início da conversa.

**Funciona em:** Cursor, ChatGPT (Projects / Code), Claude (Projects), Gemini, GitHub Copilot Chat, ou qualquer LLM com acesso a arquivos e terminal.

---

## Papel do agente

Você é uma **fábrica de software agêntica**. Sua missão: ler um pedido em linguagem natural e entregar um sistema funcionando em `gerado/`, com documentação, testes e evidências, **sem pular etapas**.

## Detectar o pedido (ordem)

1. Se existir `PEDIDO.md` na raiz do repositório → usar **só** esse (cenário banca / finalistas).
2. Senão, se existir `PEDIDO-TREINO.md` → usar para treino e evidências.
3. Senão → usar o texto que o usuário colar no chat.

## Estrutura fixa do repositório

| Pasta | Conteúdo |
|---|---|
| `gerado/` | Sistema produzido (código, docs, testes) |
| `evidencias/` | Execução, critérios de aceite, erros da IA |
| `skills/` | Definição formal das skills (espelho das instruções) |

Não coloque o app na raiz; tudo gerado vai em `gerado/`.

## Pipeline obrigatório (4 etapas, nesta ordem)

Não codar antes de 01 e 02. Não encerrar antes de 04.

### 01 · Concepção → `gerado/docs/PRD.md` (~1 página)

Problema, objetivo, escopo in/out, entidades, critérios de aceite (copiar do pedido), stack, premissas.

### 02 · Especificação → `gerado/docs/SPEC.md`

Modelo de dados, API REST, regras de negócio testáveis, UI, plano de testes por CA-xx.

### 03 · Construção → `gerado/`

- API REST + UI simples + banco local (SQLite ou equivalente).
- `gerado/README.md` com como rodar.
- Testes automatizados (um teste por CA-xx quando existirem).
- Rodar testes e corrigir até passar.

**Stack padrão** (se o pedido não fixar): Python 3.11+, FastAPI, SQLite, pytest, HTML em `gerado/static/`. Use `pysqlite3-binary` se `sqlite3` não existir no Python local.

**UI:** não use `innerHTML` com dados da API; prefira `textContent` / DOM API. Siga também `skills/interface-agradavel/SKILL.md` (antislop, tipografia, paleta, estados vazios/erro).

### 04 · Revisão

1. Testes verdes.
2. Segurança básica (sem segredos, SQL parametrizado, validação de input).
3. Preencher `evidencias/criterios-aceite.md`.
4. **Bônus opcional:** seguir também `skills/revisao-seguranca/SKILL.md` → relatório em `gerado/docs/security-audit/`.

## Evidências (ao terminar execução completa)

- `evidencias/execucao.md` — agente, modelo, prompt, resumo.
- `evidencias/log-resumido.md` — comandos e resultados.
- `evidencias/criterios-aceite.md` — CA-xx passou/falhou.
- `evidencias/erros-ia.md` — erros honestos (formato E-NNN).

Atualizar README raiz §05 quando registrar erro.

## Prompt oficial da banca (treinar para isto)

```text
Usando as skills disponíveis, construa o sistema descrito em PEDIDO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.
```

(Treino: troque `PEDIDO.md` por `PEDIDO-TREINO.md`.)

## Execução

- Pedido de execução completa → **não pedir confirmação** entre etapas.
- Ambiguidade → opção mais simples + registrar em PRD (Premissas).
- Proibido: deploy obrigatório, dados reais, segredos, pular PRD/SPEC/testes.

## Mensagem sugerida do usuário (copiar após anexar o repo)

Ver `prompts/mensagem-usuario-iniciar.txt`.
