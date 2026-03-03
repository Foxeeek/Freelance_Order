from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from freelance_ai.app.database import SessionLocal
from freelance_ai.core.models import OrderAnalysis, OrderDB
from freelance_ai.core.proposal_generator import generate_proposal
from freelance_ai.services.order_service import OrderService


def _analysis_from_order(order: OrderDB) -> OrderAnalysis | None:
    if order.difficulty is None or order.codex_fit is None:
        return None
    return OrderAnalysis(
        difficulty=order.difficulty,
        codex_fit=order.codex_fit,
        detected_stack=order.detected_stack.split(",") if order.detected_stack else [],
        estimated_hours_range=(order.estimated_hours_min or 1, order.estimated_hours_max or 3),
        estimated_price_range=(order.estimated_price_min or 0, order.estimated_price_max or 0),
        risk_flags=order.risk_flags.split(",") if order.risk_flags else [],
        language=order.language,
    )


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()
    if not query.data:
        return

    action, _, raw_order_id = query.data.partition(":")
    if not raw_order_id.isdigit():
        return

    order_id = int(raw_order_id)

    with SessionLocal() as session:
        service = OrderService(session)
        order = session.get(OrderDB, order_id)
        if not order:
            await query.edit_message_text("Order not found.")
            return

        if action == "approve":
            order = service.mark_approved(order_id)
            if not order:
                return
            analysis = _analysis_from_order(order)
            if analysis:
                proposal = generate_proposal(order, analysis, language=order.language)
                await context.bot.send_message(chat_id=query.message.chat_id, text=f"📨 Draft proposal:\n\n{proposal}")
            await query.edit_message_reply_markup(reply_markup=None)
            return

        if action == "reject":
            reason = order.risk_flags or "manual_reject"
            service.mark_rejected(order_id, reason=reason)
            await query.edit_message_reply_markup(reply_markup=None)
            await context.bot.send_message(chat_id=query.message.chat_id, text=f"🚫 Order {order_id} rejected: {reason}")


def register_handlers(app: Application) -> None:
    app.add_handler(CallbackQueryHandler(callback_router, pattern=r"^(approve|reject):\d+$"))
