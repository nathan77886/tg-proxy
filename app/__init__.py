from fastapi import FastAPI, WebSocket
from .bot import *
from .model import set_channel, remove_channel
import asyncio
from loguru import logger
import uuid

app = FastAPI()


@app.websocket("/ws/{group_id}/barrage")
async def on_ws_barrage_open(websocket: WebSocket, group_id: str):
    await websocket.accept()
    random_id = str(uuid.uuid4())
    set_channel(group_id, websocket, random_id)
    logger.info(f"{group_id} connect watch")
    try:
        while True:
            await asyncio.sleep(1)
            await websocket.send_json({"type": "heartbeat"})
    except Exception as e:
        logger.info(f"{group_id} disconnect watch")
        remove_channel(group_id, random_id)

@app.get("/hello")
async def hello():
    return "hello"
