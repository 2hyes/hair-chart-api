from fastapi import APIRouter, Depends, HTTPException, Body, Query, Header
from sqlalchemy.orm import Session
from app import schemas, models, database
from passlib.hash import bcrypt
from typing import List

router = APIRouter(prefix="/api/users", tags=["user"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    x_user_id: str = Header(...), 
    x_user_type: str = Header(...)
):
    return {"user_id": x_user_id, "user_type": x_user_type}

@router.post("/signup")
def signup(data: dict = Body(...), db: Session = Depends(get_db)):
    user_type = data.get("user_type")
    if user_type not in ["customer", "shop", "designer"]:
        raise HTTPException(status_code=400, detail="Invalid user_type.")
    # Validate duplicate IDs
    existing_user = db.query(models.User).filter(models.User.id == data["id"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID is already taken.")
    existing_phone = db.query(models.User).filter(models.User.phone_number == data["user_phone_number"]).first()
    if existing_phone:
        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
    # Hash password
    hashed_pw = bcrypt.hash(data["user_password"])
    db_user = models.User(
        id=data["id"],
        name=data["user_name"],
        hashed_password=hashed_pw,
        phone_number=data["user_phone_number"],
        user_type=user_type
    )
    db.add(db_user)
    db.flush()
    if user_type == "customer":
        db.commit()
        db.refresh(db_user)
        return {
            "id": db_user.id,
            "user_name": db_user.name,
            "user_phone_number": db_user.phone_number
        }
    elif user_type == "shop":
        db_shop = models.Shop(
            id=data["id"],
            name=data["shop_name"],
            number=data["shop_number"],
            biz_number=data["shop_biz_number"]
        )
        db.add(db_shop)
        db.commit()
        db.refresh(db_shop)
        return {
            "id": db_user.id,
            "user_name": db_user.name,
            "user_phone_number": db_user.phone_number,
            "shop_name": db_shop.name,
            "shop_number": db_shop.number,
            "shop_biz_number": db_shop.biz_number
        }
    elif user_type == "designer":
        db_designer = models.Designer(
            id=data["id"],
            name=data["user_name"],
            belonging_shop_id=data.get("belonging_shop_id"),
            memo=data.get("memo")
        )
        db.add(db_designer)
        db.commit()
        db.refresh(db_designer)
        return {
            "id": db_user.id,
            "user_name": db_user.name,
            "user_phone_number": db_user.phone_number,
            "belonging_shop_id": db_designer.belonging_shop_id,
            "is_active": db_designer.is_active,
            "memo": db_designer.memo
        } 

@router.patch("/{user_id}")
def update_user_info(
    user_id: str, 
    data: dict = Body(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    designer = None
    if user.user_type == "designer":
        designer = db.query(models.Designer).filter(models.Designer.id == user_id).first()
        if not designer:
            raise HTTPException(status_code=404, detail="Designer not found")
    # 권한 분기 (기존 main.py와 동일)
    if user.user_type == "designer":
        designer = db.query(models.Designer).filter(models.Designer.id == user_id).first()
        if not designer:
            raise HTTPException(status_code=404, detail="Designer not found")
        has_shop = bool(designer.belonging_shop_id)
        if has_shop:
            if current_user["user_type"] == "shop":
                allowed = False
                if "user_password" in data:
                    user.hashed_password = bcrypt.hash(data["user_password"])
                    allowed = True
                if "user_name" in data:
                    user.name = data["user_name"]
                    designer.name = data["user_name"]
                    allowed = True
                if "user_phone_number" in data:
                    # 중복 체크 (본인 제외)
                    existing = db.query(models.User).filter(
                        models.User.phone_number == data["user_phone_number"],
                        models.User.id != user_id
                    ).first()
                    if existing:
                        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
                    user.phone_number = data["user_phone_number"]
                    allowed = True
                if "is_active" in data:
                    designer.is_active = data["is_active"]
                    allowed = True
                if "memo" in data:
                    designer.memo = data["memo"]
                    allowed = True
                if not allowed:
                    raise HTTPException(status_code=400, detail="수정할 필드가 없습니다.")
            elif current_user["user_type"] == "designer" and current_user["user_id"] == user_id:
                for key in data:
                    if key not in ["user_name", "user_phone_number"]:
                        raise HTTPException(status_code=400, detail="샵 소속 디자이너는 이름/전화번호만 수정할 수 있습니다.")
                allowed = False
                if "user_name" in data:
                    user.name = data["user_name"]
                    designer.name = data["user_name"]
                    allowed = True
                if "user_phone_number" in data:
                    existing = db.query(models.User).filter(
                        models.User.phone_number == data["user_phone_number"],
                        models.User.id != user_id
                    ).first()
                    if existing:
                        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
                    user.phone_number = data["user_phone_number"]
                    allowed = True
                if not allowed:
                    raise HTTPException(status_code=400, detail="수정할 필드가 없습니다.")
            else:
                raise HTTPException(status_code=403, detail="권한이 없습니다.")
        else:
            if current_user["user_type"] == "designer" and current_user["user_id"] == user_id:
                allowed = False
                if "user_password" in data:
                    user.hashed_password = bcrypt.hash(data["user_password"])
                    allowed = True
                if "user_name" in data:
                    user.name = data["user_name"]
                    designer.name = data["user_name"]
                    allowed = True
                if "user_phone_number" in data:
                    existing = db.query(models.User).filter(
                        models.User.phone_number == data["user_phone_number"],
                        models.User.id != user_id
                    ).first()
                    if existing:
                        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
                    user.phone_number = data["user_phone_number"]
                    allowed = True
                if "is_active" in data:
                    designer.is_active = data["is_active"]
                    allowed = True
                if "memo" in data:
                    designer.memo = data["memo"]
                    allowed = True
                if not allowed:
                    raise HTTPException(status_code=400, detail="수정할 필드가 없습니다.")
            else:
                raise HTTPException(status_code=403, detail="권한이 없습니다.")
    elif user.user_type == "customer":
        updatable_fields = ["user_name", "user_phone_number"]
        updated = False
        for field in updatable_fields:
            if field in data:
                if field == "user_phone_number":
                    existing = db.query(models.User).filter(
                        models.User.phone_number == data["user_phone_number"],
                        models.User.id != user_id
                    ).first()
                    if existing:
                        raise HTTPException(status_code=400, detail="이미 가입된 전화번호입니다.")
                setattr(user, field, data[field])
                updated = True
        if "user_password" in data:
            user.hashed_password = bcrypt.hash(data["user_password"])
            updated = True
        if not updated:
            raise HTTPException(status_code=400, detail="수정할 필드가 없습니다.")
    else:
        raise HTTPException(status_code=400, detail="User type이 지원되지 않습니다.")
    db.commit()
    return {"message": "User info updated successfully"}

@router.get("/check-id")
def check_user_id(id: str, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.id == id).first() is not None
    return {"exists": exists}

@router.get("/customers/{user_id}")
def get_customer(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.user_type == "customer").first()
    if not user:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {
        "id": user.id,
        "user_name": user.name,
        "user_phone_number": user.phone_number
    }

@router.get("/shops/{user_id}")
def get_shop(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.user_type == "shop").first()
    if not user:
        raise HTTPException(status_code=404, detail="Shop user not found")
    shop = db.query(models.Shop).filter(models.Shop.id == user_id).first()
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return {
        "id": user.id,
        "user_name": user.name,
        "user_phone_number": user.phone_number,
        "shop_name": shop.name,
        "shop_number": shop.number,
        "shop_biz_number": shop.biz_number
    }