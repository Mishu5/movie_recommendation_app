from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def add_user(email, password):
    session = Session()
    new_user = User(email=email, password=password)
    session.add(new_user)
    session.commit()
    print(f"User {email} added.")
    session.close()
