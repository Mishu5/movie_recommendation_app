import os
from sqlalchemy import create_engine
from db.models import Base, Media
from sqlalchemy.orm import sessionmaker
from data.get_data import get_media_from_tsv
from db.media import get_all_media

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created!")

def check_and_add_media():
    media = get_all_media()
    if not media:
        print("Adding media...")
        rows_of_media = get_media_from_tsv("name.basics.tsv")
        
    else:
        print("Media exists")