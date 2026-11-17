from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import DEFAULT_THRESHOLDS
from app.database import get_db
from app.models import SystemConfig
from app.schemas import ThresholdsUpdate

router = APIRouter(prefix="/api/config", tags=["Configuration"])


def _read(db: Session) -> dict:
    values = dict(DEFAULT_THRESHOLDS)
    for row in db.query(SystemConfig).all():
        if row.config_key in values:
            values[row.config_key] = row.config_value
    return values


@router.get("/thresholds")
def get_thresholds(db: Session = Depends(get_db)):
    return {"status": "success", "data": _read(db)}


@router.put("/thresholds")
def update_thresholds(payload: ThresholdsUpdate, db: Session = Depends(get_db)):
    for key, value in payload.model_dump(exclude_none=True).items():
        row = db.get(SystemConfig, key)
        if row:
            row.config_value = value
        else:
            db.add(SystemConfig(config_key=key, config_value=value))
    db.commit()
    return {"status": "success", "message": "Đã lưu cấu hình", "data": _read(db)}
