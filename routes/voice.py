from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import mongo
from bson import ObjectId
import re

voice_bp = Blueprint('voice', __name__)

def extract_quantity(text):
    numbers = {'one':1,'two':2,'three':3,'four':4,'five':5}
    for word, num in numbers.items():
        if word in text.lower():
            return num
    match = re.search(r'\b(\d+)\b', text)
    return int(match.group(1)) if match else 1

def find_product(pname):
    if not pname:
        return None
    return mongo.db.products.find_one({
        '$or': [
            {'name':     {'$regex': pname, '$options': 'i'}},
            {'category': {'$regex': pname, '$options': 'i'}},
            {'tags':     {'$in':    [pname.lower()]}}
        ]
    })

@voice_bp.route('/command', methods=['POST'])
@jwt_required()
def command():
    uid        = get_jwt_identity()
    transcript = request.json.get('transcript', '').strip()
    t          = transcript.lower()
    print(f"[VOICE] Received: {transcript}")

    # ────────────────────────────────────────────────────
    # 1. ADD TO CART  (checked FIRST before anything else)
    # ────────────────────────────────────────────────────
    if any(w in t for w in ['add','put','buy','want','get','order']):
        print("[VOICE] Intent: add_to_cart")
        clean = re.sub(
            r'\b(add|put|buy|want|get|order|to|my|cart|please|in|the|a|an|i|me|into|this)\b',
            '', t
        ).strip()
        print(f"[VOICE] Product keyword: '{clean}'")
        qty = extract_quantity(t)
        p   = find_product(clean)
        if p:
            pid  = str(p['_id'])
            user = mongo.db.users.find_one({'_id': ObjectId(uid)})
            cart = user.get('cart', [])
            for item in cart:
                if item['product_id'] == pid:
                    item['quantity'] += qty
                    break
            else:
                cart.append({'product_id': pid, 'quantity': qty})
            mongo.db.users.update_one(
                {'_id': ObjectId(uid)},
                {'$set': {'cart': cart}}
            )
            print(f"[VOICE] ✅ Added {p['name']} x{qty} to cart")
            return jsonify({
                'intent':     'add_to_cart',
                'message':    f"✅ Added {qty} × {p['name']} to your cart!",
                'cart_count': len(cart)
            })
        else:
            print(f"[VOICE] ❌ Product not found: {clean}")
            return jsonify({
                'intent':  'add_to_cart',
                'message': f"❌ Sorry, could not find '{clean}' in our store."
            })

    # ────────────────────────────────────────────────────
    # 2. REMOVE FROM CART
    # ────────────────────────────────────────────────────
    if any(w in t for w in ['remove','delete','take out']):
        print("[VOICE] Intent: remove_from_cart")
        clean = re.sub(
            r'\b(remove|delete|take|out|from|cart|my|the|please|i|want|to)\b',
            '', t
        ).strip()
        user     = mongo.db.users.find_one({'_id': ObjectId(uid)})
        cart     = user.get('cart', [])
        new_cart = []
        removed  = False
        for item in cart:
            p = mongo.db.products.find_one({'_id': ObjectId(item['product_id'])})
            if p and clean in p['name'].lower():
                removed = True
            else:
                new_cart.append(item)
        mongo.db.users.update_one(
            {'_id': ObjectId(uid)},
            {'$set': {'cart': new_cart}}
        )
        msg = f"✅ Removed from cart!" if removed else f"❌ Item '{clean}' not found in cart."
        return jsonify({
            'intent':     'remove_from_cart',
            'message':    msg,
            'cart_count': len(new_cart)
        })

    # ────────────────────────────────────────────────────
    # 3. CHECKOUT
    # ────────────────────────────────────────────────────
    if any(w in t for w in ['checkout','place order','buy now','proceed','payment','order now']):
        print("[VOICE] Intent: checkout")
        return jsonify({
            'intent':           'checkout',
            'trigger_checkout': True,
            'message':          '🚀 Opening checkout for you!'
        })

    # ────────────────────────────────────────────────────
    # 4. VIEW CART
    # ────────────────────────────────────────────────────
    if any(w in t for w in ['show cart','view cart','what is in','how many','open cart','my cart']):
        print("[VOICE] Intent: view_cart")
        user  = mongo.db.users.find_one({'_id': ObjectId(uid)})
        cart  = user.get('cart', [])
        total = 0
        for i in cart:
            p = mongo.db.products.find_one({'_id': ObjectId(i['product_id'])})
            if p:
                total += p['price'] * i['quantity']
        msg = (
            f"🛒 You have {len(cart)} items totalling ₹{round(total, 2)}"
            if cart else
            "🛒 Your cart is empty!"
        )
        return jsonify({
            'intent':     'view_cart',
            'message':    msg,
            'cart_total': round(total, 2)
        })

    # ────────────────────────────────────────────────────
    # 5. SEARCH PRODUCTS (default)
    # ────────────────────────────────────────────────────
    print("[VOICE] Intent: search_products")
    clean = re.sub(
        r'\b(show|find|search|look|display|for|me|all|some|please|products|items|give|list)\b',
        '', t
    ).strip()
    print(f"[VOICE] Search keyword: '{clean}'")

    if clean:
        products = list(mongo.db.products.find({
            '$or': [
                {'name':     {'$regex': clean, '$options': 'i'}},
                {'category': {'$regex': clean, '$options': 'i'}},
                {'tags':     {'$in':    [clean]}}
            ]
        }).limit(8))
    else:
        products = list(mongo.db.products.find().limit(8))

    for p in products:
        p['_id'] = str(p['_id'])

    msg = (
        f"🔍 Found {len(products)} results for '{clean}'!"
        if products else
        f"❌ No products found for '{clean}'"
    )
    return jsonify({
        'intent':   'search_products',
        'products': products,
        'message':  msg
    })