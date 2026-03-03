"""FastAPI application serving Prom.ua XML feed from Google Sheets data."""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from prom_importer.config import load_settings
from prom_importer.feed_generator import PromFeedGenerator
from prom_importer.logger import configure_logging
from prom_importer.sheets_service import SheetsService

configure_logging()
LOGGER = logging.getLogger(__name__)

app = FastAPI(title="Prom Importer API", version="1.0.0")


@app.get("/feed", response_class=Response)
def get_feed() -> Response:
    """Read Google Sheets products and return generated YML XML feed."""
    try:
        settings = load_settings()
        sheets_service = SheetsService(
            service_account_file=str(settings.service_account_file),
            sheet_id=settings.sheet_id,
        )

        products = sheets_service.fetch_products()
        payloads = [product.to_dict() for product in products]

        xml_payload = PromFeedGenerator().generate_xml_bytes(payloads)
        LOGGER.info("Generated in-memory feed with %d products", len(payloads))
        return Response(content=xml_payload, media_type="application/xml")
    except Exception as exc:
        LOGGER.exception("Failed to generate feed")
        raise HTTPException(status_code=500, detail="Failed to generate feed") from exc


# Run with:
# uvicorn app:app --host 0.0.0.0 --port 8000
