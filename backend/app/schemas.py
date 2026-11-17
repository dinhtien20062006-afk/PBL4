"""Payload request (validate bằng Pydantic)."""
import ipaddress
from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _clean_ip(value: str) -> str:
    return str(ipaddress.ip_address(value.strip()))


class AlertCreate(BaseModel):
    ip_source: str
    attack_type: str = Field(min_length=1, max_length=50)
    severity: str = "High"
    threshold_value: int = 0

    @field_validator("ip_source")
    @classmethod
    def _ip(cls, v: str) -> str:
        return _clean_ip(v)


class TrafficLogCreate(BaseModel):
    ip_source: str
    packet_count: int = Field(ge=0)
    port_target: int = Field(ge=0, le=65535)
    protocol: str = "TCP"


class TrafficBatch(BaseModel):
    items: list[TrafficLogCreate]


class IpRequest(BaseModel):
    ip_address: str

    @field_validator("ip_address")
    @classmethod
    def _ip(cls, v: str) -> str:
        return _clean_ip(v)


class BlockRequest(IpRequest):
    reason: Optional[str] = None
    alert_id: Optional[int] = None  # frontend gửi kèm khi chặn từ một cảnh báo


class AttackStartRequest(BaseModel):
    """Tham số tuỳ chọn khi bấm nút Bắt đầu ở Attack Lab — bỏ trống để dùng giá trị mặc định (.env)."""

    target_ip: Optional[str] = None
    port: Optional[int] = Field(default=None, ge=1, le=65535)
    valid_email: Optional[str] = None
    delay: Optional[float] = Field(default=None, gt=0)
    max_attempts: Optional[int] = Field(default=None, ge=1)
    packets_per_sec: Optional[int] = Field(default=None, ge=1)

    @field_validator("target_ip")
    @classmethod
    def _target_ip(cls, v: Optional[str]) -> Optional[str]:
        return _clean_ip(v) if v else v


class ThresholdsUpdate(BaseModel):
    spam_per_minute: Optional[int] = Field(default=None, ge=1)
    brute_force_attempts: Optional[int] = Field(default=None, ge=1)
    syn_packets_per_second: Optional[int] = Field(default=None, ge=1)
    block_duration_seconds: Optional[int] = Field(default=None, ge=1)
