from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base


class TrafficLog(Base):
    __tablename__ = "traffic_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    source_ip = Column(String(45), index=True, nullable=False)
    dest_ip = Column(String(45), nullable=False)
    port = Column(Integer)
    protocol = Column(String(20))
    packet_size = Column(Integer)
    status = Column(String(50), default="Normal")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, nullable=True)
    traffic_log_id = Column(Integer, nullable=True)
    attack_type = Column(String(100), nullable=False)
    source_ip = Column(String(45), nullable=False, index=True)
    severity = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), nullable=False, index=True)
    reason = Column(Text)
    blocked_at = Column(DateTime, default=datetime.now)
    unblocked_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="Blocked")
