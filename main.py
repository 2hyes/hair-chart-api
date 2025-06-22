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


@app.post("/designers", response_model=schemas.DesignerCreateResponse)
def create_designer(designer: schemas.DesignerCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.id == designer.id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User ID already taken.")
    
    db_user = models.User(
        id=designer.id,
        name=designer.user_name,
        password=designer.user_password,
        phone_number=designer.user_phone_number,
        user_type='designer'
    )
    db.add(db_user)
    db.flush()

    db_designer = models.Designer(
        id=designer.id,
        name=designer.user_name,
        is_active=designer.is_active,
        belonging_shop_id=designer.belonging_shop_id,
        memo=designer.memo
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


@app.get("/designers/{designer_id}", response_model=schemas.DesignerRead)
def get_designer(designer_id: str, db: Session = Depends(get_db)):
    result = db.query(models.Designer, models.User).\
        join(models.User, models.Designer.id == models.User.id).\
        filter(models.Designer.id == designer_id).\
        first()
    
    if result is None:
        raise HTTPException(status_code=404, detail="Designer not found")
    
    designer, user = result
    # TODO: customer_count, recent_chart_created_time 추가
    return {
        "id": user.id,
        "user_name": user.name,
        "user_phone_number": user.phone_number,
        "belonging_shop_id": designer.belonging_shop_id,
        "is_active": designer.is_active,
        "created_time": designer.created_time,
        "memo": designer.memo
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

@app.post("/chart-item-user-options/", response_model=schemas.ChartItemUserOption)
def create_chart_item_user_option(option: schemas.ChartItemUserOption, db: Session = Depends(get_db)):
    db_option = models.ChartItemUserOption(**option.dict())
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    return db_option

@app.get("/chart-item-user-options/user/{user_id}", response_model=List[schemas.ChartItemOptionMerged])
def get_chart_item_options_by_user(user_id: str, db: Session = Depends(get_db)):
    user_options = db.query(models.ChartItemUserOption).filter(models.ChartItemUserOption.user_id == user_id).all()
    user_category_ids = {option.category_id for option in user_options}

    default_options = db.query(models.ChartItemDefaultOption).filter(
        models.ChartItemDefaultOption.category_id.in_(user_category_ids)
    ).all()
    user_option_names = {option.option_name for option in user_options}
    
    merged_options = []
    for user_option in user_options:
        merged_options.append(schemas.ChartItemOptionMerged(
            user_id=user_option.user_id,
            category_id=user_option.category_id,
            category_name=user_option.category_name,
            option_name=user_option.option_name,
            image_source=user_option.image_source,
            is_user_option=True
        ))
    
    for default_option in default_options:
        if default_option.option_name not in user_option_names:
            merged_options.append(schemas.ChartItemOptionMerged(
                user_id=None,
                category_id=default_option.category_id,
                category_name=default_option.category_name,
                option_name=default_option.option_name,
                image_source=default_option.image_source,
                is_user_option=False
            ))
    
    return merged_options

@app.delete("/chart-item-user-options/")
def delete_chart_item_user_option(
    user_id: str,
    category_id: str, 
    option_name: str, 
    db: Session = Depends(get_db)):
    db_option = db.query(models.ChartItemUserOption).filter(
        models.ChartItemUserOption.user_id == user_id,
        models.ChartItemUserOption.category_id == category_id,
        models.ChartItemUserOption.option_name == option_name
    ).first()
    
    if not db_option:
        raise HTTPException(status_code=404, detail="Chart item user option not found")
    
    db.delete(db_option)
    db.commit()
    
    return {"message": "Chart item user option deleted successfully"}

# @app.put("/chart-item-user-options/")
# def update_chart_item_user_option(
#     user_id: str, 
#     category_id: str, 
#     option_name: str, 
#     option_update: schemas.ChartItemUserOption, 
#     db: Session = Depends(get_db)
# ):
#     db_option = db.query(models.ChartItemUserOption).filter(
#         models.ChartItemUserOption.user_id == user_id,
#         models.ChartItemUserOption.category_id == category_id,
#         models.ChartItemUserOption.option_name == option_name
#     ).first()
    
#     if not db_option:
#         raise HTTPException(status_code=404, detail="Chart item user option not found")
    
#     update_data = option_update.dict(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(db_option, field, value)
    
#     db.commit()
#     db.refresh(db_option)
    
#     return {"message": "Chart item user option updated successfully"}

