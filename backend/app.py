from flask import Flask, jsonify, request
from db.create_tables import create_tables, check_and_add_media, check_and_add_reviews
from db.users import add_user, get_user
import os
import jwt
import datetime
import hashlib

from db.media import get_all_genres
from recommendation.knn_recommendation import get_media_features, train_knn, delete_cache
from db.user_preferences import add_and_update_user_preference, get_user_preferences

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

if __name__ == '__main__':
    create_tables()
    check_and_add_media()
    check_and_add_reviews()
    media_features, media_ids = get_media_features()
    train_knn(media_features)
    app.run(host='0.0.0.0', port=5000)
