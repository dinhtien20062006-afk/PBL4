from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, SmallInteger, Boolean
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='admin')
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class LogTraffic(Base):
    __tablename__ = "logs_traffic"
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    ip_source = Column(String(45), nullable=False, index=True)
    protocol = Column(String(10), nullable=False)
    packet_count = Column(Integer, nullable=False)
    port_target = Column(SmallInteger, nullable=False)

class BlacklistIP(Base):
    __tablename__ = "blacklist_ips"
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False)
    reason_blocked = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status_active = Column(Boolean, default=True)
    # Ghi chú: SQLAlchemy không hỗ trợ tạo Composite Index trực tiếp trên Column definitions
    # một cách đơn giản cho MySQL TINYINT(1) / Boolean. Nên tạo trực tiếp trong SQL.

class AlertHistory(Base):
    __tablename__ = "alert_history"
    id = Column(Integer, primary_key=True, index=True)
    ip_source = Column(String(45), nullable=False)
    attack_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    threshold_value = Column(Integer, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)