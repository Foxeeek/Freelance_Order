from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from freelance_ai.core.models import OrderAnalysis, OrderDB, OrderIn, OrderStatus


class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def upsert_order(self, order_in: OrderIn) -> tuple[OrderDB, bool]:
        stmt = select(OrderDB).where(OrderDB.platform == order_in.platform, OrderDB.external_id == order_in.external_id)
        order = self.session.execute(stmt).scalar_one_or_none()

        if order:
            order.title = order_in.title
            order.description = order_in.description
            order.budget_raw = order_in.budget_raw
            order.url = order_in.url
            order.language = order_in.language
            self.session.commit()
            self.session.refresh(order)
            return order, False

        order = OrderDB(
            platform=order_in.platform,
            external_id=order_in.external_id,
            title=order_in.title,
            description=order_in.description,
            budget_raw=order_in.budget_raw,
            url=order_in.url,
            language=order_in.language,
            status=OrderStatus.NEW,
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        return order, True

    def save_analysis(self, order_id: int, analysis: OrderAnalysis) -> OrderDB | None:
        order = self.session.get(OrderDB, order_id)
        if not order:
            return None
        order.difficulty = analysis.difficulty
        order.codex_fit = analysis.codex_fit
        order.detected_stack = ",".join(analysis.detected_stack)
        order.estimated_hours_min = analysis.estimated_hours_range[0]
        order.estimated_hours_max = analysis.estimated_hours_range[1]
        order.estimated_price_min = analysis.estimated_price_range[0]
        order.estimated_price_max = analysis.estimated_price_range[1]
        order.risk_flags = ",".join(analysis.risk_flags)
        order.language = analysis.language
        self.session.commit()
        self.session.refresh(order)
        return order

    def mark_sent(self, order_id: int) -> None:
        order = self.session.get(OrderDB, order_id)
        if order and order.status == OrderStatus.NEW:
            order.status = OrderStatus.SENT
            self.session.commit()

    def mark_approved(self, order_id: int) -> OrderDB | None:
        order = self.session.get(OrderDB, order_id)
        if not order:
            return None
        order.status = OrderStatus.APPROVED
        self.session.commit()
        self.session.refresh(order)
        return order

    def mark_rejected(self, order_id: int, reason: str) -> OrderDB | None:
        order = self.session.get(OrderDB, order_id)
        if not order:
            return None
        order.status = OrderStatus.REJECTED
        order.reject_reason = reason
        self.session.commit()
        self.session.refresh(order)
        return order
