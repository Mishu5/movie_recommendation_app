from flask import Flask, jsonify
from db.create_tables import create_tables
from db.add_user import add_user
import os

app = Flask(__name__)

create_tables()

@app.route('/')
def hello_world():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
