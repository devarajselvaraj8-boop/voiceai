from flask import Blueprint, request, jsonify
from extensions import mongo
from bson import ObjectId

products_bp = Blueprint('products', __name__)

def serialize(product):
    product['_id'] = str(product['_id'])
    return product

@products_bp.route('/', methods=['GET'])
def get_products():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    filters = {}
    if query:
        filters['$or'] = [
            {'name': {'$regex': query, '$options': 'i'}},
            {'description': {'$regex': query, '$options': 'i'}},
            {'tags': {'$in': [query.lower()]}}
        ]
    if category:
        filters['category'] = {'$regex': category, '$options': 'i'}
    products = list(mongo.db.products.find(filters))
    return jsonify([serialize(p) for p in products])

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
    if not product:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(serialize(product))

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = mongo.db.products.distinct('category')
    return jsonify(categories)