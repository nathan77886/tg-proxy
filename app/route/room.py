import os
from typing import Dict

import requests
from fastapi import Body, Query, WebSocket, WebSocketDisconnect, Request, HTTPException
from loguru import logger
from pydantic import Field, BaseModel

from app import app
from app.model.room import (
    create_room as create_room_db,
    get_room_session,
    set_room_user_connect,
    create_user_connect,
    on_room_message,
    on_websocket_disconnect,
    set_live_room
)
from app.utils.ice_server import get_ice_server


def get_cf_headers():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.getenv("APP_TOKEN"),
    }
    return headers


class RoomCreateRequest(BaseModel):
    nick_name: str = Field()
    live_room: bool = Field()


@app.post("/room/create")
async def create_room(request: Request, body: RoomCreateRequest = Body()):
    """Create a new room."""
    room_id, room_name = await create_room_db()
    if body.live_room:
        await set_live_room(room_name, body.nick_name)
        logger.info(f"创建直播模式房间:{room_name},主播:{body.live_room}")
    return {"room_id": room_id, "room_name": room_name, "live_name":body.live_room}


@app.post("/room/session/{room_name}/create")
async def create_room_session(room_name: str, request: Request):
    app_id = os.getenv("APP_ID")

    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/new?{request.url.query}"
    headers = get_cf_headers()
    res = requests.post(url, headers=headers)
    if res.status_code != 201:
        logger.error(f"Failed to create room: {res.text}")
        return {"error": "Failed to create room"}
    data = res.json()
    session_id = data["sessionId"]
    room_id, room_name = await create_room_db(session_id)
    return {"room_id": room_id, "sessionId": session_id, "room_name": room_name}


@app.get("/room/session/{room_name}")
async def get_room_session_by_room_name(room_name: str):
    """Get the session id of a room."""
    session_id = await get_room_session(room_name)
    return {"sessionId": session_id}

@app.get("/room/live/player/{room_name}")
async def get_room_live_player(room_name: str):
    from app.db.redis import redis_conn
    player_name = redis_conn.get(f"tgproxy:live_room:{room_name}")
    return {"player": player_name}


@app.get("/room/session/tracks/{session_id}")
async def get_room_tracks(session_id: str, request):
    """Get the tracks of a room."""
    app_id = os.getenv("APP_ID")
    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/{session_id}?{request.url.query}"
    headers = get_cf_headers()
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        logger.error(f"Failed to get tracks: {res.text}")
        return {"error": "Failed to get tracks"}
    return res.json()


@app.post("/room/session/tracks/{session_id}/new")
async def create_room_tracks(session_id: str, request: Request):
    """Create a new track in a room."""
    body_json = await request.json()
    app_id = os.getenv("APP_ID")
    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/{session_id}/tracks/new?{request.url.query}"
    headers = get_cf_headers()
    logger.info(f"Create room tracks: {url}, {body_json}")
    res = requests.post(url, json=body_json, headers=headers)
    if res.status_code != 200:
        logger.error(f"Failed to create track: {res.text}")
        ## 返回500
        raise HTTPException(status_code=500, detail=res.json())
    return res.json()


class RoomConfigRequest(BaseModel):
    mode: str = Field(..., description="Mode of the room configuration")
    api_extra_params: Dict[str, str] = Field(
        {},
        description="Extra parameters to be passed to the API, in JSON format",
    )
    room_name:str = Field(..., description="Name of the room")

@app.put("/room/session/tracks/{session_id}/renegotiate")
async def renegotiate_room_tracks(session_id: str, request: Request):
    """Renegotiate a room configuration with mode and api_extra_params from the request body."""
    body_json = await request.json()
    app_id = os.getenv("APP_ID")
    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/{session_id}/renegotiate?{request.url.query}"
    headers = get_cf_headers()
    logger.info(f"Renegotiate room tracks: {url}, {body_json}")
    res = requests.put(url, json=body_json, headers=headers)
    if res.status_code != 200:
        logger.error(f"Failed to renegotiate track: {res.text}")
    return res.json()


@app.put("/room/session/tracks/{session_id}/close")
async def close_room_tracks(session_id: str, request: Request):
    """Close a room configuration with mode and api_extra_params from the request body."""
    body_json = await request.json()
    app_id = os.getenv("APP_ID")
    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/{session_id}/tracks/close?{request.url.query}"
    headers = get_cf_headers()
    logger.info(f"Close room tracks: {url}, {body_json}")
    res = requests.put(url, json=body_json, headers=headers)
    if res.status_code != 200:
        logger.error(f"Failed to close track: {res.text}")
    return res.json()


@app.post("/room/config/load")
async def load_room_config(body: RoomConfigRequest = Body()):
    """Load a room configuration with mode and api_extra_params from the request body."""

    ice_servers = await get_ice_server()
    feedback_enabled = bool(
        os.getenv("FEEDBACK_URL")
        and os.getenv("FEEDBACK_QUEUE")
        and os.getenv("FEEDBACK_STORAGE")
    )
    max_webcam_framerate = os.getenv("MAX_WEBCAM_FRAMERATE", 24)
    max_webcam_bitrate = os.getenv("MAX_WEBCAM_BITRATE", 1200000)
    max_webcam_quality_level = os.getenv("MAX_WEBCAM_QUALITY_LEVEL", 1080)
    max_api_history = os.getenv("MAX_API_HISTORY", 100)
    from app.db.redis import redis_conn
    player_name = redis_conn.get(f"tgproxy:live_room:{body.room_name}")
    return {
        "mode": body.mode,
        "userDirectoryUrl": os.getenv("USER_DIRECTORY_URL"),
        "traceLink": os.getenv("TRACE_LINK"),
        "apiExtraParams": body.api_extra_params,
        "iceServers": ice_servers,
        "feedbackEnabled": feedback_enabled,
        "maxWebcamFramerate": max_webcam_framerate,
        "maxWebcamBitrate": max_webcam_bitrate,
        "maxWebcamQualityLevel": max_webcam_quality_level,
        "maxApiHistory": max_api_history,
        "live_player": player_name
    }


@app.websocket("/room/keep/{user_name}/parties/rooms/{room_name}")
async def keep_room(websocket: WebSocket, room_name: str, user_name: str, _pk: str = Query()):
    await websocket.accept()
    if user_name == "":
        await websocket.close()
        return
    connect_id = _pk
    logger.info(f"user {user_name} join room {room_name} connect with conn id: {connect_id}")
    set_room_user_connect(connect_id, websocket)
    await create_user_connect(connect_id, user_name, room_name)
    try:
        while True:
            data = await websocket.receive_json()
            print(f"{user_name} receive:" + str(data))
            await on_room_message(connect_id, room_name, data)
    except WebSocketDisconnect:
        await on_websocket_disconnect(connect_id, room_name)
    except Exception as e:
        logger.info(f"{room_name} disconnect watch: {e}")
