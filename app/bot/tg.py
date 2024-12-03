from dataclasses import dataclass
from telegram import Update
from typing import NoReturn
from .handler import application

def run_bot() -> NoReturn:
    # bot = application.bot.get_me()
    # logger.info(f"{bot.first_name}@{bot.username} start")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        timeout=10,
        read_timeout=10,
        connect_timeout=10,
        write_timeout=10,
    )
