# Prompt completo · Fábrica Ideen (gerado automaticamente)

_Não edite manualmente; regenere com: `./scripts/montar-prompt.sh [PEDIDO.md]`_

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

---

## Pedido anexado

# Pedido de treino · Reserva de salas

> Use este pedido para construir e calibrar o seu pacote de skills. Rode o pacote nele, de ponta a ponta, e guarde as evidências.
> A banca usará um **pedido oculto** do mesmo tamanho e do mesmo tipo de entrega para desempatar os finalistas.

## O pedido, como o cliente escreveu

"A gente tem salas em São Paulo, em Araraquara e num coworking, e vive acontecendo de duas pessoas reservarem a mesma sala no mesmo horário. Hoje é tudo numa planilha compartilhada. Queria um sistema simples: cadastro das salas, reserva sem conflito, um jeito rápido de achar sala livre e saber quanto cada sala é usada. Não precisa de login por enquanto."

## O que o sistema precisa fazer

**Salas**
- Cadastro com nome, local (`SAO_PAULO`, `ARARAQUARA`, `COWORKING`), capacidade e recursos (`TV`, `VIDEOCONFERENCIA`, `QUADRO`).
- O sistema já começa com 6 salas cadastradas, duas por local.

**Reservas**
- Uma reserva tem sala, responsável (nome e e-mail), título, quantidade de participantes, início e fim.
- Duas reservas da mesma sala não podem se sobrepor. Encostar é permitido: 10h–11h e 11h–12h podem coexistir.
- Duração mínima de 15 minutos e máxima de 4 horas.
- Não é possível reservar no passado.
- Participantes não podem passar da capacidade da sala.

**Cancelamento**
- Só reservas futuras podem ser canceladas.
- A reserva cancelada fica no histórico com status `CANCELADA` e libera o horário.

**Consulta**
- Salas livres num intervalo, com filtro opcional por local e capacidade mínima.

**Relatório**
- Taxa de ocupação de cada sala num dia, considerando o horário das 8h às 18h e só reservas ativas.

**Interface**
- API REST para todas as operações.
- Uma tela web simples para reservar e ver a agenda do dia por sala.
- Dados em banco local. Sem login.

## Critérios de aceite

| Código | Cenário | Resultado esperado |
|---|---|---|
| CA-01 | Reservar sala livre dentro das regras | Reserva criada com status `ATIVA` |
| CA-02 | Reservar sala já ocupada em horário que se sobrepõe | Recusa com mensagem de conflito |
| CA-03 | Reservar 11h–12h numa sala com reserva 10h–11h | Reserva criada |
| CA-04 | Reserva com 10 minutos ou com 4h01 | Recusa por duração |
| CA-05 | Reserva com início no passado | Recusa |
| CA-06 | Participantes acima da capacidade | Recusa |
| CA-07 | Cancelar reserva futura | Status `CANCELADA` e horário liberado |
| CA-08 | Cancelar reserva que já passou | Recusa |
| CA-09 | Consultar salas livres com filtro de local e capacidade | Só salas livres que atendem aos filtros |
| CA-10 | Relatório de ocupação de um dia com reservas canceladas | Canceladas não entram no cálculo |

---

## Mensagem final do usuário

Siga integralmente o arquivo prompts/INSTRUCOES-UNIVERSAIS.md deste repositório.

Construa o sistema do pedido de treino (PEDIDO-TREINO.md) dentro de gerado/, execute as 4 etapas, rode os testes de aceite e preencha evidencias/.

Não pare entre etapas. Registre em evidencias/erros-ia.md qualquer erro seu antes de corrigir.
