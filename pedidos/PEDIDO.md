# Pedido de teste · Controle de horas

> **Uso:** testar o pacote de skills de ponta a ponta com um pedido **diferente** do treino (`PEDIDO-TREINO.md`).
> Mesmo tipo de entrega: API REST, UI web simples, banco local, sem login, critérios de aceite verificáveis.
>
> Prompt sugerido:
>
> ```text
> Usando as skills disponíveis, construa o sistema descrito em pedidos/PEDIDO.md dentro da pasta gerado/. Siga todas as etapas das skills até o sistema rodar e os critérios de aceite serem verificados.
> ```

## O pedido, como o cliente escreveu

"A equipe registra horas em planilha e ninguém confia no total do fim do mês. Queria um sistema simples: cadastro de projetos, lançamento de horas com início e fim, um cronômetro para marcar o que estou fazendo agora, e um relatório que eu possa exportar em CSV por período e por projeto. Não precisa de login por enquanto — cada lançamento tem o nome e o e-mail de quem trabalhou."

## O que o sistema precisa fazer

**Projetos**
- Cadastro com nome, cliente (texto) e cor em hex (`#RRGGBB`) para exibir na UI.
- O sistema já começa com 3 projetos cadastrados.

**Lançamentos de hora**
- Um lançamento tem: projeto, colaborador (nome e e-mail), descrição da atividade, início, fim, status (`FINALIZADO` ou `EM_ANDAMENTO`).
- Duração mínima de 1 minuto quando finalizado; fim deve ser depois do início.
- Não é possível criar lançamento com início no futuro.
- Um colaborador (mesmo e-mail) não pode ter dois lançamentos `EM_ANDAMENTO` ao mesmo tempo.
- Dois lançamentos `FINALIZADO` do mesmo colaborador não podem se sobrepor no tempo. Encostar é permitido (10h–11h e 11h–12h).

**Cronômetro**
- Iniciar cronômetro: cria lançamento `EM_ANDAMENTO` com início = agora e fim vazio/null até parar.
- Parar cronômetro: define fim = agora, status `FINALIZADO`, valida duração mínima.

**Edição e exclusão**
- Só lançamentos `EM_ANDAMENTO` podem ser excluídos (remove o registro).
- Lançamentos `FINALIZADO` podem ser editados (descrição, projeto, início, fim) respeitando as mesmas regras de sobreposição.

**Consulta**
- Listar lançamentos de um colaborador (e-mail) em um intervalo de datas.
- Total de horas por projeto em um intervalo (somando só `FINALIZADO`).

**Relatório e exportação**
- Relatório por período (`data_inicio`, `data_fim`) com totais por projeto e por colaborador.
- Exportar CSV do período com colunas: `projeto`, `cliente`, `colaborador`, `email`, `descricao`, `inicio`, `fim`, `duracao_minutos`, `status`.
- Lançamentos `EM_ANDAMENTO` não entram no CSV nem nos totais do relatório.

**Interface**
- API REST para todas as operações.
- Tela web: escolher projeto, iniciar/parar cronômetro, formulário de lançamento manual, lista do dia e botão para exportar CSV do mês corrente.
- Dados em banco local. Sem login.

## Critérios de aceite

| Código | Cenário | Resultado esperado |
|---|---|---|
| CA-01 | Criar lançamento finalizado válido (1h, sem sobreposição) | Status `FINALIZADO`, duração correta |
| CA-02 | Lançamento com fim antes ou igual ao início | Recusa (4xx) |
| CA-03 | Dois finalizados do mesmo e-mail com sobreposição | Recusa com mensagem de conflito |
| CA-04 | Dois finalizados encostados (10h–11h e 11h–12h) | Ambos aceitos |
| CA-05 | Iniciar cronômetro para colaborador sem outro em andamento | Lançamento `EM_ANDAMENTO` criado |
| CA-06 | Iniciar segundo cronômetro para o mesmo e-mail | Recusa |
| CA-07 | Parar cronômetro em andamento | `FINALIZADO` com fim preenchido |
| CA-08 | Relatório de totais por projeto no período | Soma só `FINALIZADO`; bate com lançamentos |
| CA-09 | Exportar CSV do período | Arquivo/resposta CSV com colunas exigidas; sem `EM_ANDAMENTO` |
| CA-10 | Excluir lançamento `EM_ANDAMENTO` | Removido; parar cronômetro do mesmo e-mail volta a funcionar |
