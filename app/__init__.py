from fastapi import FastAPI, WebSocket
from .bot import *
from .model import set_channel
import asyncio
from loguru import logger

app = FastAPI()


@app.websocket("/ws/{group_id}/barrage")
async def on_ws_barrage_open(websocket: WebSocket, group_id: str):
    await websocket.accept()
    set_channel(group_id, websocket)
    logger.info(f"{group_id} connect watch")
    try:
        while True:
            data = await websocket.receive_text()
            await asyncio.sleep(10)
            await websocket.send_json({"type": "heartbeat"})
    except Exception as e:
        logger.info(f"{group_id} disconnect watch")

@app.get("/hello")
async def hello():
    return "hello"