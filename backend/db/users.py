from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from db.models import User
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def add_user(email, password):
    session = Session()
    existing_user = get_user(email)

    if existing_user:
        session.close()
        return False

    try:
        new_user = User(email=email, password=password)
        session.add(new_user)
        session.commit()
        print(f"User {email} added.")
    except Exception as e:
        session.rollback()
        print(f"Error adding user: {e}")
    finally:
        session.close()
    return True

def update_user_password(email, new_password):
    session = Session()
    user = get_user(email)

    if not user:
        session.close()
        return False

    try:
        user.password = new_password
        session.commit()
        print(f"Password for {email} updated.")
    except Exception as e:
        session.rollback()
        print(f"Error updating password: {e}")
    finally:
        session.close()
    return True

def get_user(email):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    return user
    
