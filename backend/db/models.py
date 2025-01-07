from sqlalchemy import Column, Integer, String, Boolean, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    preferences = relationship("UserPreference", back_populates="user")


class Media(Base):
    __tablename__ = "medias"

    tconst = Column(String, primary_key=True)  # Alphanumeric unique identifier for the title
    titleType = Column(String)  # Type of the title (movie, short, tvseries, tvepisode, video, etc.)
    primaryTitle = Column(String)  # The popular title used by filmmakers
    originalTitle = Column(String)  # Original title in the original language
    isAdult = Column(Boolean)  # Boolean flag (0 for non-adult, 1 for adult)
    startYear = Column(Integer)  # Year the title was released (or series start year)
    endYear = Column(Integer, nullable=True)  # Year the series ended (nullable for non-TV titles)
    runtimeMinutes = Column(Integer, nullable=True)  # Duration in minutes
    genres = Column(ARRAY(String))  # Comma-separated string of genres
    preferences = relationship("UserPreference", back_populates="media")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Foreign key to User
    media_id = Column(String, ForeignKey('medias.tconst'), nullable=False)  # Foreign key to Media
    rating = Column(Integer, nullable=False)
    user = relationship("User", back_populates="preferences")
    media = relationship("Media", back_populates="preferences")