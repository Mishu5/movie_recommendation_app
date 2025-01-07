from flask import Flask, jsonify, request
from db.create_tables import create_tables, check_and_add_media, check_and_add_reviews
from db.users import add_user, get_user
import os
import jwt
import datetime
import hashlib

from db.media import get_all_genres
from recommendation.knn_recommendation import get_media_features

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

    return jsonify({"message": "Login sucessful", "token": token}), 200
    


if __name__ == '__main__':
    create_tables()
    check_and_add_media()
    check_and_add_reviews()
    #media_features, media_ids = get_media_features()
    app.run(host='0.0.0.0', port=5000)
