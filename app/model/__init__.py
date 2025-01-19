import asyncio
import json
from typing import Dict, List

from loguru import logger

# 用于存储每个 group_id 对应的 SSE 客户端连接列表
_message_queues: Dict[str, List[asyncio.Queue]] = {}


async def on_event_stream(group_id):
    heatbeat = json.dumps({"heatbeat": "1"})
    yield f"data: {heatbeat}\n\n"
    g_id = str(group_id)
    message_queue = asyncio.Queue()
    if g_id not in _message_queues:
        _message_queues[g_id] = []
    _message_queues[g_id].append(message_queue)
    while True:
        # 从队列中获取消息并发送到客户端
        message = await message_queue.get_nowait()
        if message is None:
            ## 十秒后发心跳
            await asyncio.sleep(1)
            yield f"data: {heatbeat}\n\n"
            continue
        yield message


# 派发事件
async def dispatch(group_id, msg):
    g_id = str(group_id)
    logger.info(f"dispatch msg to {g_id}")
    if g_id not in _message_queues:
        return
    by = json.dumps(msg)
    steam_data = f"data: {by}\n\n"
    for message_queue in _message_queues[g_id]:
        await message_queue.put(steam_data)
