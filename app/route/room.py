from typing import Dict

from pydantic import Field,BaseModel,Json

from app import app
import requests
import os
from app.model.room import create_room as create_room_db, get_room_session
from loguru import logger
from app.utils.ice_server import get_ice_server
from fastapi import Body

def get_cf_headers():
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.getenv("APP_TOKEN"),
    }
    return headers


@app.post("/room/create")
async def create_room():
    """Create a new room."""
    app_id = os.getenv("APP_ID")

    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/new"
    headers = get_cf_headers()
    res = requests.post(url, headers=headers)
    if res.status_code != 201:
        logger.error(f"Failed to create room: {res.text}")
        return {"error": "Failed to create room"}
    data = res.json()
    session_id = data["sessionId"]
    room = await create_room_db(session_id)
    return {"room_id": room.id, "session_id": session_id, "room_name": room.room_name}


@app.get("/room/session/tracks/{room_name}")
async def get_room_tracks(room_name: str):
    """Get the tracks of a room."""
    session_id = await get_room_session(room_name)
    if session_id is None:
        return {"error": "Room not found"}
    app_id = os.getenv("APP_ID")
    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/{session_id}"
    headers = get_cf_headers()
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        logger.error(f"Failed to get tracks: {res.text}")
        return {"error": "Failed to get tracks"}
    return res.json()


@app.post("/room/session/tracks/{room_name}/new")
async def create_room_tracks(room_name: str):
    """Create a new track in a room."""
    session_id = await get_room_session(room_name)
    if session_id is None:
        return {"error": "Room not found"}
    app_id = os.getenv("APP_ID")
    url = f"https://rtc.live.cloudflare.com/apps/{app_id}/sessions/{session_id}/tracks/new"
    headers = get_cf_headers()
    res = requests.post(url, headers=headers)
    if res.status_code != 200:
        logger.error(f"Failed to create track: {res.text}")
        return {"error": "Failed to create track"}
    return res.json()


class RoomConfigRequest(BaseModel):
    mode: str = Field(..., description="Mode of the room configuration")
    api_extra_params: Dict[str,str] = Field(
        {},
        description="Extra parameters to be passed to the API, in JSON format",
    )


@app.post("/room/config/load")
async def load_room_config(body: RoomConfigRequest = Body()):
    """Load a room configuration with mode and api_extra_params from the request body."""

    ice_servers = await get_ice_server()
    feedback_enabled = bool(
        os.getenv('FEEDBACK_URL') and
        os.getenv('FEEDBACK_QUEUE') and
        os.getenv('FEEDBACK_STORAGE')
    )
    max_webcam_framerate = os.getenv('MAX_WEBCAM_FRAMERATE')
    if not max_webcam_framerate is None:
        max_webcam_framerate = int(max_webcam_framerate)
    max_webcam_bitrate = os.getenv('MAX_WEBCAM_BITRATE')
    if not max_webcam_bitrate is None:
        max_webcam_bitrate = int(max_webcam_bitrate)
    max_webcam_quality_level = os.getenv('MAX_WEBCAM_QUALITY_LEVEL')
    max_api_history = os.getenv('MAX_API_HISTORY')
    if not max_webcam_quality_level is None:
        max_webcam_quality_level = int(max_webcam_quality_level)
    if not max_api_history is None:
        max_api_history = int(max_api_history)
    return {
        'mode': body.mode,
        'userDirectoryUrl': os.getenv('USER_DIRECTORY_URL'),
        'traceLink': os.getenv('TRACE_LINK'),
        'apiExtraParams': body.api_extra_params,
        'iceServers': ice_servers,
        'feedbackEnabled': feedback_enabled,
        'maxWebcamFramerate': max_webcam_framerate,
        'maxWebcamBitrate': max_webcam_bitrate,
        'maxWebcamQualityLevel': max_webcam_quality_level,
        'maxApiHistory': max_api_history,
    }
