from fastapi.responses import StreamingResponse

from app import app
from ..model import on_event_stream
from loguru import logger
import os
from fastapi.responses import FileResponse


# https://tg-proxy.coinpaas.com/sse/-4750287705/barrage
@app.get("/sse/{group_id}/barrage")
async def on_sse_barrage_open(group_id: str):
    return StreamingResponse(on_event_stream(group_id), media_type="text/event-stream")


## 头像
@app.get("/proxy/avatar/{user_id}")
async def get_avatar(user_id: str):
    from app.bot import application

    photos = await application.bot.get_user_profile_photos(user_id)
    # logger.info(f"get user {user_id} avatar {photos.to_json()}")
    i_photos = photos.photos[0][0]
    file_id = i_photos.file_id
    photo_file = await application.bot.get_file(file_id)
    file_path = os.path.join("/avatar", f"{user_id}_avatar.jpg")
    # 下载文件并保存到本地
    await photo_file.download_to_drive(file_path)
    return FileResponse(
        file_path,
        headers={"Content-Disposition": "inline; filename=avatar.jpg"},
        media_type="image/jpeg"
    )


@app.get("/hello")
async def hello():
    return "hello"
