from typing import Optional, List

from app import schemas, models, database

from fastapi import APIRouter, Depends, HTTPException, Body, Query, Header
from sqlalchemy.orm import Session
from passlib.hash import bcrypt


router = APIRouter(prefix="/api/designers", tags=["designers"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.DesignerRead])
def get_all_designers_for_shop(
    shop_id: str,
    id: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(models.Designer, models.User).join(models.User, models.Designer.id == models.User.id)
    query = query.filter(models.Designer.belonging_shop_id == shop_id)
    if id:
        query = query.filter(models.Designer.id == id)
    results = query.all()
    designers = []
    for designer, user in results:
        designers.append({
            "id": user.id,
            "user_name": user.name,
            "user_phone_number": user.phone_number,
            "belonging_shop_id": designer.belonging_shop_id,
            "is_active": designer.is_active,
            "created_time": designer.created_time,
            "memo": designer.memo
        })
    return designers

@router.get("/{designer_id}")
def get_designer(
    designer_id: str,
    shop_id: str = Query(None),
    db: Session = Depends(get_db),
    x_user_id: str = Header(...),
    x_user_type: str = Header(...)
):
    user = db.query(models.User).filter(models.User.id == designer_id, models.User.user_type == "designer").first()
    if not user:
        raise HTTPException(status_code=404, detail="Designer user not found")
    designer = db.query(models.Designer).filter(models.Designer.id == designer_id).first()
    if not designer:
        raise HTTPException(status_code=404, detail="Designer not found")

    # 소속 샵이 있는 경우: shop_id 필수, 해당 샵 매니저만 조회 가능
    if designer.belonging_shop_id:
        if not shop_id:
            raise HTTPException(status_code=403, detail="shop_manager_id 쿼리 파라미터가 필요합니다.")
        # shop_id 실제 샵 매니저인지 검증 (user_type == 'shop')
        shop_manager = db.query(models.User).filter(
            models.User.id == shop_id,
            models.User.user_type == "shop"
        ).first()
        if not shop_manager:
            raise HTTPException(status_code=403, detail="유효하지 않은 샵 매니저입니다.")
        # 디자이너의 소속 샵과 shop_id 일치해야 함
        if designer.belonging_shop_id != shop_id:
            raise HTTPException(status_code=403, detail="해당 샵의 디자이너가 아닙니다.")

        return {
            "id": user.id,
            "user_name": user.name,
            "user_phone_number": user.phone_number,
            "belonging_shop_id": designer.belonging_shop_id,
            "is_active": designer.is_active,
            "created_time": designer.created_time,
            "memo": designer.memo
        }
    else:
        # 소속 샵이 없는 경우: 본인만 조회 가능
        if x_user_type != "designer" or x_user_id != designer_id:
            raise HTTPException(status_code=403, detail="본인만 조회할 수 있습니다.")
        return {
            "id": user.id,
            "user_name": user.name,
            "user_phone_number": user.phone_number,
            "belonging_shop_id": designer.belonging_shop_id,
            "is_active": designer.is_active,
            "created_time": designer.created_time,
            "memo": designer.memo
        }

@router.post("/", response_model=schemas.DesignerCreateResponse)
def create_designer_for_shop(
    data: schemas.DesignerCreate = Body(...),
    db: Session = Depends(get_db),
    x_user_id: str = Header(...),
    x_user_type: str = Header(...)
):
    # Only shop manager can create designer for their own shop
    if x_user_type != "shop":
        raise HTTPException(status_code=403, detail="Only shop managers can create designer accounts.")
    # belonging_shop_id must match shop manager's id
    if not data.belonging_shop_id or data.belonging_shop_id != x_user_id:
        raise HTTPException(status_code=403, detail="belonging_shop_id must match your shop id.")
    # Check duplicate id
    if db.query(models.User).filter(models.User.id == data.id).first():
        raise HTTPException(status_code=409, detail="User ID is already taken.")
    # Check duplicate phone
    if db.query(models.User).filter(models.User.phone_number == data.user_phone_number).first():
        raise HTTPException(status_code=409, detail="이미 가입된 전화번호입니다.")
    # Create user
    hashed_pw = bcrypt.hash(data.user_password)
    db_user = models.User(
        id=data.id,
        name=data.user_name,
        hashed_password=hashed_pw,
        phone_number=data.user_phone_number,
        user_type="designer"
    )
    db.add(db_user)
    db.flush()
    # Create designer
    db_designer = models.Designer(
        id=data.id,
        name=data.user_name,
        belonging_shop_id=data.belonging_shop_id,
        is_active=True if data.is_active is None else data.is_active,
        memo=data.memo
    )
    db.add(db_designer)
    db.commit()
    db.refresh(db_designer)
    return schemas.DesignerCreateResponse(
        id=db_user.id,
        user_name=db_user.name,
        user_phone_number=db_user.phone_number,
        belonging_shop_id=db_designer.belonging_shop_id,
        is_active=db_designer.is_active,
        memo=db_designer.memo
    )

@router.patch("/{designer_id}")
def update_designer_for_shop(
    designer_id: str,
    shop_id: Optional[str] = Query(None),
    data: schemas.DesignerUpdate = Body(...),
    db: Session = Depends(get_db),
    x_user_id: str = Header(...),
    x_user_type: str = Header(...)
):
    designer = db.query(models.Designer).filter(
        models.Designer.id == designer_id
    )
    if shop_id is not None:
        designer = designer.filter(models.Designer.belonging_shop_id == shop_id)
    designer = designer.first()
    if not designer:
        raise HTTPException(status_code=404, detail="Designer not found or does not belong to this shop")
    user = db.query(models.User).filter(models.User.id == designer_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated = False
    # 권한 체크 및 필드별 분기
    if designer.belonging_shop_id:
        if x_user_type == "shop" and x_user_id == designer.belonging_shop_id:
            # 샵 매니저: 모든 필드 수정 가능
            if data.user_password is not None:
                user.hashed_password = bcrypt.hash(data.user_password)
                updated = True
            if data.user_name is not None:
                user.name = data.user_name
                designer.name = data.user_name
                updated = True
            if data.user_phone_number is not None:
                user.phone_number = data.user_phone_number
                updated = True
            if data.is_active is not None:
                designer.is_active = data.is_active
                updated = True
            if data.memo is not None:
                designer.memo = data.memo
                updated = True
        elif x_user_type == "designer" and x_user_id == designer_id:
            # 본인 디자이너: 이름/폰번호만 수정 가능
            if data.user_name is not None:
                user.name = data.user_name
                designer.name = data.user_name
                updated = True
            if data.user_phone_number is not None:
                user.phone_number = data.user_phone_number
                updated = True
            if any([
                data.user_password is not None,
                data.is_active is not None,
                data.memo is not None
            ]):
                raise HTTPException(status_code=400, detail="본인은 이름/전화번호만 수정할 수 있습니다.")
        else:
            raise HTTPException(status_code=403, detail="해당 샵 매니저 또는 본인만 수정할 수 있습니다.")
    else:
        # 개인 디자이너: 본인만 모든 필드 수정 가능
        if x_user_type == "designer" and x_user_id == designer_id:
            if data.user_password is not None:
                user.hashed_password = bcrypt.hash(data.user_password)
                updated = True
            if data.user_name is not None:
                user.name = data.user_name
                designer.name = data.user_name
                updated = True
            if data.user_phone_number is not None:
                user.phone_number = data.user_phone_number
                updated = True
            if data.is_active is not None:
                designer.is_active = data.is_active
                updated = True
            if data.memo is not None:
                designer.memo = data.memo
                updated = True
        else:
            raise HTTPException(status_code=403, detail="본인만 수정할 수 있습니다.")
    if not updated:
        raise HTTPException(status_code=400, detail="수정할 필드가 없습니다.")
    db.commit()
    return {"message": "Designer info updated successfully"}
