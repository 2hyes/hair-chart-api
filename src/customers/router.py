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


@router.get("/{customer_id}", response_model=schemas.CustomerRead)
def get_customer_detail(
    customer_id: str,
    db: Session = Depends(get_db),
    x_user_id: str = Header(...),
    x_user_type: str = Header(...)
):
    # 1. 고객 존재 확인
    customer = db.query(models.User).filter(
        models.User.id == customer_id,
        models.User.user_type == "customer"
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="고객을 찾을 수 없습니다.")
    # 2. 권한 체크
    if x_user_type == "shop":
        # 샵 소속 디자이너 중 한 명이라도 이 고객과 매핑되어 있으면 허용
        designers = db.query(models.Designer.id).filter(models.Designer.belonging_shop_id == x_user_id).all()
        designer_ids = [d.id for d in designers]
        exists = db.query(models.CustomerDesignerMapping).filter(
            models.CustomerDesignerMapping.customer_id == customer_id,
            models.CustomerDesignerMapping.designer_id.in_(designer_ids),
            models.CustomerDesignerMapping.status == "accepted"
        ).first()
        if not exists:
            raise HTTPException(status_code=403, detail="해당 고객에 접근할 권한이 없습니다.")
    elif x_user_type == "designer":
        # 본인에게 등록된 고객만 허용
        exists = db.query(models.CustomerDesignerMapping).filter(
            models.CustomerDesignerMapping.customer_id == customer_id,
            models.CustomerDesignerMapping.designer_id == x_user_id,
            models.CustomerDesignerMapping.status == "accepted"
        ).first()
        if not exists:
            raise HTTPException(status_code=403, detail="해당 고객에 접근할 권한이 없습니다.")
    else:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    return schemas.CustomerRead(
        id=customer.id,
        user_name=customer.name,
        user_phone_number=customer.phone_number
    )


@router.patch("/{customer_id}/designers/{designer_id}/response")
def respond_designer_request(
    customer_id: str,
    designer_id: str,
    body: schemas.DesignerRequestResponse = Body(...),
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

