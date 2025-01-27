from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db.models import Creators, Media
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def add_creator(session, creator_id):
    #session = Session()
    creator = session.query(Creators).filter_by(id=creator_id).first()
    if not creator:
        creator = Creators(id=creator_id)
        session.add(creator)
        session.commit()
    #session.close()
    return creator

def associate_creator_with_media(session, media_id, creator_id):
    #session = Session()
    media = session.query(Media).filter_by(tconst=media_id).first()
    creator = session.query(Creators).filter_by(id=creator_id).first()
    if media and creator:
        media.creators.append(creator)
        session.commit()
        #session.close()
        return True
    #session.close()
    return False

def check_creators():
    session = Session()
    creator_count = session.query(Creators).count()
    session.close()
    return creator_count > 0