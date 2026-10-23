# Contrato de aceite — CA-01 a CA-10

Formato testável para implementação e evidência.

## CA-01 · Reserva válida

- **Given:** sala existente, horário futuro, duração entre 15 min e 4 h, participantes ≤ capacidade, sem conflito
- **When:** POST criar reserva
- **Then:** HTTP 201, `status` = `ATIVA`

**Prova:** `gerado/tests/test_acceptance.py::test_ca01_reserva_valida`

## CA-02 · Conflito de horário

- **Given:** reserva ATIVA 10h–11h na sala X
- **When:** nova reserva na sala X com sobreposição (ex. 10h30–11h30)
- **Then:** HTTP 409 (ou 400), mensagem menciona conflito

**Prova:** `test_ca02_conflito_sobreposicao`

## CA-03 · Horários encostados

- **Given:** reserva ATIVA 10h–11h
- **When:** nova reserva 11h–12h mesma sala
- **Then:** HTTP 201, `ATIVA`

**Prova:** `test_ca03_horarios_encostados`

## CA-04 · Duração inválida

- **Given:** sala livre
- **When:** reserva com 10 min OU 4h01
- **Then:** recusa (4xx)

**Prova:** `test_ca04_duracao_invalida`

## CA-05 · Passado

- **Given:** sala livre
- **When:** início no passado
- **Then:** recusa (4xx)

**Prova:** `test_ca05_inicio_passado`

## CA-06 · Capacidade

- **Given:** sala capacidade N
- **When:** participantes > N
- **Then:** recusa (4xx)

**Prova:** `test_ca06_capacidade`

## CA-07 · Cancelar futura

- **Given:** reserva ATIVA futura
- **When:** cancelar
- **Then:** `CANCELADA`, novo horário livre para reserva

**Prova:** `test_ca07_cancelar_futura`

## CA-08 · Cancelar passada

- **Given:** reserva já terminada
- **When:** cancelar
- **Then:** recusa (4xx)

**Prova:** `test_ca08_cancelar_passada`

## CA-09 · Salas livres com filtro

- **Given:** mix de salas/reservas
- **When:** GET salas livres no intervalo + filtro local + capacidade mínima
- **Then:** só salas livres que atendem filtros

**Prova:** `test_ca09_salas_livres_filtro`

## CA-10 · Ocupação ignora canceladas

- **Given:** dia com reservas ATIVA e CANCELADA
- **When:** relatório de ocupação do dia
- **Then:** taxa considera só ATIVA, janela 8h–18h

**Prova:** `test_ca10_relatorio_ocupacao`
