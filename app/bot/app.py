from telegram.ext import Application

import os

bot_token = os.environ.get("bot_token")
if not bot_token:
    raise Exception("bot_token not found")

application = Application.builder().token(bot_token).build()

