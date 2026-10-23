# Checklist formal — apresentação × repositório

Conformidade com o kit do desafio (prazo de entrega: segunda 09h).

## Escopo obrigatório (passa / não passa)

| # | Exigência (apresentação + kit) | Evidência no repo |
|---|---|---|
| O1 | Pacote em `skills/` com `SKILL.md` | `skills/fabrique-sistema/SKILL.md` |
| O2 | Quatro etapas: concepção, especificação, construção, revisão | PRD/SPEC em `gerado/docs/` + skill |
| O3 | Sistema gerado a partir do pedido de treino | `gerado/` |
| O4 | `evidencias/` com agente, modelo, prompt, log | `evidencias/execucao.md`, `log-resumido.md` |
| O5 | README com 5 blocos (problema, solução, reproduzir, evidências, erros IA) | `README.md` |
| O6 | Execução completa no treino com critérios verificados | `evidencias/criterios-aceite.md` |
| O7 | Prompt da banca funciona sem intervenção | README + skill |

## Proibidos

| # | Regra | Verificação |
|---|---|---|
| P1 | Sem dados reais de cliente/colaborador | Revisão manual |
| P2 | Sem segredos/tokens reais | [`varredura-segredos-git.md`](varredura-segredos-git.md) + `.gitignore` |
| P3 | Deploy não obrigatório | N/A |

## Bônus (opcional)

| # | Item |
|---|---|
| B1 | Testes e scans do sistema gerado |
| B2 | Pacote em dois agentes |
| B3 | Skill dedicada à revisão de segurança |

## Avaliação da banca → ação operacional

| Critério | Peso | O que a banca precisa ver |
|---|---|---|
| Entregou o mínimo | 35% | Pacote + 1 execução completa documentada no treino |
| Respeitou o desafio | 30% | 4 etapas + sistema sem ajuste manual relevante |
| Reaproveitável | 20% | Terceiro segue README e chega ao mesmo resultado |
| README | 15% | Claro + honesto sobre erros da IA |

## Matriz slide → ação

| Slide / tema | Ação no repositório |
|---|---|
| Fábrica de skills | `skills/fabrique-sistema/` |
| 4 etapas | `gerado/docs/PRD.md`, `SPEC.md`, código, revisão/testes |
| Pedido treino | `pedidos/PEDIDO-TREINO.md` → sistema em `gerado/` |
| Outro pedido | `pedidos/PEDIDO.md` (ou novo arquivo em `pedidos/`) |
| Evidências | `evidencias/*` |
| Onde a IA errou | `evidencias/erros-ia.md` + README §05 |
| Prazo segunda 9h | Entrega em [leonardodias-wq/hackathon-2026-d2](https://github.com/leonardodias-wq/hackathon-2026-d2) |
