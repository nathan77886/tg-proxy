from app.db import get_session, Room, RoomSessionMapping
import random
import string
from datetime import datetime
import json
from loguru import logger
from fastapi import WebSocket


async def create_room(session_id, room_name=""):
    if room_name == "":
        ## 随机8位字符串
        room_name = "".join(random.sample(string.ascii_letters + string.digits, 8))
    with get_session() as session:
        room = (
            session.query(RoomSessionMapping)
            .filter(RoomSessionMapping.session_id == session_id)
            .first()
        )
        if room is None:
            ## 创建房间和映射
            room = Room.create_room(room_name)
            session.add(room)
            session.commit()
            room_session_mapping = RoomSessionMapping.create_room_session_mapping(
                room.id, session_id
            )
            session.add(room_session_mapping)
            session.commit()
        return room.id,room.room_name


async def get_room(room_name):
    with get_session() as session:
        room = session.query(Room).filter(Room.room_name == room_name).first()
        return room


async def get_room_session(room_name):
    with get_session() as session:
        room = session.query(Room).filter(Room.room_name == room_name).first()
        if room is None:
            return None
        room_session_mapping = (
            session.query(RoomSessionMapping)
            .filter(RoomSessionMapping.room_id == room.id)
            .first()
        )
        return room_session_mapping.session_id


room_user2connects: dict[str, WebSocket] = {}

def set_room_user_connect(conn_id, ws_conn):
    room_user2connects[conn_id] = ws_conn

async def create_user_connect(conn_id, user_name, room_name):
    from app.db.redis import redis_conn, expire_time_7_day

    user = redis_conn.get(f"tgproxy:session-{conn_id}")
    if user == None:
        new_user_session = {
            "id": conn_id,
            "name": user_name,
            "room_name": room_name,
            "joined": False,
            "raisedHand": False,
            "speaking": False,
            "tracks": {
                "audioEnabled": False,
                "videoEnabled": False,
                "screenShareEnabled": False,
            },
        }
        redis_conn.set(
            f"tgproxy:heartbeat:${conn_id}",
            datetime.now().timestamp(),
            expire_time_7_day,
        )
        redis_conn.set(
            f"tgproxy:session:{conn_id}",
            json.dumps(new_user_session),
            expire_time_7_day,
        )
        room2conn_rkey = f"tgproxy:room:session:{room_name}"
        redis_conn.hset(room2conn_rkey, conn_id, json.dumps(new_user_session))
        redis_conn.expire(room2conn_rkey, expire_time_7_day)
        await broadcast_room_state(room_name)


async def on_websocket_disconnect(conn_id, room_name):
    from app.db.redis import redis_conn

    redis_conn.delete(f"tgproxy:session:{conn_id}")
    redis_conn.delete(f"tgproxy:heartbeat:${conn_id}")
    room2conn_rkey = f"tgproxy:room:session:{room_name}"
    redis_conn.hdel(room2conn_rkey, conn_id)
    del room_user2connects[conn_id]
    await broadcast_room_state(room_name)
    logger.info(f"{conn_id} 断开连接,roomer:{room_name}")


async def broadcast_room_state(room_name):
    from app.db.redis import redis_conn

    room2conn_rkey = f"tgproxy:room:session:{room_name}"
    room_users = redis_conn.hgetall(room2conn_rkey)
    did_someone_quit = False
    room_state = {
        "type": "roomState",
        "state": {
            "meetingId": room_name,
            "users": [],
        },
    }
    for cid, user_state in room_users.items():
        room_state["state"]["users"].append(json.loads(user_state))
        conn_id = cid.decode()
        if conn_id in room_user2connects:
            ws_conn = room_user2connects[conn_id]
            try:
                await ws_conn.send_json(room_state)
            except Exception as e:
                ws_conn.close(1011)
                logger.error(f"{conn_id} 断开连接,roomer:{room_name},err:{e}")
                did_someone_quit = True
                redis_conn.hdel(room2conn_rkey, conn_id)
                redis_conn.delete(f"tgproxy:session:{conn_id}")
        else:
            logger.error(f"{conn_id} 链接不存在,roomer:{room_name}")
            redis_conn.hdel(room2conn_rkey, conn_id)
            redis_conn.delete(f"tgproxy:session:{conn_id}")
            did_someone_quit = True
    if did_someone_quit:
        await broadcast_room_state(room_name)


async def on_room_message(conn_id, room_name, message):
    from app.db.redis import redis_conn, expire_time_7_day

    msg_type = message["type"]
    if msg_type == "userLeft":
        if conn_id in room_user2connects:
            room_user2connects[conn_id].close(1000)
        await on_websocket_disconnect(conn_id, room_name)
        return
    if msg_type == "userUpdate":
        user_data = message["data"]
        user_data["room_name"] = room_name
        redis_conn.set(
            f"tgproxy:session:{conn_id}",
            json.dumps(user_data),
            expire_time_7_day,
        )
        room2conn_rkey = f"tgproxy:room:session:{room_name}"
        redis_conn.hset(room2conn_rkey, conn_id, json.dumps(user_data))
        redis_conn.expire(room2conn_rkey, expire_time_7_day)
        await broadcast_room_state(room_name)
        return
    if msg_type == "directMessage":
        to_user_conn_id = message["to"]
        message = message["message"]
        from_user = redis_conn.get(f"tgproxy:session:{conn_id}")
        for conn_id, ws_conn in room_user2connects.items():
            if conn_id == to_user_conn_id:
                try:
                    await ws_conn.send_json(
                        {
                            "type": "directMessage",
                            "from": from_user["name"],
                            "message": message,
                        }
                    )
                except Exception as e:
                    ws_conn.close(1011)
                    logger.error(f"{conn_id} 断开连接,roomer:{room_name},err:{e}")
    if msg_type == "muteUser":
    #     user = redis_conn.get(f"tgproxy:session:{conn_id}")
        muted_user = False
        for conn_id, ws_conn in room_user2connects.items():
            if conn_id == message["id"]:
                other_user = redis_conn.get(f"tgproxy:session:{conn_id}")
                redis_conn.set(
                    f"tgproxy:session:{conn_id}",
                    json.dumps(
                        {
                            **other_user,
                            "tracks": {
                                **other_user["tracks"],
                                "audioEnabled": False,
                            },
                        }
                    ),
                )
                await ws_conn.send_json(
                    {
                        "type": "muteMic",
                    }
                )
                muted_user = True
        if muted_user:
            await broadcast_room_state(room_name)
    if msg_type == "heartbeat":
        redis_conn.set(
            f"tgproxy:heartbeat:${conn_id}",
            datetime.now().timestamp(),
            expire_time_7_day,
        )
