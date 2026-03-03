from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from freelance_ai.app.database import SessionLocal
from freelance_ai.core.analyzer import analyze_order
from freelance_ai.core.models import OrderStatus
from freelance_ai.core.platform_registry import build_platform_registry
from freelance_ai.services.order_service import OrderService

logger = logging.getLogger(__name__)


class FetchScheduler:
    def __init__(self, poll_interval_minutes: int, notifier: object | None = None):
        self.scheduler = AsyncIOScheduler()
        self.poll_interval_minutes = poll_interval_minutes
        self.notifier = notifier

    async def run_cycle(self) -> None:
        registry = build_platform_registry()
        if not registry:
            logger.info("No enabled platforms configured.")
            return

        for platform_name, platform in registry.items():
            logger.info("Fetching orders from %s", platform_name)
            raw_orders = await platform.fetch_orders()
            for raw in raw_orders:
                try:
                    order_in = platform.parse(raw)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse order from %s: %s", platform_name, exc)
                    continue

                with SessionLocal() as session:
                    service = OrderService(session)
                    order_db, is_new = service.upsert_order(order_in)
                    analysis = analyze_order(order_in)
                    order_db = service.save_analysis(order_db.id, analysis) or order_db

                    if is_new and order_db.status == OrderStatus.NEW:
                        if self.notifier:
                            await self.notifier.send_order(order_db)
                            service.mark_sent(order_db.id)
                        else:
                            logger.info("Notifier disabled; order %s kept in NEW state.", order_db.id)

    def start(self) -> None:
        self.scheduler.add_job(self.run_cycle, trigger="interval", minutes=self.poll_interval_minutes, max_instances=1)
        self.scheduler.start()
