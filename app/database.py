import os
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Page(Base):
    __tablename__ = "pages"
    url = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    embedding = Column(ARRAY(Float))
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
