from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AttackThreshold
from app.schemas import ThresholdUpdate

router = APIRouter(prefix="/api/config", tags=["Configuration"])

@router.get("/thresholds")
def get_thresholds(db: Session = Depends(get_db)):
    """Lấy danh sách các ngưỡng hiện tại để hiển thị lên bảng điều khiển"""
    thresholds = db.query(AttackThreshold).all()
    return {"status": "success", "total": len(thresholds), "data": thresholds}

@router.put("/thresholds/{threshold_id}")
def update_threshold(threshold_id: int, payload: ThresholdUpdate, db: Session = Depends(get_db)):
    """Cập nhật linh hoạt các thông số ngưỡng từ giao diện Web"""
    threshold = db.query(AttackThreshold).filter(AttackThreshold.id == threshold_id).first()
    
    if not threshold:
        raise HTTPException(status_code=404, detail="Không tìm thấy cấu hình với ID này")
    
    # Chỉ cập nhật những trường mà người dùng gửi lên
    if payload.threshold_limit is not None:
        threshold.threshold_limit = payload.threshold_limit
    if payload.time_window_seconds is not None:
        threshold.time_window_seconds = payload.time_window_seconds
    if payload.is_active is not None:
        threshold.is_active = payload.is_active
        
    db.commit()
    db.refresh(threshold)
    return {"status": "success", "message": f"Đã cập nhật ngưỡng cho {threshold.attack_type}", "data": threshold}