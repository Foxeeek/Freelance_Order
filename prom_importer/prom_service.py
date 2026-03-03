"""PROM API integration service."""

from __future__ import annotations

import logging
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)


class PromService:
    """Service client for interacting with PROM product API."""

    BASE_URL = "https://my.prom.ua/api/v1"

    def __init__(self, api_token: str, timeout_seconds: float = 15.0) -> None:
        if not api_token.strip():
            raise ValueError("PROM API token cannot be empty.")

        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def create_product(self, product: dict[str, Any]) -> dict[str, Any]:
        """Create a product in PROM and return parsed JSON response."""
        response = self._session.post(
            f"{self.BASE_URL}/products", json=product, timeout=self._timeout_seconds
        )

        response_body = self._safe_response_json(response)
        LOGGER.info(
            "PROM create product response status=%s body=%s",
            response.status_code,
            response_body,
        )

        if response.status_code >= 400:
            raise requests.HTTPError(
                f"PROM API request failed with status={response.status_code}, "
                f"body={response_body}",
                response=response,
            )

        return response_body

    @staticmethod
    def _safe_response_json(response: requests.Response) -> dict[str, Any]:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                return payload
            return {"data": payload}
        except ValueError:
            return {"raw": response.text}
