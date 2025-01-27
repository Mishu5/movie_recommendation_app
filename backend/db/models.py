from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, ARRAY, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Association table for the many-to-many relationship between Media and Creators
media_creators_association = Table(
    'media_creators', Base.metadata,
    Column('media_id', String, ForeignKey('medias.tconst')),
    Column('creator_id', String, ForeignKey('creators.id'))
)

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
    averageRating = Column(Float, nullable=True)  # Average rating of the title
    numVotes = Column(Integer, nullable=True)  # Number of votes the title has received

    preferences = relationship("UserPreference", back_populates="media")
    creators = relationship("Creators", secondary=media_creators_association, back_populates="works")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Foreign key to User
    media_id = Column(String, ForeignKey('medias.tconst'), nullable=False)  # Foreign key to Media
    rating = Column(Float, nullable=False)

    user = relationship("User", back_populates="preferences")
    media = relationship("Media", back_populates="preferences")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "media_id": self.media_id,
            "rating": self.rating
        }

class Creators(Base):
    __tablename__ = "creators"

    id = Column(String, primary_key=True)
    works = relationship("Media", secondary=media_creators_association, back_populates="creators")