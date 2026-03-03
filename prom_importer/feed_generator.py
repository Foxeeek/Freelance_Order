"""YML feed generation for Prom.ua."""

from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

LOGGER = logging.getLogger(__name__)


class PromFeedGenerator:
    """Generate a YML XML product feed compatible with Prom.ua."""

    SHOP_NAME = "Test Shop"
    COMPANY_NAME = "Test Company"
    CURRENCY_ID = "UAH"

    def generate(self, products: list[dict[str, Any]], output_path: str) -> None:
        """Generate and persist a Prom.ua feed as pretty-formatted XML."""
        root = ET.Element(
            "yml_catalog", {"date": datetime.now().strftime("%Y-%m-%d %H:%M")}
        )
        shop = ET.SubElement(root, "shop")

        ET.SubElement(shop, "name").text = self.SHOP_NAME
        ET.SubElement(shop, "company").text = self.COMPANY_NAME

        currencies = ET.SubElement(shop, "currencies")
        ET.SubElement(currencies, "currency", {"id": self.CURRENCY_ID, "rate": "1"})

        offers = ET.SubElement(shop, "offers")

        for index, product in enumerate(products, start=1):
            offer = ET.SubElement(
                offers,
                "offer",
                {"id": str(index), "available": "true"},
            )

            name = str(product.get("name", "")).strip()
            price = str(product.get("price", "")).strip()
            description = str(product.get("description", "")).strip()
            picture = str(product.get("picture", "")).strip()

            ET.SubElement(offer, "name").text = name
            ET.SubElement(offer, "price").text = price
            ET.SubElement(offer, "currencyId").text = self.CURRENCY_ID
            ET.SubElement(offer, "description").text = description
            if picture:
                ET.SubElement(offer, "picture").text = picture

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")

        target_path = Path(output_path)
        tree.write(target_path, encoding="utf-8", xml_declaration=True)

        LOGGER.info("Prom feed generated: %s (offers=%d)", target_path, len(products))
