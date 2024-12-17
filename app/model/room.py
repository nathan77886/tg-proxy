from app.db import get_session, Room, RoomSessionMapping
import random
import string
from datetime import datetime

async def create_room(session_id, room_name=""):
    if room_name == "":
        ## 随机8位字符串
        room_name = "".join(random.sample(string.ascii_letters + string.digits, 8))
    session = get_session()
    room = session.query(RoomSessionMapping).filter(RoomSessionMapping.session_id == session_id).first()
    if room is None:
        ## 创建房间和映射
        room = Room.create_room(room_name)
        session.add(room)
        room_session_mapping = RoomSessionMapping.create_room_session_mapping(room.id, session_id)
        session.add(room_session_mapping)
        session.commit()
    session.close()
    return room
