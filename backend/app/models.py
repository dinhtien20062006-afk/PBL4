from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class TrafficLog(Base):
    __tablename__ = "traffic_logs" # Cập nhật tên bảng
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_ip = Column(String(45), index=True)
    dest_ip = Column(String(45))
    port = Column(Integer)
    protocol = Column(String(20))
    packet_size = Column(Integer)
    status = Column(String(50), default="Normal")

class BlockedIP(Base):
    __tablename__ = "blocked_ips" # Cập nhật tên bảng
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, nullable=True)
    ip_address = Column(String(45), unique=True, index=True)
    reason = Column(String(255))
    blocked_at = Column(DateTime, default=datetime.utcnow)
    unblocked_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="Blocked")