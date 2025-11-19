from sqlalchemy import create_engine, asc, desc
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
    review_count = session.query(Media).filter(Media.numVotes > 0).count()
    session.close()
    return review_count > 0

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

#Returns media page with minimum number of votes and containing any genres
def get_media_page(page, page_size, min_num_votes=0):
    offset = page * page_size
    session = Session()
    media = (
        session.query(Media)
        .filter(
            Media.numVotes >= min_num_votes,
            Media.genres != '{}',
            Media.titleType != 'tvEpisode'  # skip TV episodes
        )
        .offset(offset)
        .limit(page_size)
        .all()
    )
    session.close()
    return media


def add_review(tconst, averageRating, numVotes):
    session = Session()
    media = session.query(Media).filter(Media.tconst == tconst).first()
    if not media:
        session.close()
        return
    media.averageRating = averageRating
    media.numVotes = numVotes
    session.commit()
    session.close()

def get_user_media_page(page=1, page_size=6, sort_by="primaryTitle", sort_dir="asc",
                   min_rating=0, categories=None, search=""):
    
    if page < 1:
        page = 1

    session = Session()
    query = session.query(Media)

    # --- filtering ---
    query = query.filter(Media.averageRating >= min_rating)

    # ignoring tvEpisode for user browsing
    query = query.filter(Media.titleType != "tvEpisode")

    #ignoring media with no number of votes
    query = query.filter(Media.numVotes > 0)

    if categories:
        for cat in categories:
            query = query.filter(Media.genres.islike(f"%{cat}%"))

    if search:
        query = query.filter(Media.primaryTitle.islike(f"%{search}%"))

    # popular media on top
    query = query.order_by(desc(Media.numVotes))

    # --- sorting ---
    if sort_by == "primaryTitle":
        order = asc(Media.primaryTitle) if sort_dir == "asc" else desc(Media.primaryTitle)
    elif sort_by == "averageRating":
        order = asc(Media.averageRating) if sort_dir == "asc" else desc(Media.averageRating)
    else:
        order = asc(Media.tconst)

    query = query.order_by(desc(Media.numVotes), order)

    # --- pagination ---
    total = query.count()
    media_page = query.offset((page - 1) * page_size).limit(page_size).all()

    has_more = (page * page_size) < total

    result = {
        "ids": [m.tconst for m in media_page],
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": has_more
    }

    session.close()
    return result

def get_most_pupular_media(limit=10):
    session = Session()
    query = session.quert(Media)
    #ignoring tvEpisode
    query = query.filter(Media.titleType != "tvEpisode")
    #ignoring media with no number of votes
    query = query.filter(Media.numVotes > 0)
    #popular media on top
    query = query.order_by(desc(Media.numVotes))
    media = query.limit(limit).all()
    session.close()
    return media