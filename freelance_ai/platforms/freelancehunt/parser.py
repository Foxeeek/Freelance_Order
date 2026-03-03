from __future__ import annotations

from bs4 import BeautifulSoup


def parse_job_cards(html: str) -> list[dict]:
    """Minimal HTML parser example for Freelancehunt public pages."""
    soup = BeautifulSoup(html, "html.parser")
    cards: list[dict] = []
    for card in soup.select(".project-card"):
        title_el = card.select_one(".project-card__title a")
        desc_el = card.select_one(".project-card__description")
        if not title_el:
            continue

        href = title_el.get("href")
        cards.append(
            {
                "external_id": card.get("data-project-id") or (href or "").strip("/").split("/")[-1],
                "title": title_el.get_text(strip=True),
                "description": desc_el.get_text(" ", strip=True) if desc_el else "",
                "url": href,
                "budget_raw": None,
            }
        )
    return cards
