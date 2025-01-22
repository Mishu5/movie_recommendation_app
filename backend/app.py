from flask import Flask, jsonify, request
from db.create_tables import create_tables, check_and_add_media, check_and_add_reviews
from db.users import add_user, get_user
import os
import jwt
import datetime
import hashlib
import string
import random
from threading import Timer

from db.media import get_all_genres
from recommendation.knn_recommendation import get_media_features, train_knn, delete_cache
from db.user_preferences import add_and_update_user_preference, get_user_preferences

rooms = {} #List of rooms that users can interact with

app = Flask(__name__)
SECRET_KEY = os.getenv("SECRET_KEY")

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
    
@app.route('/add_preferences/add', methods=['POST'])
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


if __name__ == '__main__':
    create_tables()
    check_and_add_media()
    check_and_add_reviews()
    media_features, media_ids = get_media_features()
    train_knn(media_features)
    app.run(host='0.0.0.0', port=5000)
