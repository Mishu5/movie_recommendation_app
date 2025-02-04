import numpy as np
import pickle
import os
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from db.models import Media, User, UserPreference
import db.users
import db.media
import db.user_preferences

CACHE_FILE = '/app/cache/media_genre_features_cache.pkl'
PAGE_SIZE = 10000
genre_knn = None # genre_knn model
scaler = None

def save_to_cache_genre(media_genre_features, media_ids, all_genres, genre_index):
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump((media_genre_features, media_ids, all_genres, genre_index), f)
        print(f"Cache file saved to {CACHE_FILE}")
    except Exception as e:
        print(f"Error saving cache file: {e}")

def load_from_cache_genre():
    with open(CACHE_FILE, 'rb') as f:
        media_genre_features, media_ids, all_genres, genre_index = pickle.load(f)
    return media_genre_features, media_ids, all_genres, genre_index

def delete_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print(f"Cache file {CACHE_FILE} deleted.")
    else:
        print(f"Cache file {CACHE_FILE} does not exist.")

def get_media_features_for_genres():

    media_list = None
    all_genres = db.media.get_all_genres()
    genre_index = {genre: idx for idx, genre in enumerate(all_genres)}
    media_ids = []
    page = 0
    media_genre_features = []

    if os.path.exists(CACHE_FILE):
        print(f"Loading media features from cache file {CACHE_FILE}")
        media_genre_features, media_ids, all_genres, genre_index = load_from_cache_genre()
        return media_genre_features, media_ids

    while True:

        media_list = db.media.get_media_page(page, PAGE_SIZE , 0)
        if not media_list:
            break

        for media in media_list:
            genre_features = [0] * len(all_genres)
            for genre in media.genres:
                genre_features[genre_index[genre]] = 1
            media_genre_features.append(genre_features)
            media_ids.append(media.tconst)

        page += 1

    media_genre_features = np.array(media_genre_features)

    # Normalizing the data
    global scaler
    scaler = StandardScaler()

    save_to_cache_genre(media_genre_features, media_ids, all_genres, genre_index)

    return media_genre_features, media_ids

def train_genre_knn(media_features):
    global genre_knn
    genre_knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
    genre_knn.fit(media_features)
    return genre_knn

def train_knns():
    media_features, _ = get_media_features_for_genres()
    train_genre_knn(media_features)

def recommend_media(user_id, k=5):
    user_preferences = db.user_preferences.get_user_preferences(user_id)
    media, distances = recommend_media_based_on_genre(user_preferences, k)
    return media, distances


def recommend_media_based_on_genre(user_preferences, k=5):
    #add if nothing in user_preferences
    
    #features
    global genre_knn
    if not genre_knn:
        return None
    
    user_ratings = []
    _, media_ids, all_genres, genre_index = load_from_cache_genre()

    
    for preference in user_preferences:
        media = db.media.get_media_by_tconst(preference.media_id)
        if media:
            genre_features = [0] * len(all_genres)
            for genre in media.genres:
                genre_features[genre_index[genre]] = 1
            user_ratings.append(genre_features)

    user_ratings = np.array(user_ratings)
    distances, indices = genre_knn.kneighbors(user_ratings, n_neighbors=k)

    #Convert knn results to list of media ids and distances
    recommended_ids = set()
    recommended_distances = []
    for idx_list, dist_list in zip(indices, distances):
        for idx, dist in zip(idx_list, dist_list):
            recommended_ids.add(media_ids[idx])
            recommended_distances.append(dist)

    return list(recommended_ids), recommended_distances


def test_recommend_media(user_id, k=5):
    recommendations = recommend_media(user_id, k)
    if recommendations:
        print(f"Recommendations for user {user_id}: {recommendations}")
    else:
        print(f"No recommendations for user {user_id}")