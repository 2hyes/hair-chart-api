import re
from typing import List, Optional

from app import models, schemas, database
from src.auth.router import router as auth_router
from src.user.router import router as user_router
from src.chart_option.router import router as chart_option_router
from src.designers.router import router as designers_router

from fastapi import FastAPI, Depends, HTTPException, Body, Query, Header
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
# from jose import jwt

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chart_option_router)
app.include_router(designers_router)

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 임시 current_user Dependency (실제 서비스에서는 JWT에서 파싱)
def get_current_user(
    x_user_id: str = Header(...), 
    x_user_type: str = Header(...)
):
    return {"user_id": x_user_id, "user_type": x_user_type}

# TODO: refactor whole main.py

@app.get("/shops/{shop_id}/customers", response_model=List[schemas.CustomerDesignerMappingRead])
def get_customers_for_shop(shop_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 샵 관리자 권한 체크 필요
    pass

@app.get("/designers/{designer_id}/customers", response_model=List[schemas.CustomerDesignerMappingRead])
def get_customers_for_designer(designer_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 디자이너 본인 권한 체크 필요
    pass

@app.post("/designers/{designer_id}/customers/request", response_model=schemas.CustomerDesignerMappingRead)
def request_customer_registration(designer_id: str, req: schemas.CustomerDesignerMappingCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 1. 디자이너 본인 권한 체크
    if current_user["user_type"] != "designer" or current_user["user_id"] != designer_id:
        raise HTTPException(status_code=403, detail="본인 디자이너만 고객 등록 요청이 가능합니다.")

    # 2. 중복 체크 (customer_id, designer_id 조합)
    existing = db.query(models.CustomerDesignerMapping).filter_by(
        customer_id=req.customer_id,
        designer_id=designer_id
    ).first()
    if existing:
        if existing.status == "pending":
            raise HTTPException(status_code=400, detail="이미 등록 요청이 대기 중입니다.")
        elif existing.status == "accepted":
            raise HTTPException(status_code=400, detail="이미 등록된 고객입니다.")
        elif existing.status == "rejected":
            raise HTTPException(status_code=400, detail="이전에 거절된 요청이 있습니다. 관리자에게 문의하세요.")
        else:
            raise HTTPException(status_code=400, detail=f"이미 요청이 존재합니다. (status={existing.status})")

    # 3. 매핑 생성
    mapping = models.CustomerDesignerMapping(
        customer_id=req.customer_id,
        designer_id=designer_id,
        status="pending",
        requested_by=designer_id,
        memo=req.memo
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return mapping

@app.patch("/customers/{customer_id}/designer-requests/{mapping_id}", response_model=schemas.CustomerDesignerMappingRead)
def update_customer_registration_status(customer_id: str, mapping_id: int, req: schemas.CustomerDesignerMappingUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 고객 본인 권한 체크, status 변경
    pass

@app.get("/customers/{customer_id}/detail")
def get_customer_detail(customer_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # 본인/권한자 체크, 고객+디자이너+차트이력 등 반환
    pass
