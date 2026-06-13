from backend.database.db_service import DatabaseService


async def is_suppressed(db_service: DatabaseService, company_name: str, alert_type: str) -> bool:
    """Check if an active suppression exists for this company and alert type."""
    suppression = await db_service.get_active_suppression(company_name, alert_type)
    return suppression is not None

async def suppress_alert(db_service: DatabaseService, company_name: str, alert_type: str, hours: int = 24):
    """Create a new suppression record for this company and alert type."""
    await db_service.create_suppression(company_name, alert_type, hours)
