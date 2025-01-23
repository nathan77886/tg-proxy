import json
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    CallbackContext,
    ExtBot,
    filters,
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, constants
from .app import application
from loguru import logger
from ..model import dispatch


async def on_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.effective_chat.id
    await dispatch(
        group_id,
        {
            "group_id": update.message.chat_id,
            "user_id": update.message.from_user.id,
            "message": update.message.text,
            "message_id": update.message.message_id,
            "message_date": update.message.date.timestamp(),
        },
    )


async def on_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理用户发送的id"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    logger.info(f"on cmd id from {chat_id}")
    await update.message.reply_text(
        f"你的id是:{user_id}\n 群组id是:<code>{chat_id}</code>", parse_mode="HTML"
    )


# 直播插件
async def on_live_plugin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.effective_chat.send_message(
        "直播插件页面",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "插件页面",
                        url=f"https://tgvideo.coinpaas.com/proxy?tg_group_id={chat_id}",
                    ),
                ],
                [InlineKeyboardButton("送礼物", callback_data="gift")],
            ]
        ),
    )


async def on_gift(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    await dispatch(
        chat_id,
        {
            "group_id": update.message.chat_id,
            "user_id": update.message.from_user.id,
            "message": update.message.text,
            "message_id": update.message.message_id,
            "message_date": update.message.date.timestamp(),
            "gift_id": 1
        },
    )


import os

run_bot = os.environ.get("run_bot")

if not run_bot:
    logger.info("handler bot")
    application.add_handler(CommandHandler("id", on_id))
    application.add_handler(CommandHandler("live", on_live_plugin))

    application.add_handler(CallbackQueryHandler(on_gift, "gift"))
    application.add_handler(MessageHandler(filters.TEXT, on_text_message, False))
    from .error_handler import error_handler

    application.add_error_handler(error_handler)
