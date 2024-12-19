from app import app
import requests
import os
from app.model.room import create_room as create_room_db
from loguru import logger

def get_cf_headers():
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+os.getenv('APP_TOKEN')
    }
    return headers


@app.post('/room/create')
async def create_room():
    """Create a new room."""
    app_id = os.getenv('APP_ID')
    
    url = f'https://rtc.live.cloudflare.com/apps/{app_id}/sessions/new'
    headers = get_cf_headers()
    res = requests.post(url, headers=headers)
    if res.status_code != 201:
        logger.error(f'Failed to create room: {res.text}')
        return {'error': 'Failed to create room'}
    data = res.json()
    session_id = data['sessionId']
    await create_room_db(session_id)
    return res.json()