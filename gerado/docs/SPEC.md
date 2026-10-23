# SPEC · Reserva de salas

## Modelo de dados

### salas
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | autoincrement |
| nome | TEXT | obrigatório |
| local | TEXT | `SAO_PAULO` \| `ARARAQUARA` \| `COWORKING` |
| capacidade | INTEGER | > 0 |
| recursos | TEXT | JSON array de `TV` \| `VIDEOCONFERENCIA` \| `QUADRO` |

### reservas
| Campo | Tipo | Notas |
|---|---|---|
| id | INTEGER PK | autoincrement |
| sala_id | INTEGER FK | → salas.id |
| responsavel_nome | TEXT | obrigatório |
| responsavel_email | TEXT | obrigatório |
| titulo | TEXT | obrigatório |
| participantes | INTEGER | ≥ 1 |
| inicio | TEXT | ISO datetime |
| fim | TEXT | ISO datetime |
| status | TEXT | `ATIVA` \| `CANCELADA` |

**Invariantes:** `inicio < fim`; duração ∈ [15 min, 4 h]; participantes ≤ capacidade da sala; sem sobreposição entre `ATIVA` da mesma sala.

## Seed (6 salas)

| Nome | Local | Cap. | Recursos |
|---|---|---|---|
| SP Sala A | SAO_PAULO | 8 | TV, VIDEOCONFERENCIA |
| SP Sala B | SAO_PAULO | 4 | QUADRO |
| AQ Sala A | ARARAQUARA | 10 | TV, QUADRO |
| AQ Sala B | ARARAQUARA | 6 | VIDEOCONFERENCIA |
| CW Sala A | COWORKING | 12 | TV, VIDEOCONFERENCIA, QUADRO |
| CW Sala B | COWORKING | 2 | — |

## API REST

### GET /api/salas
Lista salas. 200 → `[{id, nome, local, capacidade, recursos}]`

### POST /api/salas
Body: `{nome, local, capacidade, recursos[]}`. 201 → sala. 400 se enum/capacidade inválidos.

### GET /api/reservas?data=YYYY-MM-DD&sala_id=
Lista reservas (opcional filtro). 200 → lista.

### POST /api/reservas
Body: `{sala_id, responsavel_nome, responsavel_email, titulo, participantes, inicio, fim}`.  
201 → reserva `ATIVA`.  
400 duração/passado/capacidade/validação.  
404 sala inexistente.  
409 conflito de horário.

### POST /api/reservas/{id}/cancelar
200 → reserva `CANCELADA`.  
400 se já cancelada ou já passou (`fim <= agora`).  
404 se não existe.

### GET /api/salas/livres?inicio=&fim=&local=&capacidade_min=
Salas sem reserva `ATIVA` sobreposta no intervalo; filtros opcionais. 200 → salas. 400 se intervalo inválido.

### GET /api/relatorios/ocupacao?data=YYYY-MM-DD
Por sala: minutos ativos no intervalo [8h, 18h] ∩ reserva, taxa = minutos / 600. Canceladas ignoradas. 200 → `[{sala_id, nome, minutos_ocupados, taxa_ocupacao}]`.

## Regras de negócio

1. **Sobreposição:** `inicio_a < fim_b AND inicio_b < fim_a` entre ATIVAs da mesma sala → 409.
2. **Encostar:** `fim_a == inicio_b` permitido.
3. **Duração:** `(fim - inicio)` ∈ [15, 240] minutos; fora → 400.
4. **Passado:** `inicio < agora` → 400.
5. **Capacidade:** `participantes > sala.capacidade` → 400.
6. **Cancelar futura:** só se `status=ATIVA` e `fim > agora`; libera horário.
7. **Cancelar passada:** `fim <= agora` → 400.
8. **Ocupação:** só ATIVA; clip em [08:00, 18:00] do dia; taxa = minutos_clip / 600.

## UI (`static/`)

1. Contexto: “Reserva de salas sem conflito de horário”.
2. Formulário “Nova reserva” + feedback sucesso/erro.
3. Agenda do dia: tabela Sala | Horário | Título | Status (chips ATIVA/CANCELADA).
4. Sem `innerHTML` com dados da API.

## Plano de verificação (CA)

| CA | Teste |
|---|---|
| CA-01 | `test_ca01_reserva_valida` |
| CA-02 | `test_ca02_conflito_sobreposicao` |
| CA-03 | `test_ca03_horarios_encostados` |
| CA-04 | `test_ca04_duracao_invalida` |
| CA-05 | `test_ca05_inicio_passado` |
| CA-06 | `test_ca06_capacidade` |
| CA-07 | `test_ca07_cancelar_futura` |
| CA-08 | `test_ca08_cancelar_passada` |
| CA-09 | `test_ca09_salas_livres_filtro` |
| CA-10 | `test_ca10_ocupacao_ignora_canceladas` |
