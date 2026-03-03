from __future__ import annotations

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application

from freelance_ai.app.config import get_settings
from freelance_ai.bot.handlers import register_handlers
from freelance_ai.core.models import OrderDB

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, app: Application, chat_id: str):
        self.app = app
        self.chat_id = chat_id

    async def send_order(self, order: OrderDB) -> None:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve:{order.id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject:{order.id}"),
                ]
            ]
        )
        text = (
            f"🆕 New order ({order.platform})\n"
            f"ID: {order.id}\n"
            f"Title: {order.title}\n"
            f"Fit: {order.codex_fit or '-'} / 100\n"
            f"Difficulty: {order.difficulty or '-'} / 10\n"
            f"URL: {order.url or 'N/A'}"
        )
        await self.app.bot.send_message(chat_id=self.chat_id, text=text, reply_markup=keyboard)


def build_telegram_application() -> tuple[Application | None, TelegramNotifier | None]:
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        logger.warning("Telegram bot token/chat_id missing; bot notifications are disabled.")
        return None, None

    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    register_handlers(app)
    notifier = TelegramNotifier(app, settings.TELEGRAM_CHAT_ID)
    return app, notifier
