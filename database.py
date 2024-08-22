from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pymongo

import os

engine = create_engine(
    os.getenv("SQL_ALCHEMY_DATABASE_URL"),connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind = engine)

Base = declarative_base()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_damn_db():
    return SessionLocal()

def get_mongodb():
    client = pymongo.MongoClient(os.getenv("MONGO_DB_URL"))
    db = client.GB
    return db.GB
