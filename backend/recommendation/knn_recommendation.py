import numpy as np
import pickle
import os
from sklearn.neighbors import NearestNeighbors
from db.models import Media, User, UserPreference
import db.users
import db.media
import db.user_preferences

CACHE_FILE = 'media_features_cache.pkl'

def get_media_features():

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            media_features, media_ids, all_genres, genre_index = pickle.load(f)
        return media_features, media_ids, all_genres, genre_index

    media_list = db.media.get_all_media()
    all_genres = db.media.get_all_genres()
    genre_index = {genre: idx for idx, genre in enumerate(all_genres)}
    media_features = []
    media_ids = []
    for media in media_list:
        features = [
            media.isAdult,
            media.startYear if media.startYear else 0,
            media.endYear if media.endYear else 0,
            media.runtimeMinutes if media.runtimeMinutes else 0,
        ]
        genre_features = [0] * len(all_genres)
        for genre in media.genres:
            genre_features[genre_index[genre]] = 1
        features.extend(genre_features)
        media_features.append(features)
        media_ids.append(media.tconst)

    with open(CACHE_FILE, 'wb') as f:
        pickle.dump((media_features, media_ids, all_genres, genre_index), f)

    return np.array(media_features), media_ids