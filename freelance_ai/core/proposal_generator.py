from __future__ import annotations

from freelance_ai.core.models import OrderAnalysis, OrderDB


def generate_proposal(order: OrderDB, analysis: OrderAnalysis, language: str = "en") -> str:
    if language == "ua":
        return (
            f"Вітаю!\n\n"
            f"Готовий виконати проєкт: {order.title}.\n"
            f"Оцінка складності: {analysis.difficulty}/10, очікуваний час: "
            f"{analysis.estimated_hours_range[0]}-{analysis.estimated_hours_range[1]} годин.\n"
            f"Орієнтовна вартість: €{analysis.estimated_price_range[0]}-€{analysis.estimated_price_range[1]}.\n"
            "Можу почати одразу після узгодження деталей."
        )
    return (
        f"Hello!\n\n"
        f"I can help with your project: {order.title}.\n"
        f"Estimated complexity: {analysis.difficulty}/10 with delivery in "
        f"{analysis.estimated_hours_range[0]}-{analysis.estimated_hours_range[1]} hours.\n"
        f"Approximate budget: €{analysis.estimated_price_range[0]}-€{analysis.estimated_price_range[1]}.\n"
        "Happy to start as soon as we confirm details."
    )
