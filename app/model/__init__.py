from typing import List
from fastapi import WebSocket
from loguru import logger

group_channel = {}


def set_channel(group_id, channel: WebSocket, random_id):
    g_id = str(group_id)
    global group_channel
    if not group_channel:  # type: ignore
        group_channel = {}
    if group_channel.get(g_id):
        group_channel[g_id][random_id] = channel
    else:
        group_channel[g_id] = {random_id: channel}


def remove_channel(group_id, random_id):
    g_id = str(group_id)
    global group_channel
    if not group_channel:  # type: ignore
        return
    if group_channel.get(g_id) and group_channel[g_id].get(random_id):
        del group_channel[g_id][random_id]

# 派发事件
async def dispatch(group_id, msg):
    global group_channel
    if not group_channel:  # type: ignore
        return
    g_id = str(group_id)
    channel_map = group_channel.get(g_id)
    if not channel_map:
        logger.error(f"group {g_id} not found")
        return
    for ws in channel_map.values():
        if ws.state != "connecting":
            continue
        logger.info(f"dispatch msg to {group_id}")
        try:
            await ws.send_json({"type": "text", "data": msg})
        except Exception as e:
            logger.error(e)
