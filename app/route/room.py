from app import app
import requests
import os
from app.model.room import create_room as create_room_db, get_room_session
from loguru import logger


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