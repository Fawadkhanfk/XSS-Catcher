import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

if os.getenv("TESTING"):
    database_url = "sqlite:///./app.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    db_password = os.environ["POSTGRES_PASSWORD"]
    database_url = f"postgresql://user:{db_password}@database/xss"
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
