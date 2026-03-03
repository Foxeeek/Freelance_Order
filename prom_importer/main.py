"""Application entrypoint for importing products from Google Sheets."""

from __future__ import annotations

import logging

from .config import load_settings
from .logger import configure_logging
from .sheets_service import SheetsService

LOGGER = logging.getLogger(__name__)



def main() -> None:
    """Run the product import flow."""
    configure_logging()
    settings = load_settings()

    service = SheetsService(
        service_account_file=str(settings.service_account_file),
        sheet_id=settings.sheet_id,
    )

    products = service.fetch_products()
    LOGGER.info("Parsed %d product(s).", len(products))

    for product in products:
        LOGGER.info("Product row=%d payload=%s", product.row_number, product.to_dict())


if __name__ == "__main__":
    main()
