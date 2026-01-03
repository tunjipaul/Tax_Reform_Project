from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")  # mysql+pymysql://root:pass@localhost/dbname

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)











