from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import DetectionRule

router = APIRouter(prefix="/api/config", tags=["Configuration"])

# Schema quy định cấu trúc dữ liệu khi gửi PUT request lên
class ThresholdUpdate(BaseModel):
    rule_name: Optional[str] = None
    match_pattern: Optional[str] = None
    is_active: Optional[bool] = None

@router.get("/thresholds")
def get_thresholds(db: Session = Depends(get_db)):
    """Lấy danh sách các cấu hình ngưỡng hiện tại (VD: giới hạn đăng nhập sai, packet SYN/s)"""
    rules = db.query(DetectionRule).all()
    return {"status": "success", "total": len(rules), "data": rules}

@router.put("/thresholds/{rule_id}")
def update_threshold(rule_id: int, payload: ThresholdUpdate, db: Session = Depends(get_db)):
    """Cập nhật các thông số cấu hình ngưỡng chống tấn công"""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Không tìm thấy cấu hình với ID này")
    
    # Cập nhật linh hoạt các trường có dữ liệu gửi lên
    if payload.rule_name is not None:
        rule.rule_name = payload.rule_name
    if payload.match_pattern is not None:
        rule.match_pattern = payload.match_pattern
    if payload.is_active is not None:
        rule.is_active = payload.is_active
        
    db.commit()
    db.refresh(rule)
    return {"status": "success", "message": f"Đã cập nhật cấu hình ngưỡng ID {rule_id}", "data": rule}