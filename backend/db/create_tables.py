import os
from sqlalchemy import create_engine
from db.models import Base, Media
from sqlalchemy.orm import sessionmaker
from data.get_data import get_media_from_tsv
from db.media import check_media, add_media, check_reviews, add_review, get_media_by_tconst
from db.creators import check_creators, add_creator, associate_creator_with_media

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def create_tables():
    print("Creating tables...")
    Base.metadata.create_all(engine)
    print("Tables created!")

def check_and_add_media():
    media = check_media()
    print(media)
    if not media:
        print("Adding media...")
        rows_of_media = get_media_from_tsv("title.basics.tsv")
        for row in rows_of_media:

            # Skiping individual episodes
            if row['titleType'] == 'tvEpisode' and 'Episode' in row['primaryTitle']:
                continue

            genres = ''.join(str(row['genres'])).split(',')
            add_media(
                tconst=row['tconst'] if row['tconst'] != '\\N' else '',
                titleType=row['titleType'] if row['titleType'] != '\\N' else '',
                primaryTitle=row['primaryTitle'] if row['primaryTitle'] != '\\N' else '',
                originalTitle=row['originalTitle'] if row['originalTitle'] != '\\N' else '',
                isAdult=bool(int(row['isAdult'])) if row['isAdult'] != '\\N' else False,
                startYear=row['startYear'] if row['startYear'] != '\\N' else None,
                endYear=int(row['endYear']) if row['endYear'] != '\\N' else None,
                runtimeMinutes=int(row['runtimeMinutes']) if row['runtimeMinutes'].isdigit() else None,
                genres=genres if genres != ['\\N'] else []
            )
        print("Media added...")
    else:
        print("Media exists")

def check_and_add_reviews():
    review_check = check_reviews()
    if not review_check:
        print("Adding reviews...")
        rows_of_reviews = get_media_from_tsv('title.ratings.tsv')
        for row in rows_of_reviews:
            add_review(
                tconst = row['tconst'],
                averageRating = row['averageRating'],
                numVotes = row['numVotes']
            )
        print("Reviews added...")
    else:
        print("Reviews exists")

def check_and_add_creators():
    creator_check = check_creators()
    if not creator_check:
        print("Adding creators...")
        session = Session()
        rows_of_creators = get_media_from_tsv('title.crew.tsv')
        for row in rows_of_creators:
            tconst = row['tconst']
            media = get_media_by_tconst(tconst)
            if not media:
                continue
            directors = [d for d in row['directors'].split(',') if d and d != '\\N']
            writers = [w for w in row['writers'].split(',') if w and w != '\\N']
            for director in directors:
                add_creator(session, director)
                associate_creator_with_media(session, tconst, director)
            for writer in writers:
                add_creator(session, writer)
                associate_creator_with_media(session, tconst, writer)
        session.close()
        print("Creators added...")
    else:
        print("Creators already exist")