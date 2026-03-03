"""Application entrypoint for importing products from Google Sheets."""

from __future__ import annotations

import logging
from typing import Any

from .config import load_settings
from .logger import configure_logging
from .prom_service import PromService
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
    prom_service = PromService(api_token=settings.prom_api_token)

    products = sheets_service.fetch_products()
    LOGGER.info("Parsed %d product(s).", len(products))

    for product in products:
        payload: dict[str, Any] = product.to_dict()
        LOGGER.info("Sending product row=%d payload=%s", product.row_number, payload)
        result = prom_service.create_product(payload)
        LOGGER.info("Created product row=%d result=%s", product.row_number, result)


if __name__ == "__main__":
    main()
