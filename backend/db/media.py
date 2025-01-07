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

def check_media():
    session = Session()
    media_count = session.query(Media).count()
    session.close()
    return media_count

def check_reviews():
    session = Session()
    review_check = session.query(Media.numVotes).first()
    session.close()
    return review_check

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

def get_media_by_tconst(tconst):
    session = Session()
    media = session.query(Media).filter(Media.tconst == tconst).first()
    session.close()
    return media

def get_all_genres():
    session = Session()
    genres = session.query(Media.genres).all()
    session.close()
    distinct_genres = set()
    for genre in genres:
        for g in genre.genres:
            distinct_genres.add(g)
    return distinct_genres

def get_media_page(page, page_size):
    offset = page * page_size
    session = Session()
    media = session.query(Media).offset(offset).limit(page_size).all()
    session.close()
    return media

def add_review(tconst, rating, numVotes):
    session = Session()
    media = session.query(Media).filter(Media.tconst == tconst).first()
    media.averageRating = rating
    media.numVotes = numVotes
    session.commit()
    session.close()
    