"""Domain models used by the importer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    """Represents one parsed product row from Google Sheets."""

    row_number: int
    data: dict[str, str]

    def to_dict(self) -> dict[str, str]:
        """Return the product payload as a plain dictionary."""
        return dict(self.data)
