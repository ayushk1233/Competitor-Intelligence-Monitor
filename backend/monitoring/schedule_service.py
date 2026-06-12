from datetime import UTC, datetime, timedelta


def calculate_next_run(
    frequency: str,
) -> datetime:

    now = datetime.now(UTC)

    frequency = frequency.upper()

    if frequency == "HOURLY":
        return now + timedelta(hours=1)

    if frequency == "DAILY":
        return now + timedelta(days=1)

    if frequency == "WEEKLY":
        return now + timedelta(days=7)

    return now + timedelta(days=1)
