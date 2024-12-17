from telegram.ext import Application
from loguru import logger
import os

application = None

def bot_init():
    run_bot = os.environ.get("run_bot")
    if not run_bot:
        return

    bot_token = os.environ.get("bot_token")
    if not bot_token:
        raise Exception("bot_token not found")

    logger.info("======Bot start=========")
    application = Application.builder().token(bot_token).build()

bot_init()