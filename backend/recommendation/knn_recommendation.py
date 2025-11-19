import numpy as np
import pickle
import os
from sklearn.neighbors import NearestNeighbors
from db.models import Media, User, UserPreference
import db.users
import db.media
import db.user_preferences

CACHE_FILE = '/app/cache/media_genre_features_cache.pkl'
PAGE_SIZE = 10000
genre_knn = None  # genre_knn model
NUM_VOTES_WEIGHT_EXPONENT = 1.1  # Exponent for numVotes weighting

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
    all_genres = db.media.get_all_genres()
    genre_index = {genre: idx for idx, genre in enumerate(all_genres)}
    media_ids = []
    page = 0
    media_genre_features = []

    # Load from cache if exists
    if os.path.exists(CACHE_FILE):
        print(f"Loading media features from cache file {CACHE_FILE}")
        media_genre_features, media_ids, all_genres, genre_index = load_from_cache_genre()
        return media_genre_features, media_ids

    # Loop through pages of media
    while True:
        media_list = db.media.get_media_page(page, PAGE_SIZE, 0)
        if not media_list:
            break

        for media in media_list:
            genre_features = [0] * len(all_genres)
            for genre in media.genres:
                genre_features[genre_index[genre]] = 1

            # Multiply features by popularity weight
            popularity_weight = (np.log1p(media.numVotes) ** NUM_VOTES_WEIGHT_EXPONENT) if media.numVotes else 1
            weighted_features = [f * popularity_weight for f in genre_features]

            media_genre_features.append(weighted_features)
            media_ids.append(media.tconst)

        page += 1

    media_genre_features = np.array(media_genre_features, dtype=float)
    save_to_cache_genre(media_genre_features, media_ids, all_genres, genre_index)
    return media_genre_features, media_ids

def train_genre_knn(media_features):
    global genre_knn
    genre_knn = NearestNeighbors(n_neighbors=50, metric='euclidean')
    genre_knn.fit(media_features)
    return genre_knn

def train_knns():
    media_features, _ = get_media_features_for_genres()
    train_genre_knn(media_features)

def recommend_media(user_id, k=5):
    user_preferences = db.user_preferences.get_user_preferences(user_id)

    # Cold start: no preferences
    if not user_preferences:
        popular_media = db.media.get_most_pupular_media(limit=k)
        media = [m.tconst for m in popular_media]
        distances = [0] * len(media)
        return media, distances

    media, distances = recommend_media_based_on_genre(user_preferences, k)
    return media, distances

def recommend_media_based_on_genre(user_preferences, k=5, alpha=0.5, beta=7.0):
    """
    alpha: weight for average rating
    beta: weight for popularity (numVotes)
    """
    global genre_knn
    if not genre_knn or not user_preferences:
        return [], []

    media_features, media_ids, all_genres, genre_index = load_from_cache_genre()
    user_profile = np.zeros(len(all_genres))

    # Build user profile vector
    for preference in user_preferences:
        media = db.media.get_media_by_tconst(preference.media_id)
        if media:
            genre_features = np.zeros(len(all_genres))
            for genre in media.genres:
                genre_features[genre_index[genre]] = 1

            # Weight features by user rating
            user_profile += genre_features * preference.rating

            # Boost by average rating
            if media.averageRating:
                user_profile += genre_features * alpha * media.averageRating

            # Strongly boost by popularity
            if media.numVotes:
                user_profile += genre_features * beta * (np.log1p(media.numVotes) ** NUM_VOTES_WEIGHT_EXPONENT)

    # Get k nearest neighbors directly from KNN
    distances, indices = genre_knn.kneighbors([user_profile], n_neighbors=k)

    # Collect unique media IDs
    recommended_ids = []
    recommended_distances = []
    seen = set()
    for idx, dist in zip(indices[0], distances[0]):
        media_id = media_ids[idx]
        if media_id not in seen:
            recommended_ids.append(media_id)
            recommended_distances.append(dist)
            seen.add(media_id)
        if len(recommended_ids) == k:
            break

    return recommended_ids, recommended_distances

def test_recommend_media(user_id, k=5):
    recommendations = recommend_media(user_id, k)
    if recommendations:
        print(f"Recommendations for user {user_id}: {recommendations}")
    else:
        print(f"No recommendations for user {user_id}")
