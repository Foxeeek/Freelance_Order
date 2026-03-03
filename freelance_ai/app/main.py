from __future__ import annotations

import asyncio
import logging

from freelance_ai.app.config import get_settings
from freelance_ai.app.database import init_db
from freelance_ai.bot.telegram_bot import build_telegram_application
from freelance_ai.services.scheduler import FetchScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


async def run() -> None:
    settings = get_settings()
    init_db()

    app, notifier = build_telegram_application()
    scheduler = FetchScheduler(poll_interval_minutes=settings.POLL_INTERVAL_MINUTES, notifier=notifier)
    scheduler.start()
    await scheduler.run_cycle()

    if app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        logger.info("Bot polling started")

    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutdown requested")
    finally:
        scheduler.scheduler.shutdown(wait=False)
        if app:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
