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

from db.media import get_all_genres
from recommendation.knn_recommendation import get_media_features, train_knn, delete_cache, recommend_media
from db.user_preferences import add_and_update_user_preference, get_user_preferences

rooms = {} #List of rooms that users can interact with

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")
socketio = SocketIO(app) #creating socketio instance

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
        "created_at": datetime.datetime.now(),
    }
    rooms[room_id]["members"].append(user_id)

    Timer(86400, expire_room, args=[room_id]).start()
    return jsonify({"message": "Room created", "room_id": room_id}), 200

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

#TODO Convert to message-start
@app.route('/rooms/start', methods=['POST'])
def start_room():
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

    if room_id not in rooms:
        return jsonify({"message": "Room does not exist"}), 400

    if user_id != rooms[room_id]["creator"]:
        return jsonify({"message": "User is not the creator of the room"}), 400

    if len(rooms[room_id]["members"]) < 2:
        return jsonify({"message": "Not enough members in the room"}), 400

    rooms[room_id]["active"] = True
    return jsonify({"message": "Room started"}), 200

@app.route('/recommendations/get/<int:num_recommendations>', methods=['POST'])
def get_recommendations(num_recommendations):
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

    recommendations = recommend_media(user_id, num_recommendations)

    return jsonify({"recommendations": recommendations}), 200

@socketio.on('join')
def handle_join(data):
    room_id = data.get('room_id')
    user_id = data.get('user_id')
    if room_id in rooms and user_id in rooms[room_id]["members"]:
        join_room(room_id) #User join room
        send('User has entered the room', room=room_id)

def expire_room(room_id):
    if room_id in rooms:
        del rooms[room_id]
        print(f"Room {room_id} has expired and been removed")

def create_recommendation_list(members):
    recommendation_list = []
    
    return recommendation_list


if __name__ == '__main__':
    create_tables()
    check_and_add_media()
    check_and_add_reviews()
    check_and_add_creators()
    delete_cache()
    # media_features, media_ids = get_media_features()
    # train_knn(media_features)
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
