"""Background worker with scheduled jobs."""

import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from eve_intel.analytics.arbitrage import ArbitrageEngine
from eve_intel.db.base import get_db_session
from eve_intel.logging import configure_logging, get_logger
from eve_intel.settings import settings

logger = get_logger(__name__)


async def ingest_market_data() -> None:
    """Ingest market snapshots from ESI."""
    logger.info("starting_market_ingestion")

    try:
        # TODO: Implement actual ESI ingestion
        # For MVP, this is a placeholder
        logger.info("market_ingestion_placeholder")
    except Exception as e:
        logger.error("market_ingestion_failed", error=str(e))


async def run_arbitrage_analytics() -> None:
    """Run arbitrage analysis and save results."""
    logger.info("starting_arbitrage_analytics")

    try:
        async with get_db_session() as session:
            engine = ArbitrageEngine(session)

            # Find opportunities
            candidates = await engine.find_arbitrage_opportunities()

            # Save results
            if candidates:
                run_id = await engine.save_run_results(candidates)
                logger.info(
                    "arbitrage_analytics_complete",
                    run_id=run_id,
                    num_candidates=len(candidates),
                )
            else:
                logger.info("no_arbitrage_candidates_found")

    except Exception as e:
        logger.error("arbitrage_analytics_failed", error=str(e))


async def main() -> None:
    """Run worker with scheduled jobs."""
    configure_logging()

    logger.info("starting_worker", ingestion_schedule=settings.ingestion_cron_schedule)

    scheduler = AsyncIOScheduler()

    # Schedule market data ingestion
    scheduler.add_job(
        ingest_market_data,
        CronTrigger.from_crontab(settings.ingestion_cron_schedule),
        id="ingest_market_data",
        name="Market Data Ingestion",
        replace_existing=True,
    )

    # Schedule arbitrage analytics
    scheduler.add_job(
        run_arbitrage_analytics,
        CronTrigger.from_crontab(settings.analytics_cron_schedule),
        id="run_arbitrage_analytics",
        name="Arbitrage Analytics",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("worker_started", jobs=len(scheduler.get_jobs()))

    # Run once on startup
    await run_arbitrage_analytics()

    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("worker_shutdown")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
