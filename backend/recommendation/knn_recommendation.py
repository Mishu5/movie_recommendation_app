import numpy as np
from sklearn.neighbors import NearestNeighbors
from db.models import Media, User, UserPreference
import db.users
import db.media
import db.user_preferences

def get_media_features():
    media_list = db.media.get_all_media()
    media_features = []
    media_ids = []
    for media in media_list:
        features = [
            media.isAdult,
            media.startYear if media.startYear else 0,
            media.endYear if media.endYear else 0,
            media.runtimeMinutes if media.runtimeMinutes else 0,
        ]
