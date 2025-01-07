from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db.models import UserPreference
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def get_user_preferences(user_id):
    session = Session()
    user_preferences = session.query(UserPreference).filter(UserPreference.user_id == user_id).all()
    session.close()
    return user_preferences

def add_user_preference(user_id, tconst, rating):
    new_user_preference = UserPreference(
        user_id=user_id,
        tconst=tconst,
        rating=rating
    )
    
    try:
        session = Session()
        session.add(new_user_preference)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error adding user preference: {e}")
    finally:
        session.close()

def update_user_preference(user_id, tconst, rating):
    session = Session()
    user_preference = session.query(UserPreference).filter(UserPreference.user_id == user_id, UserPreference.tconst == tconst).first()
    user_preference.rating = rating
    session.commit()
    session.close()
