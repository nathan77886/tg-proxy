from fastapi import WebSocket
from loguru import logger
from typing import Dict
from collections import defaultdict
import asyncio
import json

# 用于存储每个 group_id 的队列和连接
_message_queues: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

async def on_event_stream(group_id):
    queue = _message_queues[group_id]
    while True:
        # 从队列中获取消息并发送到客户端
        message = await queue.get()
        yield json.dumps(message)

# 派发事件
async def dispatch(group_id, msg):
    g_id = str(group_id)
    logger.info(f"dispatch msg to {g_id}")
    await _message_queues[group_id].put(msg)