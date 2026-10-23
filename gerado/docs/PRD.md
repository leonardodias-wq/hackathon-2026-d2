# PRD · Reserva de salas

## Problema

Reservas de salas em planilha compartilhada geram conflito de horário entre São Paulo, Araraquara e coworking.

## Objetivo

Sistema local simples para cadastrar salas, reservar sem sobreposição, consultar salas livres e medir ocupação diária — sem login.

## Escopo

**In**
- Cadastro de salas (nome, local, capacidade, recursos)
- Seed com 6 salas (2 por local)
- Reservas com validação de conflito, duração, passado e capacidade
- Cancelamento de reservas futuras (histórico `CANCELADA`)
- Consulta de salas livres (filtro local / capacidade)
- Relatório de ocupação (8h–18h, só `ATIVA`)
- API REST + UI web + SQLite local

**Out**
- Login, autenticação, papéis
- Notificações, integrações externas, nuvem
- Recorrência de reservas

## Entidades principais

- **Sala:** nome, local (`SAO_PAULO` | `ARARAQUARA` | `COWORKING`), capacidade, recursos (`TV`, `VIDEOCONFERENCIA`, `QUADRO`)
- **Reserva:** sala, responsável (nome + e-mail), título, participantes, início, fim, status (`ATIVA` | `CANCELADA`)

## Critérios de aceite

| Código | Resultado esperado |
|---|---|
| CA-01 | Reserva válida → `ATIVA` |
| CA-02 | Sobreposição → recusa com conflito |
| CA-03 | Encostar (10h–11h e 11h–12h) → criada |
| CA-04 | Duração 10 min ou 4h01 → recusa |
| CA-05 | Início no passado → recusa |
| CA-06 | Participantes > capacidade → recusa |
| CA-07 | Cancelar futura → `CANCELADA`, horário livre |
| CA-08 | Cancelar passada → recusa |
| CA-09 | Salas livres com filtro local + capacidade |
| CA-10 | Ocupação ignora canceladas |

## Stack

Python 3.11+, FastAPI, SQLite (`pysqlite3-binary` se necessário), pytest, HTML/CSS/JS estático servido pelo FastAPI.

## Premissas

- Sem login: identidade = nome + e-mail na reserva.
- Sobreposição: `inicio_a < fim_b AND inicio_b < fim_a`; encostar não conflita.
- Duração: mín. 15 min, máx. 4 h.
- Ocupação: janela 8h–18h (10 h = 600 min); só reservas `ATIVA`.
- Fuso: datetime naive (ISO local, sem timezone).
- Env do banco: `RESERVAS_DB` (padrão `reservas.db` em `gerado/`).
