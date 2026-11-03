from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertCreate(BaseModel):
    rule_id: Optional[int] = None
    traffic_log_id: Optional[int] = None
    attack_type: str
    source_ip: str
    severity: str = "High"

class TrafficLogCreate(BaseModel):
    source_ip: str
    dest_ip: str
    port: int
    protocol: str
    packet_size: int
    status: str = "Normal"