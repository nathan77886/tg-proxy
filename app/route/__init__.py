from ..model import on_event_stream
from loguru import logger
from ..bot import *
from .. import app
from fastapi.responses import StreamingResponse

# https://tg-proxy.coinpaas.com/sse/-4750287705/barrage
@app.get("/sse/{group_id}/barrage")
async def on_sse_barrage_open(group_id: str):
    return StreamingResponse(
        on_event_stream(group_id), media_type="text/event-stream"
    )


@app.get("/hello")
async def hello():
    return "hello"


from .room import *
