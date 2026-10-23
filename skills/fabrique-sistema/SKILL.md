---
name: fabrique-sistema
description: >-
  Fábrica agêntica de software em 4 etapas (concepção, especificação, construção,
  revisão). Use quando o usuário pedir para construir um sistema a partir de um
  pedido em linguagem natural, PEDIDO.md, PEDIDO-TREINO.md, ou com o prompt da
  banca: skills disponíveis → sistema em gerado/ com critérios de aceite.
---

# Fabrique sistema

Leva um pedido em linguagem natural até um sistema funcionando em `gerado/`, com o mínimo de ajuste manual.

## Entrada

1. **Detectar pedido:** se existir `PEDIDO.md` na raiz, usar só ele; senão `PEDIDO-TREINO.md`; senão texto colado pelo usuário.
2. **Destino:** todo código e docs do sistema em `gerado/` (não na raiz do hackathon).
3. **Execução completa:** quando o prompt pedir construir o sistema, executar as 4 etapas em sequência **sem pedir confirmação** entre etapas.
4. **Ambiguidade:** escolher a opção mais simples; registrar premissa em `gerado/docs/PRD.md` (seção Premissas).
5. **Stack padrão** (se o pedido não fixar): Python 3.11+, FastAPI, SQLite, pytest, HTML estático servido pelo FastAPI.

## Pipeline obrigatório (nessa ordem)

Não pular etapas. Não começar a codar antes de concluir 01 e 02. Não entregar antes de 04.

### 01 · Concepção

Criar `gerado/docs/PRD.md` (máx. ~1 página) com:

- Problema (1 frase)
- Objetivo
- Escopo (in / out)
- Entidades principais
- Critérios de aceite (copiar/numerar os do pedido, se existirem)
- Stack escolhida (simples, local, sem nuvem obrigatória)

### 02 · Especificação

Criar `gerado/docs/SPEC.md` com:

- Modelo de dados (campos, enums, invariantes)
- Endpoints da API REST (método, path, body, erros)
- Regras de negócio testáveis (ex.: conflito de horário, duração min/máx)
- Telas/fluxos da UI web simples
- Plano de verificação dos critérios de aceite

### 03 · Construção

Implementar em `gerado/`:

- API REST + UI web simples + banco local (SQLite ou equivalente)
- Seed/dados iniciais pedidos no enunciado
- README curto em `gerado/README.md` (como instalar e rodar)
- Testes automatizados cobrindo os critérios de aceite (um teste por CA-xx quando existirem)
- Fazer o sistema **rodar** localmente e executar os testes

Stack padrão: Python 3.11+, FastAPI, SQLite, pytest, UI HTML simples em `gerado/static/`. Incluir `pysqlite3-binary` se o Python local não tiver `_sqlite3`. Testes com banco isolado (`RESERVAS_DB` por sessão de teste). Comando: `cd gerado && pip install -r requirements.txt && pytest -q`.

**Regras de negócio comuns (reserva de salas):** sobreposição = `inicio_a < fim_b AND inicio_b < fim_a`; encostar (`fim_a == inicio_b`) não é sobreposição; duração mín 15 min, máx 4 h; status `ATIVA` | `CANCELADA`.

### 04 · Revisão

Antes de considerar pronto:

1. Rodar testes; corrigir falhas.
2. Revisar qualidade: nomes, estrutura, README de `gerado/`.
3. Revisar segurança básica: sem segredos, sem dados reais, validação de input, SQL injection, path traversal.
   - **Bônus (opcional):** invocar skill `revisao-seguranca` e salvar relatório em `gerado/docs/security-audit/` (não altera testes CA).
4. Conferir cada critério de aceite do pedido; anotar resultado em `evidencias/criterios-aceite.md`.
5. Se algo falhar, corrigir o código (ainda na etapa 04) e revalidar.

## Evidências (sempre)

Ao final de uma execução completa, garantir/atualizar:

| Arquivo | Conteúdo |
|---|---|
| `evidencias/execucao.md` | agente, modelo, prompt de entrada, resumo do que foi feito |
| `evidencias/log-resumido.md` | log curto da execução (comandos, testes, resultado) |
| `evidencias/criterios-aceite.md` | tabela CA-xx → passou/falhou + observação |
| `evidencias/erros-ia.md` | erros da IA nesta execução (ver regra do projeto) |

## Erros da IA

Sempre que identificar um erro próprio (requisito errado, bug, teste falho por implementação incorreta, alucinação), **antes de só corrigir**:

1. Registrar em `evidencias/erros-ia.md` (formato da regra do projeto).
2. Atualizar a seção **05 · Onde a IA errou** do `README.md` na raiz.
3. Preferir corrigir o processo (esta skill / prompts internos) quando o erro for recorrente; ajuste manual no código gerado deve ser mínimo e citado em `evidencias/`.

## Prompt da banca (alvo)

Treinar para funcionar sem intervenção com:

> Usando as skills disponíveis, construa o sistema descrito em PEDIDO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.

Resposta esperada do agente: executar as 4 etapas, deixar o sistema rodável em `gerado/`, testes verdes (ou falhas documentadas), evidências preenchidas.

## O que não fazer

- Deploy em nuvem, login real, dados de cliente/colaborador
- Segredos, tokens ou senhas reais
- Pedir confirmação a cada etapa quando o prompt pedir execução completa
- Entregar só código sem PRD/SPEC/testes/evidências
