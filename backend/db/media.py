from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db.models import Media
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_all_media():
    session = Session()
    media = session.query(Media).all()
    session.close()
    return media

def add_media(tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres):
    new_media = Media(
        tconst=tconst,
        titleType=titleType,
        primaryTitle=primaryTitle,
        originalTitle=originalTitle,
        isAdult=isAdult,
        startYear=startYear,
        endYear=endYear,
        runtimeMinutes=runtimeMinutes,
        genres=genres
    )
    
    try:
        session = Session()
        session.add(new_media)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error adding media: {e}")
    finally:
        session.close()