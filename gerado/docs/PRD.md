# PRD · Reserva de salas

## Problema

Conflitos de reserva de salas em planilha compartilhada entre São Paulo, Araraquara e coworking.

## Objetivo

Sistema local simples para cadastrar salas, reservar sem conflito, consultar disponibilidade e relatório de ocupação.

## Escopo

**In:** salas (6 iniciais), reservas, cancelamento, consulta de livres, relatório diário, API REST, UI web mínima, SQLite, sem login.

**Out:** autenticação, deploy em nuvem, integrações externas.

## Entidades

- Sala: nome, local, capacidade, recursos
- Reserva: sala, responsável, título, participantes, início, fim, status

## Critérios de aceite

CA-01 a CA-10 conforme `PEDIDO-TREINO.md`.

## Stack

Python 3.11+, FastAPI, SQLite, pytest, HTML/JS estático.

## Premissas

- Fuso horário: UTC nos testes; API aceita ISO 8601.
- Mensagens de erro em português quando aplicável.
