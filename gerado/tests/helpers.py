from datetime import datetime, timedelta

from app.database import get_connection


def past_slot(hours_ago: float = 3, duration_hours: float = 1) -> tuple[str, str]:
    fim = datetime.now().replace(microsecond=0) - timedelta(hours=hours_ago)
    inicio = fim - timedelta(hours=duration_hours)
    return inicio.isoformat(timespec="seconds"), fim.isoformat(timespec="seconds")


def backdate_em_andamento(email: str, minutes_ago: int = 5) -> None:
    """Ajusta início do EM_ANDAMENTO para o passado (permite parar com duração ≥ 1 min)."""
    conn = get_connection()
    inicio = (datetime.now().replace(microsecond=0) - timedelta(minutes=minutes_ago)).isoformat(
        timespec="seconds"
    )
    conn.execute(
        """
        UPDATE lancamentos
        SET inicio = ?
        WHERE lower(colaborador_email) = ? AND status = 'EM_ANDAMENTO'
        """,
        (inicio, email.strip().lower()),
    )
    conn.commit()
    conn.close()
