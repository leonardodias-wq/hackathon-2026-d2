# PRD · Controle de horas

## Problema

A equipe registra horas em planilha e ninguém confia no total do fim do mês.

## Objetivo

Sistema local simples para cadastrar projetos, lançar horas (manual ou cronômetro), consultar totais e exportar CSV por período — sem login.

## Escopo

**In**
- Cadastro de projetos (nome, cliente, cor hex)
- Lançamentos manuais e via cronômetro (iniciar/parar)
- Regras de duração, sobreposição e um único `EM_ANDAMENTO` por e-mail
- Edição de finalizados; exclusão só de em andamento
- Consulta por colaborador/período; relatório e export CSV
- API REST + UI web + SQLite local

**Out**
- Login, autenticação, papéis
- Integrações externas, nuvem, notificações
- Folha de pagamento ou faturamento

## Entidades principais

- **Projeto:** nome, cliente, cor (`#RRGGBB`)
- **Lançamento:** projeto, colaborador (nome + e-mail), descrição, início, fim (nullable), status (`FINALIZADO` | `EM_ANDAMENTO`)

## Critérios de aceite

| Código | Resultado esperado |
|---|---|
| CA-01 | Lançamento finalizado válido → `FINALIZADO`, duração correta |
| CA-02 | Fim ≤ início → 4xx |
| CA-03 | Sobreposição de finalizados (mesmo e-mail) → conflito |
| CA-04 | Encostados (10h–11h e 11h–12h) → ambos aceitos |
| CA-05 | Iniciar cronômetro sem outro em andamento → `EM_ANDAMENTO` |
| CA-06 | Segundo cronômetro mesmo e-mail → recusa |
| CA-07 | Parar cronômetro → `FINALIZADO` com fim |
| CA-08 | Relatório: soma só `FINALIZADO` no período |
| CA-09 | CSV com colunas exigidas; sem `EM_ANDAMENTO` |
| CA-10 | Excluir `EM_ANDAMENTO` → removido; novo cronômetro funciona |

## Stack

Python 3.11+, FastAPI, SQLite (`pysqlite3-binary` se necessário), pytest, HTML/CSS/JS estático servido pelo FastAPI.

## Premissas

- Sem login: identidade = nome + e-mail no lançamento.
- Seed: 3 projetos iniciais.
- Fuso: horários em ISO local sem conversão de timezone (naive datetime).
- Env do banco: `HORAS_DB` (padrão `horas.db` na pasta `gerado/`).
- Duração mínima: 1 minuto quando finalizado; sem teto máximo no pedido.
