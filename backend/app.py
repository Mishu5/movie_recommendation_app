from flask import Flask, jsonify, request
from db.create_tables import create_tables, check_and_add_media, check_and_add_reviews, check_and_add_creators
from db.users import add_user, get_user
import os
import jwt
import datetime
import hashlib
import string
import random
from threading import Timer
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from db.media import get_all_genres, get_media_by_tconst
from recommendation.knn_recommendation import train_knns, delete_cache, recommend_media
from db.user_preferences import add_and_update_user_preference, get_user_preferences

rooms = {} #List of rooms that users can interact with

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")
socketio = SocketIO(app) #creating socketio instance

def verify_jwt(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/')
def hello_world():
    return jsonify({"message": "Hello, World!"})

#Register
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    #hashing password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    res = add_user(email=email, password=hashed_password)
    if res:
        return ({"message": "Register sucessfully"}), 200
    return({"message": "User exists"}), 401

#Login
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    #getting user
    user = get_user(email)

    #checking credentials
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password != user.password:
        return jsonify({"message": "Invalid email or password"}), 401

    #generating JWT
    token = jwt.encode(
        {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24) #JWT valid for 24h
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    return jsonify({"message": "Login sucessful", "jwt": token}), 200

#Add preferences
@app.route('/preferences/add', methods=['POST'])
def add_preference():
    data = request.get_json()
    token = data.get('jwt')
    tconst = data.get('tconst')
    rating = data.get('rating')
    user_id = None

    if not token:
        return jsonify({"message": "JWT is required"}), 400
    if not tconst:
        return jsonify({"message": "tconst is required"}), 400
    if not rating: 
        return jsonify({"message": "rating is required"}), 400
    
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    res = add_and_update_user_preference(user_id, tconst, rating)
    
    if res:
        return jsonify({"message": "Preference added"}), 200
    else:
        return jsonify({"message": "Error adding preference"}), 500

#Get all preferences 
@app.route('/preferences/get_all', methods=['GET'])
def get_preferences():
    data = request.get_json()
    token = data.get('jwt')
    user_id = None

    if not token:
        return jsonify({"message": "JWT is required"}), 400
    
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    res = get_user_preferences(user_id)
    
    if res:
        return jsonify({"preferences": res}), 200
    else:
        return jsonify({"message": "Error fetching preferences"}), 500

#Create room
@app.route('/rooms/create', methods=['POST'])
def create_room():
    data = request.get_json()
    token = data.get('jwt')
    room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 8)) #generating random room id

    if not token:
        return jsonify({"message": "JWT and room name are required"}), 400

    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
    
    if room_id in rooms:
        return jsonify({"message": "Room already exists"}), 400
    
    rooms[room_id] = {
        "creator": user_id,
        "members": [],
        "active": False,
        "recommended_media": [],
        "liked_media": {},
        "created_at": datetime.datetime.now(),
    }
    rooms[room_id]["members"].append(user_id)

    Timer(86400, expire_room, args=[room_id]).start()
    return jsonify({"message": "Room created", "room_id": room_id}), 200

#Join room
@app.route('/rooms/join', methods=['POST'])
def joint_room_endpoint():
    data = request.get_json()
    token = data.get('jwt')
    room_id = data.get('room_id')
    user_id = None

    if not token or not room_id:
        return jsonify({"message": "JWT and room id are required"}), 400
    
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    if room_id not in rooms or rooms[room_id]["active"]:
        return jsonify({"message": "Room does not exist or does not accept invites anymore"}), 400

    if user_id in rooms[room_id]["members"]:
        return jsonify({"message": "User is already in the room"}), 400
    rooms[room_id]["members"].append(user_id)
    return jsonify({"message": "User joined the room"}), 200

#Get recommendations
@app.route('/recommendations/get', methods=['POST'])
def get_recommendations():
    data = request.get_json()
    token = data.get('jwt')
    user_id = None

    if not token:
        return jsonify({"message": "JWT is required"}), 400
    
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

    if not user_id:
        return jsonify({"message": "User not found"}), 404

    recommendations = recommend_media(user_id)

    return jsonify({"recommendations": recommendations}), 200

