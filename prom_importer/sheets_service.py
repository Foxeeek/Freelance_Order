"""Google Sheets API integration for loading and parsing product rows."""

from __future__ import annotations

from collections.abc import Sequence
import logging

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource, build

from .models import Product

LOGGER = logging.getLogger(__name__)
SCOPES: list[str] = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class SheetsService:
    """Service object responsible for Google Sheets interactions."""

    def __init__(self, service_account_file: str, sheet_id: str) -> None:
        self.sheet_id = sheet_id
        self._client: Resource = self._build_client(service_account_file)

    @staticmethod
    def _build_client(service_account_file: str) -> Resource:
        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=SCOPES
        )
        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def fetch_products(self) -> list[Product]:
        """Read first worksheet and parse rows into Product objects."""
        first_sheet_title = self._get_first_sheet_title()
        values = self._get_sheet_values(first_sheet_title)

        if not values:
            LOGGER.warning("Sheet '%s' is empty.", first_sheet_title)
            return []

        headers = [header.strip() for header in values[0]]
        data_rows = values[1:]

        return self._parse_products(headers=headers, rows=data_rows)

    def _get_first_sheet_title(self) -> str:
        metadata: dict = (
            self._client.spreadsheets()
            .get(spreadsheetId=self.sheet_id)
            .execute()
        )
        sheets = metadata.get("sheets", [])

        if not sheets:
            raise ValueError("No sheets found in the spreadsheet.")

        first_sheet = sheets[0]
        title = first_sheet.get("properties", {}).get("title")
        if not title:
            raise ValueError("First sheet has no title.")

        LOGGER.info("Using first sheet: %s", title)
        return title

    def _get_sheet_values(self, sheet_title: str) -> list[list[str]]:
        response: dict = (
            self._client.spreadsheets()
            .values()
            .get(spreadsheetId=self.sheet_id, range=f"'{sheet_title}'")
            .execute()
        )
        return response.get("values", [])

    @staticmethod
    def _parse_products(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> list[Product]:
        products: list[Product] = []

        normalized_headers = [header for header in headers if header]
        if not normalized_headers:
            raise ValueError("Header row is empty. Cannot parse products.")

        for row_index, row in enumerate(rows, start=2):
            if not row or not any(str(cell).strip() for cell in row):
                continue

            row_values = [str(cell).strip() for cell in row]
            padded_values = row_values + [""] * max(0, len(headers) - len(row_values))

            mapped_row = {
                header: value
                for header, value in zip(headers, padded_values, strict=False)
                if header
            }

            if any(mapped_row.values()):
                products.append(Product(row_number=row_index, data=mapped_row))

        return products
