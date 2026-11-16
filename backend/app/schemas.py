from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertCreate(BaseModel):
    ip_source: str
    attack_type: str
    severity: str
    threshold_value: int

class TrafficLogCreate(BaseModel):
    ip_source: str
    protocol: str
    packet_count: int
    port_target: int

class ThresholdUpdate(BaseModel):
    threshold_limit: Optional[int] = None
    time_window_seconds: Optional[int] = None
    is_active: Optional[bool] = None