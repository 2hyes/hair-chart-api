from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# TODO: password encryption
# TODO: refactor whole main.py

@app.post("/customers", response_model=schemas.CustomerRead)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.id == customer.id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User ID is already taken.")
    
    db_user = models.User(**customer.model_dump(), 
                          user_type="customer")

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/shops", response_model=schemas.ShopRead)
def create_shop(shop: schemas.ShopCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.id == shop.id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User ID already taken.")
    
    db_user = models.User(
        id=shop.id,
        name=shop.user_name,
        password=shop.user_password,
        phone_number=shop.user_phone_number,
        user_type='shop'
    )
    db.add(db_user)
    db.flush()

    db_shop = models.Shop(
        id=shop.id,
        name=shop.shop_name,
        number=shop.shop_number,
        biz_number=shop.shop_biz_number
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


@app.get("/customers/{customer_id}", response_model=schemas.CustomerRead)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).\
        filter(models.User.id == customer_id).\
        filter(models.User.user_type == "customer").\
        first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/shops/{shop_id}", response_model=schemas.ShopRead)
def get_shop(shop_id: str, db: Session = Depends(get_db)):
    result = db.query(models.Shop, models.User).\
        join(models.User, models.Shop.id == models.User.id).\
        filter(models.Shop.id == shop_id).\
        first()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop, user = result
    return {
        "id": user.id,
        "user_name": user.name,
        "user_phone_number": user.phone_number,
        "shop_name": shop.name,
        "shop_number": shop.number,
        "shop_biz_number": shop.biz_number
    } 

# @app.post("/user-hair-profile/", response_model=schemas.UserHairProfileRead)
# def create_user_hair_profile(profile: schemas.UserHairProfileCreate, db: Session = Depends(get_db)):
#     db_profile = models.UserHairProfile(**profile.dict())
#     db.add(db_profile)
#     db.commit()
#     db.refresh(db_profile)
#     return db_profile

# @app.get("/user-hair-profile/{user_id}", response_model=List[schemas.UserHairProfileRead])
# def read_user_hair_profiles(user_id: str, db: Session = Depends(get_db)):
#     profiles = db.query(models.UserHairProfile).filter(models.UserHairProfile.user_id == user_id).order_by(models.UserHairProfile.created_time.desc()).all()
#     return profiles

# @app.get("/user-hair-profile/{user_id}/latest", response_model=schemas.UserHairProfileRead)
# def read_latest_user_hair_profile(user_id: str, db: Session = Depends(get_db)):
#     profile = db.query(models.UserHairProfile).filter(models.UserHairProfile.user_id == user_id).order_by(models.UserHairProfile.created_time.desc()).first()
#     if not profile:
#         raise HTTPException(status_code=404, detail="User profile not found")
#     return profile
