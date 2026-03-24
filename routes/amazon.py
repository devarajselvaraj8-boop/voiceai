from flask import Blueprint, request, jsonify
from amazon_paapi import AmazonApi

amazon_bp = Blueprint('amazon', __name__)

# Your Amazon credentials
AMAZON = AmazonApi(
    key        = "YOUR_ACCESS_KEY",
    secret     = "YOUR_SECRET_KEY",
    tag        = "YOUR_PARTNER_TAG",
    country    = "IN"
)

@amazon_bp.route('/search', methods=['GET'])
def search_amazon():
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No query'}), 400
    try:
        results = AMAZON.search_items(keywords=query, item_count=6)
        products = []
        for item in results.items:
            products.append({
                'name':   item.item_info.title.display_value,
                'price':  item.offers.listings[0].price.amount if item.offers else 0,
                'image':  item.images.primary.medium.url if item.images else '',
                'url':    item.detail_page_url,
                'source': 'amazon'
            })
        return jsonify(products)
    except Exception as e:
        return jsonify({'error': str(e)}), 500