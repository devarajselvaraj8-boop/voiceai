from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import mongo
from bson import ObjectId

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    cart = user.get('cart', [])
    # Enrich with product details
    enriched = []
    for item in cart:
        product = mongo.db.products.find_one({'_id': ObjectId(item['product_id'])})
        if product:
            enriched.append({
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'name': product['name'],
                'price': product['price'],
                'image': product.get('image', ''),
                'total': product['price'] * item['quantity']
            })
    total = sum(i['total'] for i in enriched)
    return jsonify({'items': enriched, 'total': round(total, 2)})

@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json
    product_id = data['product_id']
    quantity = int(data.get('quantity', 1))

    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    cart = user.get('cart', [])
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'product_id': product_id, 'quantity': quantity})

    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'cart': cart}}
    )
    return jsonify({'message': 'Added to cart', 'cart_count': len(cart)})

@cart_bp.route('/remove/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    user_id = get_jwt_identity()
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'cart': {'product_id': product_id}}}
    )
    return jsonify({'message': 'Removed from cart'})

@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_id = get_jwt_identity()
    mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'cart': []}})
    return jsonify({'message': 'Cart cleared'})