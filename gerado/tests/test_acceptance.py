from datetime import datetime, timedelta

from tests.helpers import future_slot, past_slot, payload


def test_ca01_reserva_valida(client, sala_id):
    inicio, fim = future_slot(hours_ahead=48, duration_minutes=60)
    res = client.post("/api/reservas", json=payload(sala_id, inicio, fim))
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["status"] == "ATIVA"
    assert body["sala_id"] == sala_id


def test_ca02_conflito_sobreposicao(client, sala_id):
    inicio, fim = future_slot(hours_ahead=50, duration_minutes=60)
    r1 = client.post("/api/reservas", json=payload(sala_id, inicio, fim, titulo="A"))
    assert r1.status_code == 201, r1.text

    overlap_ini = (datetime.fromisoformat(inicio) + timedelta(minutes=30)).isoformat(
        timespec="seconds"
    )
    overlap_fim = (datetime.fromisoformat(fim) + timedelta(minutes=30)).isoformat(
        timespec="seconds"
    )
    r2 = client.post(
        "/api/reservas",
        json=payload(sala_id, overlap_ini, overlap_fim, titulo="B"),
    )
    assert r2.status_code == 409, r2.text
    assert "conflito" in r2.json()["detail"].lower()


def test_ca03_horarios_encostados(client, sala_id):
    inicio, fim = future_slot(hours_ahead=52, duration_minutes=60)
    r1 = client.post("/api/reservas", json=payload(sala_id, inicio, fim, titulo="A"))
    assert r1.status_code == 201, r1.text

    # 11h–12h após 10h–11h (encostar no fim)
    inicio2 = fim
    fim2 = (datetime.fromisoformat(fim) + timedelta(hours=1)).isoformat(
        timespec="seconds"
    )
    r2 = client.post(
        "/api/reservas",
        json=payload(sala_id, inicio2, fim2, titulo="B"),
    )
    assert r2.status_code == 201, r2.text
    assert r2.json()["status"] == "ATIVA"


def test_ca04_duracao_invalida(client, sala_id):
    # 10 minutos
    inicio, _ = future_slot(hours_ahead=60, duration_minutes=60)
    fim_curto = (datetime.fromisoformat(inicio) + timedelta(minutes=10)).isoformat(
        timespec="seconds"
    )
    r_curto = client.post(
        "/api/reservas",
        json=payload(sala_id, inicio, fim_curto, titulo="curto"),
    )
    assert r_curto.status_code == 400, r_curto.text
    assert "duração" in r_curto.json()["detail"].lower() or "15" in r_curto.json()[
        "detail"
    ]

    # 4h01
    inicio2, _ = future_slot(hours_ahead=70, duration_minutes=60)
    fim_longo = (
        datetime.fromisoformat(inicio2) + timedelta(hours=4, minutes=1)
    ).isoformat(timespec="seconds")
    r_longo = client.post(
        "/api/reservas",
        json=payload(sala_id, inicio2, fim_longo, titulo="longo"),
    )
    assert r_longo.status_code == 400, r_longo.text


def test_ca05_inicio_passado(client, sala_id):
    inicio, fim = past_slot(hours_ago=2, duration_minutes=60)
    res = client.post("/api/reservas", json=payload(sala_id, inicio, fim))
    assert res.status_code == 400, res.text
    assert "passado" in res.json()["detail"].lower()


def test_ca06_capacidade(client, sala_id):
    salas = client.get("/api/salas").json()
    sala = next(s for s in salas if s["id"] == sala_id)
    inicio, fim = future_slot(hours_ahead=80, duration_minutes=60)
    res = client.post(
        "/api/reservas",
        json=payload(
            sala_id,
            inicio,
            fim,
            participantes=sala["capacidade"] + 1,
            titulo="lotado",
        ),
    )
    assert res.status_code == 400, res.text
    assert "capacidade" in res.json()["detail"].lower()


