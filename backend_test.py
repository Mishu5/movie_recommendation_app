import requests
import socketio
import time
import sys
from colorama import Fore, Style, Back
import threading
from collections import Counter
import numpy as np
import math

def get_categories(tconst: str):
    response = requests.post(f"http://{BASE_URL}/media/{tconst}", json={
        })
    #print(f"{response.json().get("media", {}).get("originalTitle")}, numVotes: {response.json().get("media", {}).get("numVotes")}")
    genres = response.json().get("media", {}).get("genres")
    return genres


def compute_accuracy(user_counter, rec_counter):
    all_genres = set(user_counter.keys()) | set(rec_counter.keys())

    user_vector = np.array([user_counter.get(g, 0) for g in all_genres])
    rec_vector = np.array([rec_counter.get(g, 0) for g in all_genres])

    if np.all(user_vector == 0) or np.all(rec_vector == 0):
        return 0.0

    similarity = np.dot(user_vector, rec_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(rec_vector))
    return similarity


def ndcg_at_k_genres(user_counter, rec_counter, k):
    all_genres = sorted(set(user_counter.keys()) | set(rec_counter.keys()))

    user_vector = np.array([user_counter.get(g, 0) for g in all_genres])
    rec_vector  = np.array([rec_counter.get(g, 0) for g in all_genres])

    if np.all(user_vector == 0) or np.all(rec_vector == 0):
        return 0.0

    ranked_indices = np.argsort(rec_vector)[::-1]

    dcg = 0.0
    for rank, idx in enumerate(ranked_indices[:k], start=1):
        relevance = user_vector[idx]
        dcg += relevance / math.log2(rank + 1)

    ideal_indices = np.argsort(user_vector)[::-1]
    ideal_hits = min(k, np.count_nonzero(user_vector))

    idcg = 0.0
    for rank, idx in enumerate(ideal_indices[:ideal_hits], start=1):
        relevance = user_vector[idx]
        idcg += relevance / math.log2(rank + 1)

    if idcg == 0:
        return 0.0

    return dcg / idcg

class UserMedia:
    tconst: str
    rating: float

    def __init__(self, tconst, rating):
        self.tconst = tconst
        self.rating = rating

class User:

    email: str = None
    password: str = None
    jwt: str = None
    room_id: str = None
    media_list: list[str] = []
    user_media_list: list[UserMedia] = []
    sio: socketio.Client = None
    recommendations_from_room: list[str] = []
    liked_media_index: list[int] = []
    personal_recommendations: list[str] = []

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.sio = socketio.Client()

    def __str__(self):
        return f"User(email={self.email}, password={self.password}, room_id={self.room_id})"

    def get_user_category_stats(self):
        category_counter = Counter()

        for tconst in self.media_list:
            categories = get_categories(tconst) or []
            category_counter.update(categories)
        return category_counter

    def get_user_recommendation_category_stats(self):
        category_counter = Counter()
        result = requests.post(f"http://{BASE_URL}/recommendations/get", json={
            "jwt": self.jwt
        })

        recommendation_list = result.json().get("recommendations", [])
        for tconst in recommendation_list:
            categories = get_categories(tconst) or []
            category_counter.update(categories)
        return category_counter



