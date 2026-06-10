import logging
import uuid

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def run_scheduled_extraction(config_id: str, user_id: str):
    """Triggered by scheduler to run a connector extraction."""
    from app.db.session import async_session_factory
    from app.services.connector_runner import ConnectorRunner

    async with async_session_factory() as session:
        runner = ConnectorRunner(session)
        try:
            await runner.run_extraction(uuid.UUID(config_id), uuid.UUID(user_id))
        except Exception as exc:
            logger.error("Scheduled extraction failed for %s: %s", config_id, exc)


def schedule_connector(config_id: uuid.UUID, user_id: uuid.UUID, interval_hours: int = 6):
    """Add or update a scheduled job for a distributor connector."""
    job_id = f"connector_{config_id}"

    # Remove existing job if any
    existing = scheduler.get_job(job_id)
    if existing:
        scheduler.remove_job(job_id)

    scheduler.add_job(
        run_scheduled_extraction,
        trigger=IntervalTrigger(hours=interval_hours),
        id=job_id,
        args=[str(config_id), str(user_id)],
        replace_existing=True,
    )
    logger.info("Scheduled connector %s every %dh", config_id, interval_hours)


def unschedule_connector(config_id: uuid.UUID):
    """Remove a scheduled job for a distributor connector."""
    job_id = f"connector_{config_id}"
    existing = scheduler.get_job(job_id)
    if existing:
        scheduler.remove_job(job_id)
        logger.info("Unscheduled connector %s", config_id)


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
