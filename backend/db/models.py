from sqlalchemy import Column, Integer, String, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

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