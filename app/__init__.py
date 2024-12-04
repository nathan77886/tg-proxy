from fastapi import FastAPI, WebSocket
from .bot import *
from .model import set_channel, remove_channel
import asyncio
from loguru import logger
import uuid
from telegram import constants

app = FastAPI()


@app.websocket("/ws/{group_id}/barrage")
async def on_ws_barrage_open(websocket: WebSocket, group_id: str):
    await websocket.accept()
    from .bot.app import application
    group = await application.bot.get_chat(group_id)
    if not group:
        await websocket.close()
        return
    if group.type != constants.ChatType.GROUP and group.type != constants.ChatType.SUPERGROUP:
        await websocket.close()
        return
    random_id = str(uuid.uuid4())
    set_channel(group_id, websocket, random_id)
    logger.info(f"{group_id} connect watch")
    try:
        while True:
            await asyncio.sleep(10)
            await websocket.send_json({"type": "heartbeat"})
    except Exception as e:
        logger.info(f"{group_id} disconnect watch")
        remove_channel(group_id, random_id)
    
@app.get("/hello")
async def hello():
    return "hello"
