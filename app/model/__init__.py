from typing import List
from fastapi import WebSocket


group_channel = {}


def set_channel(group_id, channel: WebSocket):
    if group_channel.get(group_id):
        group_channel[group_id].append(channel)
    else:
        group_channel[group_id] = [channel]


def get_channel(group_id) -> List[WebSocket]:
    return group_channel.get(group_id)