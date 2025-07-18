from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app import schemas, models, database
import re
from typing import List

router = APIRouter(prefix="/api/chart-item-user-options", tags=["chart-item-user-options"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.ChartItemUserOptionRead)
def create_chart_item_user_option(option: schemas.ChartItemUserOption, db: Session = Depends(get_db)):
    existing = db.query(models.ChartItemUserOption).filter_by(
        user_id=option.user_id,
        category_id=option.category_id,
        option_name=option.option_name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="중복된 옵션명입니다.")
    latest_option = db.query(models.ChartItemUserOption).filter_by(
        user_id=option.user_id,
        category_id=option.category_id
    ).order_by(models.ChartItemUserOption.created_time.desc()).first()
    if latest_option:
        try:
            seq_part = latest_option.id.split("_")[-1]
            seq_num = int(seq_part)
            new_seq = seq_num + 1
        except:
            new_seq = 1
    else:
        new_seq = 1
    sequence = db.query(models.UserCategorySequence).filter_by(
        user_id=option.user_id,
        category_id=option.category_id
    ).first()
    if sequence:
        sequence.current_seq = new_seq
        db.add(sequence)
    else:
        sequence = models.UserCategorySequence(
            user_id=option.user_id,
            category_id=option.category_id,
            current_seq=new_seq
        )
        db.add(sequence)
    db.flush()
    existing_options = db.query(models.ChartItemUserOption).filter_by(
        user_id=option.user_id,
        category_id=option.category_id
    ).all()
    max_seq = 0
    for opt in existing_options:
        m = re.match(rf"{option.user_id}_{option.category_id}_(\d+)", opt.id)
        if m:
            seq_num = int(m.group(1))
            if seq_num > max_seq:
                max_seq = seq_num
    new_seq = max_seq + 1
    option_id = f"{option.user_id}_{option.category_id}_{new_seq}"
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
    created_option = db.query(models.ChartItemUserOption).filter_by(
        user_id=option.user_id,
        category_id=option.category_id,
        option_name=option.option_name
    ).order_by(models.ChartItemUserOption.created_time.desc()).first()
    if not created_option:
        raise HTTPException(status_code=500, detail="등록 후 옵션을 찾을 수 없습니다.")
    return created_option

@router.get("/user/{user_id}", response_model=List[schemas.ChartItemOptionMerged])
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

@router.get("/user/{user_id}/category/{category_id}", response_model=List[schemas.ChartItemOptionMerged])
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

@router.get("/in-use/")
def is_chart_item_user_option_in_use(user_id: str, category_id: str, option_name: str, db: Session = Depends(get_db)):
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
        return {"in_use": False}

@router.delete("/")
def delete_chart_item_user_option(
    id: str,
    db: Session = Depends(get_db)):
    db_option = db.query(models.ChartItemUserOption).filter(
        models.ChartItemUserOption.id == id
    ).first()
    if not db_option:
        raise HTTPException(status_code=404, detail="Chart item user option not found")
    db.delete(db_option)
    db.commit()
    return {"message": "Chart item user option deleted successfully"} 