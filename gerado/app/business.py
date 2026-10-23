import re
from datetime import datetime

HEX_COR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def parse_dt(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1]
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError("Data/hora inválida") from exc


def duration_minutes(inicio: datetime, fim: datetime) -> int:
    return int((fim - inicio).total_seconds() // 60)


def overlaps(inicio_a: datetime, fim_a: datetime, inicio_b: datetime, fim_b: datetime) -> bool:
    return inicio_a < fim_b and inicio_b < fim_a


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_cor(cor: str) -> str:
    if not HEX_COR.match(cor.strip()):
        raise ValueError("Cor inválida; use #RRGGBB")
    return cor.strip().upper()


def validate_finalizado(inicio: datetime, fim: datetime, *, now: datetime | None = None) -> int:
    if fim <= inicio:
        raise ValueError("Fim deve ser depois do início")
    mins = duration_minutes(inicio, fim)
    if mins < 1:
        raise ValueError("Duração mínima de 1 minuto")
    ref = now or datetime.now()
    if inicio > ref:
        raise ValueError("Início não pode ser no futuro")
    return mins


def row_to_projeto(row) -> dict:
    return {
        "id": row["id"],
        "nome": row["nome"],
        "cliente": row["cliente"],
        "cor": row["cor"],
    }


def row_to_lancamento(row, projeto: dict | None = None) -> dict:
    data = {
        "id": row["id"],
        "projeto_id": row["projeto_id"],
        "colaborador_nome": row["colaborador_nome"],
        "colaborador_email": row["colaborador_email"],
        "descricao": row["descricao"],
        "inicio": row["inicio"],
        "fim": row["fim"],
        "status": row["status"],
    }
    if row["fim"]:
        inicio = parse_dt(row["inicio"])
        fim = parse_dt(row["fim"])
        data["duracao_minutos"] = duration_minutes(inicio, fim)
    else:
        data["duracao_minutos"] = None
    if projeto:
        data["projeto"] = projeto
    return data


def find_overlap(
    conn,
    email: str,
    inicio: datetime,
    fim: datetime,
    exclude_id: int | None = None,
) -> dict | None:
    email_n = normalize_email(email)
    rows = conn.execute(
        """
        SELECT * FROM lancamentos
        WHERE lower(colaborador_email) = ?
          AND status = 'FINALIZADO'
          AND fim IS NOT NULL
        """,
        (email_n,),
    ).fetchall()
    for row in rows:
        if exclude_id is not None and row["id"] == exclude_id:
            continue
        other_inicio = parse_dt(row["inicio"])
        other_fim = parse_dt(row["fim"])
        if overlaps(inicio, fim, other_inicio, other_fim):
            return row_to_lancamento(row)
    return None


def find_em_andamento(conn, email: str) -> dict | None:
    row = conn.execute(
        """
        SELECT * FROM lancamentos
        WHERE lower(colaborador_email) = ? AND status = 'EM_ANDAMENTO'
        LIMIT 1
        """,
        (normalize_email(email),),
    ).fetchone()
    return row_to_lancamento(row) if row else None
