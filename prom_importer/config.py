"""Application configuration loading utilities."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings required by the importer service."""

    sheet_id: str
    service_account_file: Path



def load_settings() -> Settings:
    """Load and validate settings from environment variables and `.env` file."""
    load_dotenv()

    sheet_id: str | None = os.getenv("GOOGLE_SHEET_ID")
    credentials_path: str | None = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

    if not sheet_id:
        raise ValueError("Missing required environment variable: GOOGLE_SHEET_ID")

    if not credentials_path:
        raise ValueError(
            "Missing required environment variable: GOOGLE_SERVICE_ACCOUNT_FILE"
        )

    service_account_file = Path(credentials_path).expanduser().resolve()
    if not service_account_file.exists():
        raise FileNotFoundError(
            f"Service account file not found: {service_account_file}"
        )

    return Settings(sheet_id=sheet_id, service_account_file=service_account_file)
