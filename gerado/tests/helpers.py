from datetime import datetime, timedelta


def future_slot(hours_ahead: int = 24, duration_minutes: int = 60):
    """Retorna (inicio_iso, fim_iso) no futuro, alinhado à hora cheia."""
    start = datetime.now().replace(minute=0, second=0, microsecond=0) + timedelta(
        hours=hours_ahead
    )
    end = start + timedelta(minutes=duration_minutes)
    return start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds")


def past_slot(hours_ago: int = 24, duration_minutes: int = 60):
    end = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(
        hours=hours_ago
    )
    start = end - timedelta(minutes=duration_minutes)
    return start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds")


def payload(sala_id: int, inicio: str, fim: str, **extra):
    base = {
        "sala_id": sala_id,
        "responsavel_nome": "Ana Silva",
        "responsavel_email": "ana@example.com",
        "titulo": "Reunião",
        "participantes": 2,
        "inicio": inicio,
        "fim": fim,
    }
    base.update(extra)
    return base
