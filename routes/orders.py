from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import mongo
from bson import ObjectId
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    user_id = get_jwt_identity()
    data = request.json  # { address, payment_method }
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    cart = user.get('cart', [])
    if not cart:
        return jsonify({'error': 'Cart is empty'}), 400

    # Build order items
    items = []
    total = 0
    for item in cart:
        product = mongo.db.products.find_one({'_id': ObjectId(item['product_id'])})
        if product:
            line = {
                'product_id': item['product_id'],
                'name': product['name'],
                'price': product['price'],
                'quantity': item['quantity'],
                'subtotal': product['price'] * item['quantity']
            }
            items.append(line)
            total += line['subtotal']

    order = {
        'user_id': user_id,
        'items': items,
        'total': round(total, 2),
        'address': data.get('address', ''),
        'payment_method': data.get('payment_method', 'COD'),
        'status': 'confirmed',
        'created_at': datetime.utcnow().isoformat()
    }
    result = mongo.db.orders.insert_one(order)
    # Clear cart
    mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': {'cart': []}})

    return jsonify({'message': 'Order placed!', 'order_id': str(result.inserted_id), 'total': order['total']}), 201

@orders_bp.route('/', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    orders = list(mongo.db.orders.find({'user_id': user_id}))
    for o in orders:
        o['_id'] = str(o['_id'])
    return jsonify(orders)