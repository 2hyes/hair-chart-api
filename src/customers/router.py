from typing import Optional, List

from app import schemas, models, database
from common.get_current_user import get_current_user

from fastapi import APIRouter, Depends, HTTPException, Body, status, Header
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from pydantic import BaseModel


router = APIRouter(prefix="/api/customers", tags=["customers"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.CustomerRead])
def get_mapped_customers(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["user_type"] == "shop":
        designers = db.query(models.Designer.id).filter(models.Designer.belonging_shop_id == current_user["user_id"]).all()
        designer_ids = [d.id for d in designers]
        if not designer_ids:
            return []
        mappings = db.query(models.CustomerDesignerMapping.customer_id).filter(
            models.CustomerDesignerMapping.designer_id.in_(designer_ids),
            models.CustomerDesignerMapping.status == "accepted"
        ).distinct().all()
    elif current_user["user_type"] == "designer":
        mappings = db.query(models.CustomerDesignerMapping.customer_id).filter(
            models.CustomerDesignerMapping.designer_id == current_user["user_id"],
            models.CustomerDesignerMapping.status == "accepted"
        ).distinct().all()
    else:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    customer_ids = [m.customer_id for m in mappings]
    if not customer_ids:
        return []
    customers = db.query(models.User).filter(
        models.User.id.in_(customer_ids),
        models.User.user_type == "customer"
    ).all()
    return [schemas.CustomerRead(
        id=c.id,
        user_name=c.name,
        user_phone_number=c.phone_number
    ) for c in customers]


class DesignerRequestResponse(BaseModel):
    response: str  # 'accepted' or 'rejected'

@router.patch("/{customer_id}/designers/{designer_id}/response")
def respond_designer_request(
    customer_id: str,
    designer_id: str,
    body: DesignerRequestResponse = Body(...),
    db: Session = Depends(get_db),
    x_user_id: str = Header(...),
    x_user_type: str = Header(...)
):
    # 1. 본인 고객만 응답 가능
    if x_user_type != "customer" or x_user_id != customer_id:
        raise HTTPException(status_code=403, detail="본인 고객만 응답할 수 있습니다.")
    # 2. 매핑 조회
    mapping = db.query(models.CustomerDesignerMapping).filter(
        models.CustomerDesignerMapping.customer_id == customer_id,
        models.CustomerDesignerMapping.designer_id == designer_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="매핑 요청을 찾을 수 없습니다.")
    # 3. 이미 처리된 요청은 불가
    if mapping.status == "accepted":
        raise HTTPException(status_code=400, detail="이미 승인된 요청입니다.")
    if mapping.status == "rejected":
        raise HTTPException(status_code=400, detail="이미 거절된 요청입니다.")
    if mapping.status != "pending":
        raise HTTPException(status_code=400, detail=f"응답할 수 없는 상태입니다. (status={mapping.status})")
    # 4. 응답 처리
    if body.response not in ("accepted", "rejected"):
        raise HTTPException(status_code=400, detail="response 값은 'accepted' 또는 'rejected'만 가능합니다.")
    mapping.status = body.response
    db.commit()
    db.refresh(mapping)
    return {"message": f"디자이너 등록 요청을 {body.response} 처리했습니다.", "customer_id": customer_id, "designer_id": designer_id, "status": mapping.status}

