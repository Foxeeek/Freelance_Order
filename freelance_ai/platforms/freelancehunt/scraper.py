from __future__ import annotations

import logging

import httpx

from freelance_ai.core.models import OrderIn
from freelance_ai.platforms.base import BasePlatform
from freelance_ai.platforms.freelancehunt.parser import parse_job_cards

logger = logging.getLogger(__name__)


class FreelancehuntPlatform(BasePlatform):
    platform_name = "freelancehunt"
    PUBLIC_URL = "https://freelancehunt.com/projects"

    async def fetch_orders(self) -> list[dict]:
        """
        TODO: Replace with authenticated scraping logic if needed.
        MVP behavior: fail-safe and return empty list when unavailable.
        """
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(self.PUBLIC_URL)
                response.raise_for_status()
                return parse_job_cards(response.text)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Freelancehunt fetch failed; returning empty list: %s", exc)
            return []

    def parse(self, raw: dict) -> OrderIn:
        external_id = str(raw.get("external_id") or "").strip()
        title = str(raw.get("title") or "Untitled project").strip()
        description = str(raw.get("description") or "").strip()
        url = raw.get("url")

        return OrderIn(
            platform=self.platform_name,
            external_id=external_id or title.lower().replace(" ", "-")[:64],
            title=title,
            description=description,
            budget_raw=raw.get("budget_raw"),
            url=url,
            language="en",
        )
