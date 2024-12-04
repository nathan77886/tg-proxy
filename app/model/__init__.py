from typing import List
from fastapi import WebSocket


group_channel = {}


def set_channel(group_id, channel: WebSocket):
    g_id = str(group_id)
    global group_channel
    if not group_channel:  # type: ignore
        group_channel = {}
    if group_channel.get(g_id):
        group_channel[g_id].append(channel)
    else:
        group_channel[g_id] = [channel]


def get_channel(group_id) -> List[WebSocket]:
    global group_channel
    if not group_channel:  # type: ignore
        return []
    g_id = str(group_id)
    return group_channel.get(g_id)