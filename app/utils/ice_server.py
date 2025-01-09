import os
import requests
import json

async def get_ice_server():
    turn_service_id = os.getenv("TURN_SERVICE_ID")
    turn_service_token = os.getenv("TURN_SERVICE_TOKEN")
    if turn_service_token is None:
        return None
    if turn_service_id is None:
        return None
    url = f'https://rtc.live.cloudflare.com/v1/turn/keys/{turn_service_id}/credentials/generate'
    headers = {
        "Authorization": f"Bearer {turn_service_token}",
        "Content-Type": "application/json"
    }
    data = {
        "ttl": 86400
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    response.raise_for_status()  # 检查请求是否成功
    result = response.json()
    return [result['iceServers']]