#Join room socket
@socketio.on('join')
def handle_join(data):
    room_id = data.get('room_id')
    user_id = verify_jwt(data.get('jwt'))
    if not user_id:
        return
    
    if room_id in rooms and user_id in rooms[room_id]["members"]:
        join_room(room_id) #User join room
        print(f'User has entered the room: {room_id}')

#Leave room socket
@socketio.on('leave')
def handle_leave(data):
    room_id = data.get('room_id')
    user_id = verify_jwt(data.get('jwt'))
    if not user_id:
        return
    
    if room_id in rooms and user_id in rooms[room_id]["members"]:
        leave_room(room_id)
        print(f'User has left the room: {room_id}')

#Handle start room
@socketio.on('message-start')
def handle_start(data):
    room_id = data.get('room_id')
    user_id = verify_jwt(data.get('jwt'))
    if not user_id:
        return

    if room_id in rooms and user_id == rooms[room_id]["creator"]:
        rooms[room_id]["active"] = True
        rooms[room_id]["recommended_media"] = create_recommendation_list(rooms[room_id]["members"])
        emit('message-start', {'message': 'Room has started'}, room=room_id)
        print('Room has started: {room_id}')

#Handle like media
@socketio.on('message-like')
def handle_like(data):
    room_id = data.get('room_id')
    user_id = verify_jwt(data.get('jwt'))
    if not user_id:
        return
    
    if room_id in rooms and user_id in rooms[room_id]["members"]:
        media_id = data.get('media_id')
        
        if media_id not in rooms[room_id]["liked_media"]:
            rooms[room_id]["liked_media"][media_id] = set()
        
        rooms[room_id]["liked_media"][media_id].add(user_id)
        print(f'Media {media_id} has been liked in room {room_id}')
        
        #Check if all users have liked the media
        if rooms[room_id]["liked_media"][media_id] == set(rooms[room_id]["members"]):
            emit('all-liked', {'media_id': media_id}, room=room_id)
            print(f'Media {media_id} has been selected in room {room_id}')


def expire_room(room_id):
    if room_id in rooms:
        del rooms[room_id]
        print(f"Room {room_id} has expired and been removed")

def create_recommendation_list(members):
    recommendation_list = []
    
    return recommendation_list


if __name__ == '__main__':
    create_tables()
    delete_cache()
    check_and_add_media()
    check_and_add_reviews()
    check_and_add_creators()
    train_knns()
    
    #Testing of knn
    user = get_user("test@gmail.com")
  
    #List of sample medias with Animation genre
    media_list = ["tt0000003",
"tt0000004",
"tt0000015",
"tt0000233",
"tt0000251",
"tt0000300",
"tt0000516",
"tt0000552",
"tt0000553",
"tt0000554",
"tt0000565",
"tt0000603",
"tt0000603",
"tt0000658",
"tt0000682",
"tt0000704",
"tt0000756",
"tt0000924",
"tt0001218",
"tt0001527",
"tt0001737",
"tt0002056",
"tt0002226",
"tt0002260",
"tt0002641",
"tt0002650",
"tt0002657",
"tt0002666",
"tt0002695",
"tt0002720",
"tt0002731",
"tt0002740",
"tt0002754",
"tt0002760",
"tt0002778",
"tt0002834",
"tt0002896",
"tt0002908",
"tt0002929",
"tt0002995",
"tt0003031",
"tt0003129",
"tt0003130",
"tt0003137",
"tt0003148",
"tt0003166",
"tt0003179",
"tt0003180",
"tt0003181",
"tt0003182",
"tt0003138",
]
    if not user:
        add_user("test@gmail.com", "password")
        user = get_user("test@gmail.com")
        for media in media_list:
            add_and_update_user_preference(user.id, media, random.uniform(5, 10))
    media, distances = recommend_media(user.id, 100)
    count = 0
    for m, n in zip(media, distances):
        media = get_media_by_tconst(m)
        count += 1
        if m in media_list:
            print(f"\033[91mMedia: {m}, Title: {media.primaryTitle}, Genres: {media.genres}, Distance: {n}\033[0m")
        else:
            print(f"Media: {m}, Title: {media.primaryTitle}, Genres: {media.genres}, Distance: {n}")
            
    print(f"Media count: {count}")
    #End of test

    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