def test_ca07_cancelar_futura(client, sala_id):
    inicio, fim = future_slot(hours_ahead=90, duration_minutes=60)
    criada = client.post(
        "/api/reservas",
        json=payload(sala_id, inicio, fim, titulo="cancelável"),
    )
    assert criada.status_code == 201
    rid = criada.json()["id"]

    cancel = client.post(f"/api/reservas/{rid}/cancelar")
    assert cancel.status_code == 200, cancel.text
    assert cancel.json()["status"] == "CANCELADA"

    # Horário liberado: nova reserva no mesmo intervalo
    nova = client.post(
        "/api/reservas",
        json=payload(sala_id, inicio, fim, titulo="reaproveita"),
    )
    assert nova.status_code == 201, nova.text
    assert nova.json()["status"] == "ATIVA"


def test_ca08_cancelar_passada(client, sala_id):
    """Insere reserva já terminada direto no DB (API não permite passado)."""
    from app.database import connect

    inicio, fim = past_slot(hours_ago=5, duration_minutes=60)
    with connect() as conn:
        cur = conn.execute(
            """
            INSERT INTO reservas
            (sala_id, responsavel_nome, responsavel_email, titulo, participantes, inicio, fim, status)
            VALUES (?, 'Ana', 'ana@example.com', 'passada', 2, ?, ?, 'ATIVA')
            """,
            (sala_id, inicio, fim),
        )
        conn.commit()
        rid = cur.lastrowid

    res = client.post(f"/api/reservas/{rid}/cancelar")
    assert res.status_code == 400, res.text
    assert "passado" in res.json()["detail"].lower() or "não é possível" in res.json()[
        "detail"
    ].lower()


def test_ca09_salas_livres_filtro(client):
    salas = client.get("/api/salas").json()
    sp = [s for s in salas if s["local"] == "SAO_PAULO"]
    assert len(sp) >= 2
    sala_ocupada = sp[0]
    sala_livre = sp[1]

    inicio, fim = future_slot(hours_ahead=110, duration_minutes=60)
    r = client.post(
        "/api/reservas",
        json=payload(sala_ocupada["id"], inicio, fim, titulo="ocupa SP"),
    )
    assert r.status_code == 201

    livres = client.get(
        "/api/salas/livres",
        params={
            "inicio": inicio,
            "fim": fim,
            "local": "SAO_PAULO",
            "capacidade_min": sala_livre["capacidade"],
        },
    )
    assert livres.status_code == 200, livres.text
    ids = {s["id"] for s in livres.json()}
    assert sala_ocupada["id"] not in ids
    assert sala_livre["id"] in ids
    for s in livres.json():
        assert s["local"] == "SAO_PAULO"
        assert s["capacidade"] >= sala_livre["capacidade"]


def test_ca10_ocupacao_ignora_canceladas(client, sala_id):
    # Dia futuro fixo para o relatório
    dia = (datetime.now() + timedelta(days=5)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    data = dia.strftime("%Y-%m-%d")

    # ATIVA: 09:00–11:00 → 2h = 120 min dentro de 8–18
    ativa_ini = dia.replace(hour=9).isoformat(timespec="seconds")
    ativa_fim = dia.replace(hour=11).isoformat(timespec="seconds")
    r_ativa = client.post(
        "/api/reservas",
        json=payload(sala_id, ativa_ini, ativa_fim, titulo="ativa"),
    )
    assert r_ativa.status_code == 201, r_ativa.text

    # CANCELADA: 13:00–15:00 → não deve contar
    canc_ini = dia.replace(hour=13).isoformat(timespec="seconds")
    canc_fim = dia.replace(hour=15).isoformat(timespec="seconds")
    r_canc = client.post(
        "/api/reservas",
        json=payload(sala_id, canc_ini, canc_fim, titulo="canc"),
    )
    assert r_canc.status_code == 201, r_canc.text
    cancel = client.post(f"/api/reservas/{r_canc.json()['id']}/cancelar")
    assert cancel.status_code == 200

    rel = client.get("/api/relatorios/ocupacao", params={"data": data})
    assert rel.status_code == 200, rel.text
    row = next(x for x in rel.json() if x["sala_id"] == sala_id)
    assert row["minutos_ocupados"] == 120
    assert abs(row["taxa_ocupacao"] - (120 / 600)) < 1e-6
