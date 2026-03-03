from flask import Blueprint, request, jsonify
from extensions import mongo
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if mongo.db.users.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already exists'}), 400

    hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt())
    user = {
        'name': data['name'],
        'email': data['email'],
        'password': hashed,
        'cart': [],
        'orders': []
    }
    result = mongo.db.users.insert_one(user)
    token = create_access_token(identity=str(result.inserted_id))
    return jsonify({'token': token, 'name': data['name']}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = mongo.db.users.find_one({'email': data['email']})
    if not user or not bcrypt.checkpw(data['password'].encode(), user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    token = create_access_token(identity=str(user['_id']))
    return jsonify({'token': token, 'name': user['name']}), 200
