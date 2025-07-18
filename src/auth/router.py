from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models, database
from passlib.hash import bcrypt

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="존재하지 않는 계정입니다.")
    if user.user_type != request.user_type:
        raise HTTPException(status_code=403, detail="해당 타입으로 가입된 아이디가 아닙니다.")
    if not bcrypt.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    belonging_shop_id = None
    if user.user_type == "designer":
        designer = db.query(models.Designer).filter(models.Designer.id == user.id).first()
        if designer:
            belonging_shop_id = designer.belonging_shop_id
    return {
        "message": "로그인 성공",
        "user_id": user.id,
        "user_name": user.name,
        "user_type": user.user_type,
        "belonging_shop_id": belonging_shop_id
    } 
