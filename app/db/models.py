from .base import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from datetime import datetime


class Room(Base):
    __tablename__ = "rooms"

    id = Column(
        BigInteger, primary_key=True, autoincrement=True, index=True, comment="直播间id"
    )
    room_type = Column(
        Integer, nullable=False, default=1, comment="房间类型：1-直播，2-会议"
    )
    title = Column(String(255), nullable=False, comment="房间标题")
    cover_url = Column(String(500), nullable=True, comment="封面图片URL")
    status = Column(Integer, default=0, comment="状态：0-未开播，1-直播中，2-已结束")
    platform = Column(String(50), nullable=False, comment="平台")
    description = Column(Text, nullable=True, comment="房间描述")
    streamer_name = Column(String(100), nullable=False, comment="主播/主持人名称")
    viewer_count = Column(Integer, default=0, comment="观看/参与人数")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), comment="更新时间"
    )
    last_live_time = Column(
        DateTime(timezone=True), nullable=True, comment="最后直播/会议时间"
    )

    @classmethod
    def create_room(cls, room_name):
        room = cls()
        room.title = room_name
        room.status = 0
        room.created_at = func.now()
        room.room_type = 1
        room.cover_url = ""
        room.description = ""
        room.streamer_name = ""
        room.viewer_count = 0
        room.last_live_time = func.now()
        room.platform = "Cloudflare Calls"
        room.updated_at = func.now()
        return room


class RoomSessionMapping(Base):
    __tablename__ = "room_session_mappings"

    id = Column(
        BigInteger, primary_key=True, autoincrement=True, index=True, comment="映射ID"
    )
    room_id = Column(
        BigInteger, ForeignKey("rooms.id"), nullable=False, comment="房间ID"
    )
    session_id = Column(
        String(255), nullable=False, unique=True, comment="Cloudflare Calls session ID"
    )
    sdp = Column(Text, nullable=True, comment="SDP 信息")
    session_type = Column(String(50), nullable=True, comment="会话类型")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )

    @staticmethod
    def create_room_session_mapping(room_id, session_id):
        room_session_mapping = RoomSessionMapping()
        room_session_mapping.room_id = room_id
        room_session_mapping.session_id = session_id
        room_session_mapping.created_at = func.now()
        room_session_mapping.sdp = ""
        room_session_mapping.session_type = ""
        return room_session_mapping


class SessionTrackMapping(Base):
    __tablename__ = "session_track_mappings"

    id = Column(
        BigInteger, primary_key=True, autoincrement=True, index=True, comment="映射ID"
    )
    session_id = Column(
        BigInteger,
        ForeignKey("room_session_mappings.id"),
        nullable=False,
        comment="会话ID",
    )
    track_name = Column(String(255), nullable=False, comment="轨道名称")
    location = Column(String(50), nullable=False, comment="轨道位置")
    mid = Column(String(50), nullable=False, comment="媒体标识符")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), comment="创建时间"
    )
    closed_at = Column(DateTime(timezone=True), nullable=True, comment="关闭时间")

    __table_args__ = (
        UniqueConstraint("session_id", "track_name", name="uix_session_track"),
    )
