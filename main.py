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
        name=shop.name,
        password=shop.password,
        phone_number=shop.phone_number,
        user_type='shop'
    )
    db.add(db_user)
    db.flush()

    db_shop = models.Shop(
        id=shop.id,
        name=shop.name,
        number=shop.shop_number,
        biz_number=shop.biz_number
    )
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)

    return {
        "id": db_shop.id,
        "name": db_shop.name,
        "phone_number": db_user.phone_number,
        "shop_number": db_shop.number,
        "biz_number": db_shop.biz_number,
        "created_time": db_shop.created_time
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
        "id": shop.id,
        "name": shop.name,
        "phone_number": user.phone_number,
        "shop_number": shop.number,
        "biz_number": shop.biz_number,
        "created_time": shop.created_time
    } 
