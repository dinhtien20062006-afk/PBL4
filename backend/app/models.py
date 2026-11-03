from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
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

class DetectionRule(Base):
    __tablename__ = "detection_rules"
    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    protocol = Column(String(20), nullable=True)
    match_pattern = Column(String(255), nullable=False)
    action_type = Column(String(50), default='alert')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrafficLog(Base):
    __tablename__ = "traffic_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_ip = Column(String(45), nullable=False)
    dest_ip = Column(String(45), nullable=False)
    port = Column(Integer, nullable=True)
    protocol = Column(String(20), nullable=True)
    packet_size = Column(Integer, nullable=True)
    status = Column(String(50), nullable=True)

class MailTransaction(Base):
    __tablename__ = "mail_transactions"
    id = Column(Integer, primary_key=True, index=True)
    traffic_log_id = Column(Integer, ForeignKey("traffic_logs.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(255), nullable=True)
    receiver = Column(String(255), nullable=True)
    subject = Column(Text, nullable=True)
    has_attachment = Column(Boolean, default=False)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("detection_rules.id", ondelete="SET NULL"), nullable=True)
    traffic_log_id = Column(Integer, ForeignKey("traffic_logs.id", ondelete="CASCADE"), nullable=True)
    attack_type = Column(String(100), nullable=False)
    source_ip = Column(String(45), nullable=False)
    severity = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class BlockedIP(Base):
    __tablename__ = "blocked_ips"
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(45), nullable=False)
    reason = Column(Text, nullable=True)
    blocked_at = Column(DateTime, default=datetime.utcnow)
    unblocked_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)