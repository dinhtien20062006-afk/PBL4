from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class TrafficLog(Base):
    __tablename__ = "traffic_logs"
    id = Column(Integer, primary_key=True, index=True)
    source_ip = Column(String(45), index=True)
    dest_ip = Column(String(45))
    port = Column(Integer)
    protocol = Column(String(20))
    packet_size = Column(Integer)
    status = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("detection_rules.id", ondelete="SET NULL"))
    traffic_log_id = Column(Integer, ForeignKey("traffic_logs.id", ondelete="CASCADE"))
    attack_type = Column(String(100))
    source_ip = Column(String(45))
    severity = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)