from datetime import datetime, timedelta

FUTURE_DAY = datetime(2030, 6, 15, 10, 0, 0)


def iso(dt: datetime) -> str:
    return dt.isoformat()


def reserva_payload(client, sala_id: int, start: datetime, duration_min: int = 60, participantes: int = 4):
    end = start + timedelta(minutes=duration_min)
    return client.post(
        "/api/reservas",
        json={
            "sala_id": sala_id,
            "responsavel_nome": "Ana",
            "responsavel_email": "ana@example.com",
            "titulo": "Reunião",
            "participantes": participantes,
            "inicio": iso(start),
            "fim": iso(end),
        },
    )


def test_ca01_reserva_valida(client):
    r = reserva_payload(client, 1, FUTURE_DAY)
    assert r.status_code == 201
    assert r.json()["status"] == "ATIVA"


def test_ca02_conflito_sobreposicao(client):
    base = FUTURE_DAY + timedelta(hours=2)
    assert reserva_payload(client, 1, base).status_code == 201
    overlap = client.post(
        "/api/reservas",
        json={
            "sala_id": 1,
            "responsavel_nome": "Bia",
            "responsavel_email": "bia@example.com",
            "titulo": "Conflito",
            "participantes": 2,
            "inicio": iso(base + timedelta(minutes=30)),
            "fim": iso(base + timedelta(minutes=90)),
        },
    )
    assert overlap.status_code == 409
    assert "conflito" in overlap.json()["detail"].lower()


def test_ca03_horarios_encostados(client):
    sala = 2
    first = FUTURE_DAY + timedelta(hours=4)
    assert reserva_payload(client, sala, first, 60).status_code == 201
    second_start = first + timedelta(hours=1)
    r = reserva_payload(client, sala, second_start, 60)
    assert r.status_code == 201
    assert r.json()["status"] == "ATIVA"


def test_ca04_duracao_invalida(client):
    base = FUTURE_DAY + timedelta(hours=6)
    short = client.post(
        "/api/reservas",
        json={
            "sala_id": 3,
            "responsavel_nome": "C",
            "responsavel_email": "c@example.com",
            "titulo": "Curta",
            "participantes": 2,
            "inicio": iso(base),
            "fim": iso(base + timedelta(minutes=10)),
        },
    )
    long = client.post(
        "/api/reservas",
        json={
            "sala_id": 3,
            "responsavel_nome": "D",
            "responsavel_email": "d@example.com",
            "titulo": "Longa",
            "participantes": 2,
            "inicio": iso(base + timedelta(hours=1)),
            "fim": iso(base + timedelta(hours=1, minutes=241)),
        },
    )
    assert short.status_code == 400
    assert long.status_code == 400


def test_ca05_inicio_passado(client):
    past = datetime.utcnow() - timedelta(hours=2)
    r = reserva_payload(client, 4, past, 60)
    assert r.status_code == 400


def test_ca06_capacidade(client):
    salas = client.get("/api/salas").json()
    sala_pequena = next(s for s in salas if s["capacidade"] == 6)
    r = reserva_payload(client, sala_pequena["id"], FUTURE_DAY + timedelta(hours=8), 60, participantes=99)
    assert r.status_code == 400


def test_ca07_cancelar_futura(client):
    start = FUTURE_DAY + timedelta(hours=10)
    created = reserva_payload(client, 5, start, 60)
    rid = created.json()["id"]
    cancel = client.post(f"/api/reservas/{rid}/cancelar")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "CANCELADA"
    # horário liberado
    again = reserva_payload(client, 5, start, 60)
    assert again.status_code == 201


def test_ca08_cancelar_passada(client):
    start = datetime.utcnow() + timedelta(minutes=30)
    end = datetime.utcnow() + timedelta(minutes=90)
    r = client.post(
        "/api/reservas",
        json={
            "sala_id": 6,
            "responsavel_nome": "F",
            "responsavel_email": "f@example.com",
            "titulo": "Futura curta",
            "participantes": 2,
            "inicio": iso(start),
            "fim": iso(end),
        },
    )
    assert r.status_code == 201
    rid = r.json()["id"]
    from app.database import get_connection

    conn = get_connection()
    past_end = (datetime.utcnow() - timedelta(minutes=5)).isoformat()
    past_start = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    conn.execute(
        "UPDATE reservas SET inicio = ?, fim = ? WHERE id = ?",
        (past_start, past_end, rid),
    )
    conn.commit()
    conn.close()
    cancel = client.post(f"/api/reservas/{rid}/cancelar")
    assert cancel.status_code == 400


def test_ca09_salas_livres_filtro(client):
    sala_id = 1
    block_start = FUTURE_DAY + timedelta(days=1, hours=9)
    assert reserva_payload(client, sala_id, block_start, 120).status_code == 201
    ini = block_start - timedelta(minutes=30)
    end = block_start + timedelta(hours=3)
    livres = client.get(
        "/api/salas/livres",
        params={
            "inicio": iso(ini),
            "fim": iso(end),
            "local": "SAO_PAULO",
            "capacidade_min": 8,
        },
    )
    assert livres.status_code == 200
    ids = {s["id"] for s in livres.json()}
    assert sala_id not in ids
    assert all(s["local"] == "SAO_PAULO" and s["capacidade"] >= 8 for s in livres.json())


def test_ca10_relatorio_ocupacao(client):
    day = "2030-06-16"
    start = datetime(2030, 6, 16, 9, 0, 0)
    assert reserva_payload(client, 1, start, 60).status_code == 201
    created = reserva_payload(client, 2, start + timedelta(hours=2), 60)
    rid_cancel = created.json()["id"]
    client.post(f"/api/reservas/{rid_cancel}/cancelar")
    rep = client.get("/api/relatorios/ocupacao", params={"data": day})
    assert rep.status_code == 200
    by_sala = {r["sala_id"]: r for r in rep.json()}
    assert by_sala[1]["minutos_ocupados"] == 60
    assert by_sala[2]["minutos_ocupados"] == 0
