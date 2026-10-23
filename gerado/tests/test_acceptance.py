"""Critérios de aceite CA-01 .. CA-10 — controle de horas."""

from datetime import date

from tests.helpers import backdate_em_andamento, past_slot

EMAIL = "ana@empresa.com"
NOME = "Ana Silva"


def _payload(projeto_id: int, inicio: str, fim: str, desc: str = "Atividade") -> dict:
    return {
        "projeto_id": projeto_id,
        "colaborador_nome": NOME,
        "colaborador_email": EMAIL,
        "descricao": desc,
        "inicio": inicio,
        "fim": fim,
    }


def test_ca01_lancamento_finalizado_valido(client, projeto_id):
    inicio, fim = past_slot(hours_ago=2, duration_hours=1)
    res = client.post("/api/lancamentos", json=_payload(projeto_id, inicio, fim))
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "FINALIZADO"
    assert data["duracao_minutos"] == 60


def test_ca02_fim_antes_ou_igual_inicio(client, projeto_id):
    inicio, _ = past_slot(hours_ago=2, duration_hours=1)
    res = client.post(
        "/api/lancamentos",
        json=_payload(projeto_id, inicio, inicio),
    )
    assert 400 <= res.status_code < 500

    earlier = past_slot(hours_ago=3, duration_hours=1)
    res2 = client.post(
        "/api/lancamentos",
        json=_payload(projeto_id, earlier[1], earlier[0]),  # fim < início
    )
    assert 400 <= res2.status_code < 500


def test_ca03_sobreposicao_finalizados(client, projeto_id):
    inicio, fim = past_slot(hours_ago=5, duration_hours=2)
    assert client.post("/api/lancamentos", json=_payload(projeto_id, inicio, fim)).status_code == 201

    # overlap: começa no meio do primeiro
    from datetime import datetime, timedelta

    mid = datetime.fromisoformat(inicio) + timedelta(hours=1)
    fim2 = mid + timedelta(hours=1)
    res = client.post(
        "/api/lancamentos",
        json=_payload(projeto_id, mid.isoformat(timespec="seconds"), fim2.isoformat(timespec="seconds")),
    )
    assert res.status_code == 409
    assert "conflito" in res.json()["detail"].lower()


def test_ca04_encostados_aceitados(client, projeto_id):
    from datetime import datetime, timedelta

    base = datetime.now().replace(microsecond=0) - timedelta(days=1)
    # 10h–11h e 11h–12h no dia anterior
    d = base.replace(hour=10, minute=0, second=0)
    a0, a1 = d, d + timedelta(hours=1)
    b0, b1 = a1, a1 + timedelta(hours=1)
    r1 = client.post(
        "/api/lancamentos",
        json=_payload(projeto_id, a0.isoformat(timespec="seconds"), a1.isoformat(timespec="seconds"), "Bloco A"),
    )
    r2 = client.post(
        "/api/lancamentos",
        json=_payload(projeto_id, b0.isoformat(timespec="seconds"), b1.isoformat(timespec="seconds"), "Bloco B"),
    )
    assert r1.status_code == 201
    assert r2.status_code == 201


def test_ca05_iniciar_cronometro(client, projeto_id):
    res = client.post(
        "/api/cronometro/iniciar",
        json={
            "projeto_id": projeto_id,
            "colaborador_nome": NOME,
            "colaborador_email": EMAIL,
            "descricao": "Foco",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "EM_ANDAMENTO"
    assert data["fim"] is None


def test_ca06_segundo_cronometro_mesmo_email(client, projeto_id):
    body = {
        "projeto_id": projeto_id,
        "colaborador_nome": NOME,
        "colaborador_email": EMAIL,
        "descricao": "Um",
    }
    assert client.post("/api/cronometro/iniciar", json=body).status_code == 201
    res = client.post(
        "/api/cronometro/iniciar",
        json={**body, "descricao": "Dois"},
    )
    assert res.status_code == 409


def test_ca07_parar_cronometro(client, projeto_id):
    assert (
        client.post(
            "/api/cronometro/iniciar",
            json={
                "projeto_id": projeto_id,
                "colaborador_nome": NOME,
                "colaborador_email": EMAIL,
                "descricao": "Sessão",
            },
        ).status_code
        == 201
    )
    backdate_em_andamento(EMAIL, minutes_ago=5)
    res = client.post("/api/cronometro/parar", json={"email": EMAIL})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "FINALIZADO"
    assert data["fim"] is not None
    assert data["duracao_minutos"] >= 1


def test_ca08_relatorio_totais_projeto(client, projeto_id):
    inicio, fim = past_slot(hours_ago=4, duration_hours=2)
    client.post("/api/lancamentos", json=_payload(projeto_id, inicio, fim, "A"))
    # EM_ANDAMENTO não deve entrar
    client.post(
        "/api/cronometro/iniciar",
        json={
            "projeto_id": projeto_id,
            "colaborador_nome": NOME,
            "colaborador_email": "outro@empresa.com",
            "descricao": "Aberto",
        },
    )
    dia = date.fromisoformat(inicio[:10])
    res = client.get(
        f"/api/relatorio?data_inicio={dia.isoformat()}&data_fim={dia.isoformat()}"
    )
    assert res.status_code == 200
    data = res.json()
    por = {p["projeto_id"]: p["total_minutos"] for p in data["por_projeto"]}
    assert por[projeto_id] == 120


def test_ca09_export_csv(client, projeto_id):
    inicio, fim = past_slot(hours_ago=6, duration_hours=1)
    client.post("/api/lancamentos", json=_payload(projeto_id, inicio, fim))
    client.post(
        "/api/cronometro/iniciar",
        json={
            "projeto_id": projeto_id,
            "colaborador_nome": NOME,
            "colaborador_email": "csv-open@empresa.com",
            "descricao": "Não vai ao CSV",
        },
    )
    dia = inicio[:10]
    res = client.get(f"/api/relatorio/csv?data_inicio={dia}&data_fim={dia}")
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    text = res.text
    header = text.splitlines()[0]
    cols = [
        "projeto",
        "cliente",
        "colaborador",
        "email",
        "descricao",
        "inicio",
        "fim",
        "duracao_minutos",
        "status",
    ]
    assert header == ",".join(cols)
    assert "EM_ANDAMENTO" not in text
    assert "FINALIZADO" in text
    assert "Não vai ao CSV" not in text


def test_ca10_excluir_em_andamento(client, projeto_id):
    body = {
        "projeto_id": projeto_id,
        "colaborador_nome": NOME,
        "colaborador_email": EMAIL,
        "descricao": "Abortar",
    }
    created = client.post("/api/cronometro/iniciar", json=body).json()
    res = client.delete(f"/api/lancamentos/{created['id']}")
    assert res.status_code == 204
    # Novo cronômetro deve funcionar
    again = client.post("/api/cronometro/iniciar", json={**body, "descricao": "De novo"})
    assert again.status_code == 201
    assert again.json()["status"] == "EM_ANDAMENTO"
