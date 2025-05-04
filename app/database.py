import os
import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
MAX_RETRIES = 10

for attempt in range(MAX_RETRIES):
    try:
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True, 
        )
        with engine.connect() as conn:
            print("✅ DB Connection successed.")
        break
    except Exception as e:
        print(f"❌ DB Connection failed... Retry:({attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)
else:
    raise RuntimeError("DB Connection failed.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
