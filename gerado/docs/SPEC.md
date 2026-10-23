# SPEC · Reserva de salas

## Modelo de dados

### Sala

| Campo | Tipo |
|---|---|
| id | int PK |
| nome | string |
| local | enum: SAO_PAULO, ARARAQUARA, COWORKING |
| capacidade | int |
| recursos | JSON array: TV, VIDEOCONFERENCIA, QUADRO |

Seed: 6 salas (2 por local).

### Reserva

| Campo | Tipo |
|---|---|
| id | int PK |
| sala_id | FK |
| responsavel_nome | string |
| responsavel_email | string |
| titulo | string |
| participantes | int |
| inicio | datetime |
| fim | datetime |
| status | ATIVA \| CANCELADA |

## Invariantes

- Duração: 15 min ≤ (fim - início) ≤ 4 h
- início ≥ agora (criação)
- participantes ≤ capacidade da sala
- Duas reservas ATIVA na mesma sala não podem sobrepor (encostar permitido)
- Cancelamento só se fim > agora

## API REST

| Método | Path | Descrição |
|---|---|---|
| GET | /api/salas | listar salas |
| POST | /api/salas | criar sala |
| GET | /api/reservas | listar (filtro data opcional) |
| POST | /api/reservas | criar |
| POST | /api/reservas/{id}/cancelar | cancelar |
| GET | /api/salas/livres | query: inicio, fim, local?, capacidade_min? |
| GET | /api/relatorios/ocupacao | query: data (YYYY-MM-DD) |

Erros: 400 validação, 409 conflito de horário.

## UI

- `/` — formulário de reserva + agenda do dia por sala (GET reservas do dia).

## Verificação CA

Um teste pytest por CA em `tests/test_acceptance.py`.
