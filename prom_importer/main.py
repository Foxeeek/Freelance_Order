"""Application entrypoint for importing products from Google Sheets."""

from __future__ import annotations

import logging
from typing import Any

from .config import load_settings
from .feed_generator import PromFeedGenerator
from .logger import configure_logging
from .sheets_service import SheetsService

LOGGER = logging.getLogger(__name__)



def main() -> None:
    """Run the product import flow."""
    configure_logging()
    settings = load_settings()

    sheets_service = SheetsService(
        service_account_file=str(settings.service_account_file),
        sheet_id=settings.sheet_id,
    )
    feed_generator = PromFeedGenerator()

    products = sheets_service.fetch_products()
    LOGGER.info("Parsed %d product(s).", len(products))

    payloads: list[dict[str, Any]] = [product.to_dict() for product in products]
    feed_generator.generate(payloads, output_path="prom_feed.xml")
    LOGGER.info("Feed generation completed successfully.")


if __name__ == "__main__":
    main()
