from __future__ import annotations

from freelance_ai.app.config import get_settings
from freelance_ai.core.models import OrderAnalysis, OrderIn
from freelance_ai.core.scorer import estimate_hours_range, estimate_price_range

COMPLEXITY_KEYWORDS = {
    "api": 1,
    "integration": 2,
    "scraping": 2,
    "payments": 2,
    "mobile": 2,
    "blockchain": 3,
    "highload": 3,
    "kubernetes": 3,
}

HIGH_FIT = ["crud", "api", "automation", "integration", "bot", "parser"]
LOW_FIT = ["blockchain", "kernel", "driver", "kubernetes", "pentest", "highload", "enterprise"]
RISK_PATTERNS = {
    "enterprise": "enterprise",
    "login": "login_required",
    "unknown": "unknown_scope",
    "tbd": "unknown_scope",
    "kubernetes": "infra_heavy",
    "blockchain": "domain_complexity",
}


def analyze_order(order: OrderIn) -> OrderAnalysis:
    settings = get_settings()
    text = f"{order.title} {order.description}".lower()

    difficulty = 2
    for keyword, weight in COMPLEXITY_KEYWORDS.items():
        if keyword in text:
            difficulty += weight
    difficulty = min(10, max(1, difficulty))

    fit = 60
    fit += sum(8 for k in HIGH_FIT if k in text)
    fit -= sum(15 for k in LOW_FIT if k in text)
    codex_fit = min(100, max(0, fit))

    detected_stack = [kw for kw in ["python", "django", "flask", "fastapi", "react", "node", "sql"] if kw in text]
    hours_range = estimate_hours_range(difficulty)
    price_range = estimate_price_range(hours_range, settings.HOURLY_RATE_EUR)

    risk_flags = sorted({flag for pattern, flag in RISK_PATTERNS.items() if pattern in text})

    return OrderAnalysis(
        difficulty=difficulty,
        codex_fit=codex_fit,
        detected_stack=detected_stack,
        estimated_hours_range=hours_range,
        estimated_price_range=price_range,
        risk_flags=risk_flags,
        language=order.language if order.language in {"en", "ua"} else settings.DEFAULT_LANGUAGE,
    )
