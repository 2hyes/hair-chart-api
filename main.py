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

@app.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # TODO: password encryption
    existing_user = db.query(models.User).filter(models.User.id == user.id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="The user ID is already taken.")
    
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}", response_model=schemas.UserRead)
def read_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=List[schemas.UserRead])
def read_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.post("/user-hair-profile/", response_model=schemas.UserHairProfileRead)
def create_user_hair_profile(profile: schemas.UserHairProfileCreate, db: Session = Depends(get_db)):
    db_profile = models.UserHairProfile(**profile.dict())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

@app.get("/user-hair-profile/{user_id}", response_model=List[schemas.UserHairProfileRead])
def read_user_hair_profiles(user_id: str, db: Session = Depends(get_db)):
    profiles = db.query(models.UserHairProfile).filter(models.UserHairProfile.user_id == user_id).order_by(models.UserHairProfile.created_time.desc()).all()
    return profiles

@app.get("/user-hair-profile/{user_id}/latest", response_model=schemas.UserHairProfileRead)
def read_latest_user_hair_profile(user_id: str, db: Session = Depends(get_db)):
    profile = db.query(models.UserHairProfile).filter(models.UserHairProfile.user_id == user_id).order_by(models.UserHairProfile.created_time.desc()).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile