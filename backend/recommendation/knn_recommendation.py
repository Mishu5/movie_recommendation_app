import numpy as np
import pickle
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from db.models import Media, User, UserPreference
import db.users
import db.media
import db.user_preferences

CACHE_FILE = '/app/cache/media_features_cache.pkl'
PAGE_SIZE = 10000

def save_to_cache(media_features, media_ids, all_genres, genre_index):
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump((media_features, media_ids, all_genres, genre_index), f)
        print(f"Cache file saved to {CACHE_FILE}")
    except Exception as e:
        print(f"Error saving cache file: {e}")


def load_from_cache():
    with open(CACHE_FILE, 'rb') as f:
        media_features, media_ids, all_genres, genre_index = pickle.load(f)
    return media_features, media_ids, all_genres, genre_index

def delete_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print(f"Cache file {CACHE_FILE} deleted.")
    else:
        print(f"Cache file {CACHE_FILE} does not exist.")


def get_media_features():

    media_list = None
    all_genres = db.media.get_all_genres()
    genre_index = {genre: idx for idx, genre in enumerate(all_genres)}
    media_features = []
    media_ids = []
    page = 0

    if os.path.exists(CACHE_FILE):
        print(f"Loading media features from cache file {CACHE_FILE}")
        media_features, media_ids, all_genres, genre_index = load_from_cache()
        return media_features, media_ids

    while True:

        media_list = db.media.get_media_page(page, PAGE_SIZE , 0) # 1 to filter out unreviewed media from the dataset
        if not media_list:
            break

        for media in media_list:
            features = [
                media.isAdult,
                media.startYear if media.startYear else 0,
                media.endYear if media.endYear else 0,
                media.runtimeMinutes if media.runtimeMinutes else 0,
                media.averageRating if media.averageRating else 0,
                media.numVotes if media.numVotes else 0
            ]
            genre_features = [0] * len(all_genres)
            for genre in media.genres:
                genre_features[genre_index[genre]] = 1
            features.extend(genre_features)
            media_features.append(features)
            media_ids.append(media.tconst)

        page += 1

    media_features = np.array(media_features)

    # Normalizing the data
    scaler = StandardScaler()
    media_features = scaler.fit_transform(media_features)

    save_to_cache(media_features, media_ids, all_genres, genre_index)

    return media_features, media_ids

def train_knn(media_features):
    knn = NearestNeighbors(n_neighbors=5, metric='auto')
    knn.fit(media_features)
    return knn

def recommend_media(user_id, k=5):
    user_preferences = db.user_preferences.get_user_preferences(user_id)
    #add if nothing in user_preferences

    