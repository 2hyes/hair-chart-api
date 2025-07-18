from typing import List

from app import models, schemas, database
from src.auth.router import router as auth_router
from src.user.router import router as user_router
from src.chart_option.router import router as chart_option_router
from src.designers.router import router as designers_router
from src.customers.router import router as customers_router

from fastapi import FastAPI, Depends, Header
from sqlalchemy.orm import Session
# from jose import jwt

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(chart_option_router)
app.include_router(designers_router)
app.include_router(customers_router)

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# @app.get("/shops/{shop_id}/customers", response_model=List[schemas.CustomerDesignerMappingRead])
# def get_customers_for_shop(shop_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
#     # 샵 관리자 권한 체크 필요
#     pass

# @app.get("/designers/{designer_id}/customers", response_model=List[schemas.CustomerDesignerMappingRead])
# def get_customers_for_designer(designer_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
#     # 디자이너 본인 권한 체크 필요
#     pass

# @app.patch("/customers/{customer_id}/designer-requests/{mapping_id}", response_model=schemas.CustomerDesignerMappingRead)
# def update_customer_registration_status(customer_id: str, mapping_id: int, req: schemas.CustomerDesignerMappingUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
#     # 고객 본인 권한 체크, status 변경
#     pass

# @app.get("/customers/{customer_id}/detail")
# def get_customer_detail(customer_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
#     # 본인/권한자 체크, 고객+디자이너+차트이력 등 반환
#     pass
