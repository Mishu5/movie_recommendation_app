import os
from sqlalchemy import create_engine
from db.models import Base, Media
from sqlalchemy.orm import sessionmaker
from data.get_data import get_media_from_tsv
from db.media import check_media, add_media, check_reviews, add_review

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

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
            if row['titleType'] == 'tvEpisode' or 'Episode' in row['primaryTitle']:
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
        rows_of_reviews = get_media_from_tsv("title.ratings.tsv")
        for row in rows_of_reviews:
            add_review(
                tconst = row['tconst'],
                averageRating = row['averageRating'],
                numVotes = row['numVotes']
            )
        print("Reviews added...")
    else:
        print("Reviews exists")

        