def connect_user_socket(user: User, base_url: str):
    try:
        #Events
        @user.sio.event
        def connect():
            print(Fore.GREEN + f"[Socket.IO] User {user.email} connected to room {user.room_id}" + Style.RESET_ALL)
        @user.sio.event
        def disconnect():
            print(Fore.YELLOW + f"[Socket.IO] User {user.email} disconnected from room {user.room_id}" + Style.RESET_ALL)
        @user.sio.on("message-started")
        def on_message_started(data):
            print(Fore.CYAN + f"[Socket.IO] User {user.email} received message-started event in room {user.room_id}: {data}" + Style.RESET_ALL)
            time.sleep(2)
            #Getting recommendations
            response = requests.post(f"http://{base_url}/rooms/recommendations", json={
                "jwt": user.jwt,
                "room_id": user.room_id
            })
            if response.status_code == 200:
                user.recommendations_from_room = response.json().get("recommended_media", [])
                user.recommendations_from_room.sort()
                print(Fore.GREEN + f"[Socket.IO] User {user.email} received recommendations in room {user.room_id}: {len(user.recommendations_from_room)}." + Style.RESET_ALL)
                #Liking media
                time.sleep(2)  #Wait before liking
                for index in user.liked_media_index:
                    tconst_to_like = user.recommendations_from_room[index]
                    user.sio.emit("message-like", {"jwt": user.jwt, "room_id": user.room_id, "media_id": tconst_to_like})
                    print(Fore.MAGENTA + f"[Socket.IO] User {user.email} liked media {tconst_to_like} in room {user.room_id}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"[Socket.IO] User {user.email} failed to get recommendations in room {user.room_id}: {response.text}" + Style.RESET_ALL)

        @user.sio.on("all-liked")
        def on_all_liked(data):
            print(Fore.CYAN + f"[Socket.IO] User {user.email} received all-liked event in room {user.room_id}: {data}" + Style.RESET_ALL)
        
        #Connecting
        user.sio.connect(f"http://{base_url}", wait_timeout=5)
        #Joining room
        user.sio.emit("join", {"jwt": user.jwt, "room_id": user.room_id})
        #Starting the room event
        user.sio.emit("message-start", {"jwt": user.jwt, "room_id": user.room_id})

        time.sleep(15)  #Keep connection alive for a short period to receive events

    except Exception as e:
        print(Fore.RED + f"[Socket.IO] User {user.email} failed to connect to room {user.room_id}: {e}" + Style.RESET_ALL)       
    finally:
        if user.sio.connected:
            user.sio.disconnect()

if __name__ == "__main__":
    
    BASE_URL = sys.argv[1] if len(sys.argv) > 1 else None
    TIMEOUT = 5
    users = None
    user_base_email = "testuser"
    user_base_domain = "@example.com"
    user_base_password = "TestPassword123!"

    if BASE_URL is None:
        exit("Please provide the backend URL")
    
    print("Starting backend test...")
    print(f"Backend URL: {BASE_URL}")

    print("Creating users...\n")
    users = [User(f"{user_base_email}{i}{user_base_domain}", user_base_password) for i in range(12)]

    print("1. Registering users...")
    for user in users:
        response = requests.post(f"http://{BASE_URL}/auth/register", json={
            "email": user.email,
            "password": user.password
        })
    print(Fore.GREEN + "User registration completed.")
    print(Style.RESET_ALL)
    print("2. Logging in users...")
    for user in users:
        response = requests.post(f"http://{BASE_URL}/auth/login", json={
            "email": user.email,
            "password": user.password
        })
        if response.status_code == 200:
            user.jwt = response.json().get("jwt")
        else:
            print(Fore.RED + f"Failed to log in user {user.email}")
            print(Style.RESET_ALL)
    print(Fore.GREEN + "User login completed.")
    print(Style.RESET_ALL)

    print("3. Creating user preferences...")
    #1. Adventure and Action fans
    u1_tconst = ["tt0133093","tt0110912","tt0245429","tt0095016","tt0120737","tt0114369","tt0120815","tt0468569","tt4154796","tt1630029","tt1877830","tt3890160"]
    u1_ratings = [9,8,9,8,10,7,8,9,9,7,6,5]
    users[0].media_list = u1_tconst    
    users[0].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u1_tconst, u1_ratings)]
    users[0].liked_media_index = [0,2,4,7]

    #2. Comedy and Romance fans
    u2_tconst = ["tt0107048","tt0119217","tt0120338","tt0109830","tt0095765","tt0111161","tt0109686","tt0120815","tt0102926","tt0091042","tt0110912","tt0088763"]
    u2_ratings = [9,8,7,7,9,6,8,5,3,6,5,7]
    users[1].media_list = u2_tconst    
    users[1].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u2_tconst, u2_ratings)]
    users[1].liked_media_index = [1, 7]

    #3. Drama and biography fans
    u3_tconst = ["tt0111161","tt0109830","tt0120689","tt0120815","tt0108052","tt0112573","tt0118799","tt0102926","tt0107048","tt0119217","tt0114369","tt0137523"]
    u3_ratings = [10,9,10,9,8,8,9,7,8,9,8,9]
    users[2].media_list = u3_tconst    
    users[2].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u3_tconst, u3_ratings)]
    users[2].liked_media_index = [2,4,7]

    #4. Science Fiction and Technology
    u4_tconst = ["tt1375666","tt0468569","tt0816692","tt0133093","tt0083658","tt0080684","tt0120737","tt0114369","tt0082971","tt0086190","tt4154756","tt4154796"]
    u4_ratings = [10,9,9,8,10,8,9,6,5,7,6,7]
    users[3].media_list = u4_tconst
    users[3].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u4_tconst, u4_ratings)]
    users[3].liked_media_index = [2,4,7]

    #5. Horror and thillers
    u5_tconst = ["tt0078748","tt0081505","tt0090605","tt0102926","tt0363589","tt0054215","tt0084787","tt0114369","tt0082971","tt1457767","tt6751668","tt0479143"]
    u5_ratings = [10,8,9,9,7,9,8,8,6,7,6,5]
    users[4].media_list = u5_tconst    
    users[4].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u5_tconst, u5_ratings)]
    users[4].liked_media_index = [5]

    #6. Documentaries and real-life stories
    u6_tconst = ["tt0108052","tt0109830","tt0120689","tt0119217","tt0111161","tt0099685","tt0102926","tt0114369","tt0361748","tt10272386","tt2395427"]
    u6_ratings = [9,8,9,8,8,7,6,6,7,9,8]
    users[5].media_list = u6_tconst    
    users[5].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u6_tconst, u6_ratings)]
    users[5].liked_media_index = [5]

    #7. Animation and family-friendly content
    u7_tconst = ["tt0114709","tt0120338","tt0245429","tt0109686","tt0110357","tt0096874","tt2096673","tt0099487","tt4633694","tt0120815","tt0910970","tt4154796"]
    u7_ratings = [10,8,9,8,9,7,8,6,7,5,10,6]
    users[6].media_list = u7_tconst    
    users[6].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u7_tconst, u7_ratings)]
    users[6].liked_media_index = [5]

    #8. Sci-fi and thillers
    u8_tconst = ["tt0816692","tt1375666","tt0133093","tt0468569","tt0114369","tt0120815","tt0112359","tt0120737","tt4154796","tt0080684","tt0088763","tt0102926"]
    u8_ratings = [9,10,9,8,8,7,8,9,9,8,7,6]
    users[7].media_list = u8_tconst    
    users[7].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u8_tconst, u8_ratings)]
    users[7].liked_media_index = [5]

    #9. Action and blockbusters
    u9_tconst = ["tt0111161","tt0133093","tt0468569","tt0120338","tt0109830","tt0245429","tt0114709","tt0088763","tt0816692","tt0110912","tt0120815","tt0119217"]
    u9_ratings = [7,9,9,7,8,9,7,8,9,8,7,6]
    users[8].media_list = u9_tconst    
    users[8].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u9_tconst, u9_ratings)]
    users[8].liked_media_index = [5]

    #10. Romantic and drama
    u10_tconst = ["tt0112573","tt0120689","tt0109830","tt0111161","tt0119217","tt0108052","tt0114369","tt0120338","tt0114709","tt0118799","tt0086190","tt0093058"]
    u10_ratings = [8,9,9,10,8,9,6,7,6,8,7,6]
    users[9].media_list = u10_tconst    
    users[9].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u10_tconst, u10_ratings)]
    users[9].liked_media_index = [5]

    #11. Action and entertainment
    u11_tconst = ["tt0110912","tt0107048","tt0114709","tt0112359","tt0133093","tt0468569","tt0112573","tt0114369","tt0088763","tt0120737","tt0080684","tt4154756"]
    u11_ratings = [8,8,7,8,9,9,7,6,8,9,8,9]
    users[10].media_list = u11_tconst    
    users[10].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u11_tconst, u11_ratings)]
    users[10].liked_media_index = [5]

    #12. Adventure and sci-fi
    u12_tconst = ["tt0816692","tt0120338","tt0102536","tt0111161","tt0088763","tt0114709","tt0245429","tt0078748","tt0081505","tt0082971","tt0120737","tt0086190"]
    u12_ratings = [9,7,9,8,10,8,9,8,7,9,9,9]
    users[11].media_list = u12_tconst    
    users[11].user_media_list = [UserMedia(tconst, rating) for tconst, rating in zip(u12_tconst, u12_ratings)]
    users[11].liked_media_index = [1]

    #Submit preferences to backend
    for user in users:
        for user_media in user.user_media_list:
            response = requests.post(f"http://{BASE_URL}/preferences/add", json={
                "jwt": user.jwt,
                "tconst": user_media.tconst,
                "rating": user_media.rating
            })
            if response.status_code != 200:
                print(Fore.RED + f"Failed to submit preference for user {user.email} for media {user_media.tconst}")
                print(Style.RESET_ALL)
    print(Fore.GREEN + "User preferences creation completed.")
    print(Style.RESET_ALL)
        
    print("4. Changing user preferences...")
    user_media_review = users[0].user_media_list[0].rating
    new_rating = 2
    response = requests.post(f"http://{BASE_URL}/preferences/add", json={
        "jwt": users[0].jwt,
        "tconst": users[0].user_media_list[0].tconst,
        "rating": new_rating
    })
    if response.status_code != 200:
        print(Fore.RED + f"Failed to change preference for user {users[0].email} for media {users[0].user_media_list[0].tconst}")
        print(Style.RESET_ALL)
        exit(1)
    #Checking from backend
    response = requests.post(f"http://{BASE_URL}/media/{users[0].user_media_list[0].tconst}", json={
        "jwt": users[0].jwt
        })
    response_rating = response.json().get("media", {}).get("user_rating")
    if response_rating != new_rating:
        print(Fore.RED + f"Preference change not reflected in backend for user {users[0].email} for media {users[0].user_media_list[0].tconst}")
        print(Style.RESET_ALL)
        exit(1)
    #Revert back to original rating
    response = requests.post(f"http://{BASE_URL}/preferences/add", json={
        "jwt": users[0].jwt,
        "tconst": users[0].user_media_list[0].tconst,
        "rating": user_media_review
    })
    if response.status_code != 200:
        print(Fore.RED + f"Failed to revert preference for user {users[0].email} for media {users[0].user_media_list[0].tconst}")
        print(Style.RESET_ALL)
        exit(1)
    print(Fore.GREEN + "User preference change completed.")
    print(Style.RESET_ALL)

    print("5. Creating a room and connecting users via socket.io...")
    #Create room with first user
    room_owners = [users[0], users[4], users[8]]
    room_names = []
    for room_owner in room_owners:
        response = requests.post(f"http://{BASE_URL}/rooms/create", json={
            "jwt": room_owner.jwt
        })
        if response.status_code != 200:
            print(Fore.RED + f"Failed to create room for user {room_owner.email}")
            print(Style.RESET_ALL)
            exit(1)
        room_name = response.json().get("room_id")
        room_names.append(room_name)
    print(room_names)
    print(Fore.GREEN + "Room creation completed.")
    print(Style.RESET_ALL)
    
    print("6. Connecting users to rooms via socket.io...")
    room_1_users = users[0:4]
    room_2_users = users[4:8]
    room_3_users = users[8:12]

    #Connecting via REST API
    for room_1_user in room_1_users:
        response = requests.post(f"http://{BASE_URL}/rooms/join", json={
            "jwt": room_1_user.jwt,
            "room_id": room_names[0]
        })
        if response.status_code != 200 and response.status_code != 400:
            print(Fore.RED + f"Failed to join room for user {room_1_user.email}")
            print(Style.RESET_ALL)
            exit(1)
        elif response.status_code == 400:
            print(Fore.YELLOW + f"User {room_1_user.email} already in room {room_names[0]}")
            print(Style.RESET_ALL)
        room_1_user.room_id = room_names[0]
    for room_2_user in room_2_users:
        response = requests.post(f"http://{BASE_URL}/rooms/join", json={
            "jwt": room_2_user.jwt,
            "room_id": room_names[1]
        })
        if response.status_code != 200 and response.status_code != 400:
            print(Fore.RED + f"Failed to join room for user {room_2_user.email}")
            print(Style.RESET_ALL)
            exit(1)
        elif response.status_code == 400:
            print(Fore.YELLOW + f"User {room_2_user.email} already in room {room_names[1]}")
            print(Style.RESET_ALL)
        room_2_user.room_id = room_names[1]
    for room_3_user in room_3_users:
        response = requests.post(f"http://{BASE_URL}/rooms/join", json={
            "jwt": room_3_user.jwt,
            "room_id": room_names[2]
        })
        if response.status_code != 200 and response.status_code != 400:
            print(Fore.RED + f"Failed to join room for user {room_3_user.email}")
            print(Style.RESET_ALL)
            exit(1)
        elif response.status_code == 400:
            print(Fore.YELLOW + f"User {room_3_user.email} already in room {room_names[2]}")
            print(Style.RESET_ALL)
        room_3_user.room_id = room_names[2]
    print(Fore.GREEN + "Users joined rooms via REST API completed.")
    print(Style.RESET_ALL)

    #Connecting via Socket.IO
    user_threads = []
    for user in users:
        thread = threading.Thread(target=connect_user_socket, args=(user, BASE_URL))
        thread.start()
        user_threads.append(thread)
        time.sleep(0.1)  #Staggered connection to avoid overload

    for thread in user_threads:
        thread.join()

    #Comparing recommendations received in rooms
    if users[0].recommendations_from_room == users[1].recommendations_from_room == users[2].recommendations_from_room == users[3].recommendations_from_room:
        print(Fore.GREEN + "Room 1 recommendations are consistent among users." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Room 1 recommendations are NOT consistent among users!" + Style.RESET_ALL)
    if users[4].recommendations_from_room == users[5].recommendations_from_room == users[6].recommendations_from_room == users[7].recommendations_from_room:
        print(Fore.GREEN + "Room 2 recommendations are consistent among users." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Room 2 recommendations are NOT consistent among users!" + Style.RESET_ALL)
    if users[8].recommendations_from_room == users[9].recommendations_from_room == users[10].recommendations_from_room == users[11].recommendations_from_room:
        print(Fore.GREEN + "Room 3 recommendations are consistent among users." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Room 3 recommendations are NOT consistent among users!" + Style.RESET_ALL)
    print(Fore.GREEN + "Users connected to rooms via Socket.IO completed.")
    print(Style.RESET_ALL)

    print(f"Room one recommendation size: {len(users[0].recommendations_from_room)}\n"
        f"Room two recommendation size: {len(users[4].recommendations_from_room)}\n"
        f"Room three recommendation size: {len(users[8].recommendations_from_room)}\n")

    for user in users[0:12]:
        list_of_categories = []
        liked_genre_counter = user.get_user_category_stats()
        recommendation_genre_counter = user.get_user_recommendation_category_stats()
        print(Fore.BLUE + f"User {user.email} cosinus: {compute_accuracy(liked_genre_counter,recommendation_genre_counter)}, NDCG@K: {ndcg_at_k_genres(liked_genre_counter,recommendation_genre_counter, 10)}" + Style.RESET_ALL)