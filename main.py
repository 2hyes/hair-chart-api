from typing import List, Optional

from app import models, schemas, database

from fastapi import FastAPI, Depends, HTTPException, Body, Query
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

@app.post("/users/signup")
def signin(data: dict = Body(...), db: Session = Depends(get_db)):
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

    # Add default options to chart_item_user_options for this user
    default_options = db.query(models.ChartItemDefaultOption).all()
    for opt in default_options:
        option_id = opt.id
        if option_id.startswith("default_"):
            option_id = option_id[len("default_"):]
        new_id = f"{db_user.id}_{option_id}"
        db_option = models.ChartItemUserOption(
            id=new_id,
            user_id=db_user.id,
            category_id=opt.category_id,
            category_name=opt.category_name,
            option_name=opt.option_name,
            image_source=opt.image_source
        )
        db.add(db_option)

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

# TODO: 토큰 발급 로직 추가
@app.post("/users/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.id).first()
    if not user:
        raise HTTPException(status_code=401, detail="존재하지 않는 계정입니다.")
    if user.user_type != request.user_type:
        raise HTTPException(status_code=403, detail="해당 타입으로 가입된 아이디가 아닙니다.")
    if not bcrypt.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")
    return {
        "message": "로그인 성공",
        "user_id": user.id,
        "user_name": user.name,
        "user_type": user.user_type
    }

@app.patch("/users/{user_id}")
def update_user_info(user_id: str, data: dict = Body(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.user_type == "shop":
        # Shop: allow all fields except id
        updatable_fields = ["name", "phone_number"]
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        # Shop info (shop_name, shop_number, shop_biz_number) in Shop table
        shop = db.query(models.Shop).filter(models.Shop.id == user_id).first()
        if shop:
            shop_fields = ["shop_name", "shop_number", "shop_biz_number"]
            for field in shop_fields:
                if field in data:
                    setattr(shop, field.replace("shop_", ""), data[field])
        db.commit()
        return {"message": "Shop user info updated successfully"}
    elif user.user_type == "designer":
        # Designer: only name, phone_number
        allowed = False
        if "name" in data:
            user.name = data["name"]
            # Also update Designer table name
            designer = db.query(models.Designer).filter(models.Designer.id == user_id).first()
            if designer:
                designer.name = data["name"]
            allowed = True
        if "phone_number" in data:
            user.phone_number = data["phone_number"]
            allowed = True
        if not allowed:
            raise HTTPException(status_code=400, detail="Only name and phone_number can be updated for designer.")
        db.commit()
        return {"message": "Designer user info updated successfully"}
    elif user.user_type == "customer":
        # Customer: allow all fields except id
        updatable_fields = ["name", "phone_number"]
        updated = False
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                updated = True
        if "password" in data:
            user.hashed_password = bcrypt.hash(data["password"])
            updated = True
        if not updated:
            raise HTTPException(status_code=400, detail="No updatable fields provided for customer.")
        db.commit()
        return {"message": "Customer user info updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="User type not supported for update.")

@app.get("/users/check-id")
def check_user_id(id: str, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.id == id).first() is not None
    return {"exists": exists}

@app.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.user_type == "customer":
        return {
            "id": user.id,
            "user_name": user.name,
            "user_phone_number": user.phone_number
        }
    elif user.user_type == "shop":
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
    elif user.user_type == "designer":
        designer = db.query(models.Designer).filter(models.Designer.id == user_id).first()
        if not designer:
            raise HTTPException(status_code=404, detail="Designer not found")
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
        raise HTTPException(status_code=400, detail="Unknown user type")

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
    user_option_names = {option.option_name for option in user_options}

    default_options = db.query(models.ChartItemDefaultOption).all()

    merged_options = []
    for user_option in user_options:
        merged_options.append(schemas.ChartItemOptionMerged(
            category_id=user_option.category_id,
            category_name=user_option.category_name,
            option_name=user_option.option_name,
            image_source=user_option.image_source,
            is_user_option=True
        ))

    for default_option in default_options:
        if default_option.option_name not in user_option_names:
            merged_options.append(schemas.ChartItemOptionMerged(
                category_id=default_option.category_id,
                category_name=default_option.category_name,
                option_name=default_option.option_name,
                image_source=default_option.image_source,
                is_user_option=False
            ))

    return merged_options

@app.get("/chart-item-user-options/user/{user_id}/category/{category_id}", response_model=List[schemas.ChartItemOptionMerged])
def get_chart_item_options_by_user_and_category(user_id: str, category_id: str, db: Session = Depends(get_db)):
    user_options = db.query(models.ChartItemUserOption).filter(
        models.ChartItemUserOption.user_id == user_id,
        models.ChartItemUserOption.category_id == category_id
    ).all()
    user_option_names = {option.option_name for option in user_options}
    default_options = db.query(models.ChartItemDefaultOption).filter(
        models.ChartItemDefaultOption.category_id == category_id
    ).all()
    merged_options = []
    for user_option in user_options:
        merged_options.append(schemas.ChartItemOptionMerged(
            category_id=user_option.category_id,
            category_name=user_option.category_name,
            option_name=user_option.option_name,
            image_source=user_option.image_source,
            is_user_option=True
        ))
    for default_option in default_options:
        if default_option.option_name not in user_option_names:
            merged_options.append(schemas.ChartItemOptionMerged(
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
    id: str,  # unique sequence id
    db: Session = Depends(get_db)):
    db_option = db.query(models.ChartItemUserOption).filter(
        models.ChartItemUserOption.id == id
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

@app.get("/shops/{shop_id}/designers")
def list_designers_for_shop(
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

@app.get("/shops/{shop_id}/designers/{designer_id}")
def get_designer_for_shop(shop_id: str, designer_id: str, db: Session = Depends(get_db)):
    result = db.query(models.Designer, models.User).join(models.User, models.Designer.id == models.User.id)
    result = result.filter(models.Designer.belonging_shop_id == shop_id, models.Designer.id == designer_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Designer not found or does not belong to this shop")
    designer, user = result
    return {
        "id": user.id,
        "user_name": user.name,
        "user_phone_number": user.phone_number,
        "belonging_shop_id": designer.belonging_shop_id,
        "is_active": designer.is_active,
        "created_time": designer.created_time,
        "memo": designer.memo
    }
