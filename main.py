from typing import List

from app import models, schemas, database

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
# from jose import jwt

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
    
    hashed_pw = bcrypt.hash(customer.user_password)
    db_user = models.User(
        id=customer.id,
        name=customer.user_name,
        hashed_password=hashed_pw, 
        phone_number=customer.user_phone_number,
        user_type='customer'
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "id": db_user.id,
        "user_name": db_user.name,
        "user_phone_number": db_user.phone_number
    }

@app.post("/shops", response_model=schemas.ShopRead)
def create_shop(shop: schemas.ShopCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.id == shop.id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="User ID already taken.")
    
    hashed_pw = bcrypt.hash(shop.user_password)
    db_user = models.User(
        id=shop.id,
        name=shop.user_name,
        hashed_password=hashed_pw, 
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
    
    hashed_pw = bcrypt.hash(designer.user_password)
    db_user = models.User(
        id=designer.id,
        name=designer.user_name,
        hashed_password=hashed_pw,
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


@app.get("/users/check-id")
def check_user_id(id: str, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.id == id).first() is not None
    return {"exists": exists}


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

@app.post("/chart-item-user-options/", response_model=schemas.ChartItemUserOptionRead)
def create_chart_item_user_option(option: schemas.ChartItemUserOption, db: Session = Depends(get_db)):
    existing = db.query(models.ChartItemUserOption).filter_by(
        user_id=option.user_id,
        category_id=option.category_id,
        option_name=option.option_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="중복된 옵션명입니다.")

    sequence = db.query(models.UserCategorySequence).filter_by(
        user_id=option.user_id,
        category_id=option.category_id
    ).first()
    
    if sequence:
        sequence.current_seq += 1
        db.add(sequence)
    else:
        sequence = models.UserCategorySequence(
            user_id=option.user_id,
            category_id=option.category_id,
            current_seq=1
        )
        db.add(sequence)
    
    db.flush()

    option_id = f"{option.user_id}_{option.category_id}_{sequence.current_seq}"
    
    db_option = models.ChartItemUserOption(
        id=option_id,
        user_id=option.user_id,
        category_id=option.category_id,
        category_name=option.category_name,
        option_name=option.option_name,
        image_source=option.image_source
    )
    db.add(db_option)
    try:
        db.flush()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"DB insert error: {str(e)}")

    db.commit()

    # 실제로 저장된 row를 user_id, category_id, option_name으로 쿼리
    created_option = db.query(models.ChartItemUserOption).filter_by(
        user_id=option.user_id,
        category_id=option.category_id,
        option_name=option.option_name
    ).order_by(models.ChartItemUserOption.created_time.desc()).first()

    if not created_option:
        raise HTTPException(status_code=500, detail="등록 후 옵션을 찾을 수 없습니다.")

    return created_option

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

@app.get("/chart-item-user-options/in-use/")
def is_chart_item_user_option_in_use(user_id: str, category_id: str, option_name: str, db: Session = Depends(get_db)):
    # TODO: Chart 테이블이 생성되면 실제 사용 여부 확인 로직으로 변경
    # 현재는 임시로 False 반환 (차트 테이블이 없으므로)
    try:
        in_use = db.query(models.Chart).filter(
            models.Chart.user_id == user_id,
            models.Chart.category_id == category_id,
            models.Chart.option_name == option_name
        ).first() is not None
        return {"in_use": in_use}
    except HTTPException:
        raise
    except:
        # Chart 테이블이 없으면 임시로 False 반환
        return {"in_use": False}

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

# TODO: 토큰 발급 로직 추가
@app.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.id).first()
    if not user or not bcrypt.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    return {
        "message": "로그인 성공",
        "user_type": user.user_type,
        "user_id": user.id
    }

