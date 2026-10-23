from datetime import datetime, timedelta
from typing import Any

MIN_DURATION = timedelta(minutes=15)
MAX_DURATION = timedelta(hours=4)
WORK_START_HOUR = 8
WORK_END_HOUR = 18


def parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)


def overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    return a_start < b_end and b_start < a_end


def validate_reservation(
    sala_capacidade: int,
    participantes: int,
    inicio: datetime,
    fim: datetime,
    now: datetime,
) -> str | None:
    if participantes > sala_capacidade:
        return "Participantes acima da capacidade da sala"
    duration = fim - inicio
    if duration < MIN_DURATION or duration > MAX_DURATION:
        return "Duração inválida: mínimo 15 minutos e máximo 4 horas"
    if inicio < now:
        return "Não é possível reservar no passado"
    if fim <= inicio:
        return "Fim deve ser após o início"
    return None


def occupancy_minutes(inicio: datetime, fim: datetime, day: datetime) -> float:
    """Minutes of reservation within [8h, 18h] on given calendar day."""
    day_start = day.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
    day_end = day.replace(hour=WORK_END_HOUR, minute=0, second=0, microsecond=0)
    start = max(inicio, day_start)
    end = min(fim, day_end)
    if end <= start:
        return 0.0
    return (end - start).total_seconds() / 60.0


def row_to_sala(row: Any) -> dict:
    import json

    return {
        "id": row["id"],
        "nome": row["nome"],
        "local": row["local"],
        "capacidade": row["capacidade"],
        "recursos": json.loads(row["recursos"]),
    }


def row_to_reserva(row: Any) -> dict:
    return {
        "id": row["id"],
        "sala_id": row["sala_id"],
        "responsavel_nome": row["responsavel_nome"],
        "responsavel_email": row["responsavel_email"],
        "titulo": row["titulo"],
        "participantes": row["participantes"],
        "inicio": row["inicio"],
        "fim": row["fim"],
        "status": row["status"],
    }
