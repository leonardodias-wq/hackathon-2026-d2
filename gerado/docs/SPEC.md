# SPEC · Controle de horas

## Modelo de dados

### Projeto

| Campo | Tipo | Regras |
|---|---|---|
| id | INTEGER PK | autoincrement |
| nome | TEXT | obrigatório, não vazio |
| cliente | TEXT | obrigatório, não vazio |
| cor | TEXT | `#RRGGBB` (hex 6 dígitos) |

### Lançamento

| Campo | Tipo | Regras |
|---|---|---|
| id | INTEGER PK | autoincrement |
| projeto_id | INTEGER FK | projeto existente |
| colaborador_nome | TEXT | obrigatório |
| colaborador_email | TEXT | obrigatório; comparação case-insensitive |
| descricao | TEXT | obrigatório |
| inicio | TEXT ISO | datetime; não no futuro na criação |
| fim | TEXT ISO \| NULL | NULL se `EM_ANDAMENTO` |
| status | TEXT | `FINALIZADO` \| `EM_ANDAMENTO` |

### Invariantes

1. `FINALIZADO` ⇒ `fim` preenchido e `fim > inicio`; duração ≥ 1 minuto.
2. `EM_ANDAMENTO` ⇒ `fim` NULL; no máximo um por e-mail (normalizado lower).
3. Sobreposição de dois `FINALIZADO` do mesmo e-mail: `inicio_a < fim_b AND inicio_b < fim_a`. Encostar (`fim_a == inicio_b`) **não** é sobreposição.
4. Só `EM_ANDAMENTO` pode ser excluído.
5. Edição só de `FINALIZADO` (descrição, projeto, início, fim); revalida duração e sobreposição (excluindo o próprio id).

## Endpoints

### Projetos

| Método | Path | Body / query | Resposta |
|---|---|---|---|
| GET | `/api/projetos` | — | lista de projetos |
| POST | `/api/projetos` | `{nome, cliente, cor}` | 201 projeto |

Erros: 400 cor inválida / campos vazios.

### Lançamentos

| Método | Path | Body / query | Resposta |
|---|---|---|---|
| GET | `/api/lancamentos` | `email`, `data_inicio`, `data_fim` (obrigatórios) | lista no intervalo (por início) |
| POST | `/api/lancamentos` | projeto_id, colaborador_*, descricao, inicio, fim | 201 `FINALIZADO` |
| PATCH | `/api/lancamentos/{id}` | campos editáveis | lançamento atualizado |
| DELETE | `/api/lancamentos/{id}` | — | 204 se `EM_ANDAMENTO` |

Erros: 400 validação; 404 não encontrado; 409 conflito de sobreposição ou já em andamento.

### Cronômetro

| Método | Path | Body | Resposta |
|---|---|---|---|
| POST | `/api/cronometro/iniciar` | projeto_id, colaborador_*, descricao | 201 `EM_ANDAMENTO`, inicio=agora |
| POST | `/api/cronometro/parar` | email | 200 `FINALIZADO`, fim=agora |

Erros: 409 se já há em andamento (iniciar) ou nenhum (parar); 400 duração &lt; 1 min ao parar.

### Relatório e CSV

| Método | Path | Query | Resposta |
|---|---|---|---|
| GET | `/api/relatorio` | `data_inicio`, `data_fim` | `{ por_projeto, por_colaborador }` só FINALIZADO |
| GET | `/api/relatorio/csv` | `data_inicio`, `data_fim` | `text/csv` |

Colunas CSV: `projeto,cliente,colaborador,email,descricao,inicio,fim,duracao_minutos,status`.

Intervalo inclusivo por data do `inicio` (date part).

### UI

| Método | Path | — |
|---|---|---|
| GET | `/` | `static/index.html` |
| GET | `/static/*` | assets |

## Regras de negócio testáveis

- R1: duração_minutos = floor((fim - inicio).total_seconds() / 60) ≥ 1
- R2: fim ≤ inicio ⇒ 400
- R3: início no futuro ⇒ 400
- R4: overlap FINALIZADO mesmo e-mail ⇒ 409
- R5: encostar permitido
- R6: um EM_ANDAMENTO por e-mail
- R7: parar define fim=agora e FINALIZADO
- R8: relatório/CSV ignoram EM_ANDAMENTO
- R9: DELETE só EM_ANDAMENTO; após delete, iniciar funciona

## Telas / fluxos UI

1. **Topo:** nome do sistema + frase de contexto.
2. **Cronômetro:** projeto, nome, e-mail, descrição → Iniciar / Parar.
3. **Lançamento manual:** mesmos campos + início/fim → Salvar.
4. **Lista do dia:** lançamentos do e-mail informado com início na data de hoje.
5. **Exportar:** botão CSV do mês corrente (`data_inicio` = 1º dia, `data_fim` = último dia).

## Plano de verificação (CA)

| CA | Como verificar |
|---|---|
| CA-01 | POST lançamento 1h → 201, status, duração 60 |
| CA-02 | fim ≤ início → 4xx |
| CA-03 | segundo overlapping → 409 + mensagem |
| CA-04 | 10–11 e 11–12 → ambos 201 |
| CA-05 | POST iniciar → EM_ANDAMENTO |
| CA-06 | segundo iniciar mesmo e-mail → 409 |
| CA-07 | POST parar → FINALIZADO com fim |
| CA-08 | GET relatório → totais batem |
| CA-09 | GET csv → colunas; sem EM_ANDAMENTO |
| CA-10 | DELETE EM_ANDAMENTO → 204; iniciar de novo OK |
