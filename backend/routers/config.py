from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/config", tags=["Configuration"])

class ThresholdUpdate(BaseModel):
    rule_name: Optional[str] = None
    match_pattern: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/thresholds")
def get_thresholds():
    return {"status": "success", "total": 0, "data": []}

@router.put("/thresholds/{rule_id}")
def update_threshold(rule_id: int, payload: ThresholdUpdate):
    return {"status": "error", "message": "Tính năng quản lý Rule đã bị vô hiệu hóa."}