import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database configuration: defaults to SQLite inside the project folder
# For MySQL, set the DATABASE_URL environment variable to:
# mysql+pymysql://username:password@localhost:3306/db_name
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dengue.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
