import os
from sqlalchemy import create_engine
from db.models import Base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created!")

