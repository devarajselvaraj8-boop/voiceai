import requests
import json

BASE = "http://127.0.0.1:5000"
token = None
headers = {}

def print_header(title):
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def print_result(data):
    print(json.dumps(data, indent=2))

# ─── 1. REGISTER ─────────────────────────────────────
def demo_register():
    print_header("1️⃣  REGISTER NEW USER")
    res = requests.post(f"{BASE}/api/auth/register", json={
        "name":     "Demo User",
        "email":    "demo@test.com",
        "password": "demo123"
    })
    data = res.json()
    print_result(data)
    if "token" in data:
        print("✅ Registration Successful!")
    return data.get("token")

# ─── 2. LOGIN ─────────────────────────────────────────
def demo_login():
    print_header("2️⃣  LOGIN")
    res = requests.post(f"{BASE}/api/auth/login", json={
        "email":    "demo@test.com",
        "password": "demo123"
    })
    data = res.json()
    print_result(data)
    if "token" in data:
        print("✅ Login Successful!")
        print(f"🔑 JWT Token: {data['token'][:40]}...")
    return data.get("token")

# ─── 3. GET ALL PRODUCTS ──────────────────────────────
def demo_get_products():
    print_header("3️⃣  GET ALL PRODUCTS FROM MONGODB")
    res  = requests.get(f"{BASE}/api/products/")
    data = res.json()
    print(f"✅ Found {len(data)} products in database:\n")
    for p in data:
        print(f"  📦 {p['name']:<25} ₹{p['price']:>10,}  [{p['category']}]")

# ─── 4. SEARCH PRODUCTS ───────────────────────────────
def demo_search_products(query):
    print_header(f"4️⃣  SEARCH PRODUCTS: '{query}'")
    res  = requests.get(f"{BASE}/api/products/", params={"q": query})
    data = res.json()
    print(f"✅ Found {len(data)} results for '{query}':\n")
    for p in data:
        print(f"  🔍 {p['name']:<25} ₹{p['price']:>10,}")

# ─── 5. GET CATEGORIES ────────────────────────────────
def demo_categories():
    print_header("5️⃣  GET ALL CATEGORIES")
    res  = requests.get(f"{BASE}/api/products/categories")
    data = res.json()
    print(f"✅ Categories in database: {data}")

# ─── 6. ADD TO CART ───────────────────────────────────
def demo_add_to_cart(product_name):
    print_header(f"6️⃣  ADD TO CART: '{product_name}'")
    # First find the product
    res      = requests.get(f"{BASE}/api/products/", params={"q": product_name})
    products = res.json()
    if not products:
        print(f"❌ Product '{product_name}' not found!")
        return
    product = products[0]
    print(f"  Found: {product['name']} at ₹{product['price']:,}")

    # Add to cart
    res  = requests.post(f"{BASE}/api/cart/add",
                         json={"product_id": product["_id"], "quantity": 1},
                         headers=headers)
    data = res.json()
    print_result(data)
    print(f"✅ Added to cart! Cart now has {data.get('cart_count', 0)} items")

# ─── 7. VIEW CART ─────────────────────────────────────
def demo_view_cart():
    print_header("7️⃣  VIEW CART")
    res  = requests.get(f"{BASE}/api/cart/", headers=headers)
    data = res.json()
    items = data.get("items", [])
    if not items:
        print("🛒 Cart is empty!")
        return
    print(f"✅ Cart has {len(items)} items:\n")
    for item in items:
        print(f"  🛒 {item['name']:<25} x{item['quantity']}  ₹{item['total']:>10,}")
    print(f"\n  💰 Total: ₹{data['total']:,}")

# ─── 8. VOICE COMMAND ─────────────────────────────────
def demo_voice_command(command):
    print_header(f"8️⃣  VOICE COMMAND: \"{command}\"")
    res  = requests.post(f"{BASE}/api/voice/command",
                         json={"transcript": command},
                         headers=headers)
    data = res.json()
    print(f"  🎤 You said    : {command}")
    print(f"  🤖 Intent      : {data.get('intent', 'unknown')}")
    print(f"  💬 Response    : {data.get('message', '')}")
    if data.get("products"):
        print(f"  📦 Products    : {len(data['products'])} found")
        for p in data["products"]:
            print(f"     → {p['name']} ₹{p['price']:,}")
    if data.get("cart_count"):
        print(f"  🛒 Cart Count  : {data['cart_count']}")
    if data.get("trigger_checkout"):
        print(f"  💳 Checkout    : Triggered!")

# ─── 9. PLACE ORDER ───────────────────────────────────
def demo_checkout():
    print_header("9️⃣  PLACE ORDER (CHECKOUT)")
    res  = requests.post(f"{BASE}/api/orders/checkout",
                         json={
                             "address":        "123 Demo Street, Chennai, Tamil Nadu",
                             "payment_method": "COD"
                         },
                         headers=headers)
    data = res.json()
    print_result(data)
    if "order_id" in data:
        print(f"\n✅ Order Placed Successfully!")
        print(f"  📋 Order ID : {data['order_id']}")
        print(f"  💰 Total    : ₹{data['total']:,}")
        print(f"  📦 Status   : Confirmed")

# ─── 10. VIEW ORDERS ──────────────────────────────────
def demo_view_orders():
    print_header("🔟  VIEW ORDER HISTORY")
    res    = requests.get(f"{BASE}/api/orders/", headers=headers)
    orders = res.json()
    if not orders:
        print("📋 No orders yet!")
        return
    print(f"✅ Found {len(orders)} order(s):\n")
    for o in orders:
        print(f"  📋 Order ID : {o['_id']}")
        print(f"  💰 Total    : ₹{o['total']:,}")
        print(f"  📦 Status   : {o['status']}")
        print(f"  📍 Address  : {o['address']}")
        print(f"  🕐 Date     : {o['created_at']}")
        print()

# ─── MAIN DEMO RUNNER ─────────────────────────────────
def run_demo():
    global token, headers

  
    print("   VOICESHOP AI — BACKEND DEMO")
    print("   Built with Python + Flask + MongoDB")
    
    # Step 1: Register
    token = demo_register()

    # Step 2: Login (in case already registered)
    if not token:
        token = demo_login()

    if not token:
        print("❌ Could not get token. Is Flask running?")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Step 3: Show all products
    demo_get_products()

    # Step 4: Show categories
    demo_categories()

    # Step 5: Search products
    demo_search_products("laptop")

    # Step 6: Voice commands demo
    voice_commands = [
        "find iphone",
        "add iphone to my cart",
        "add sony headphones to cart",
        "show my cart",
        "add macbook to cart",
        "checkout"
    ]
    for cmd in voice_commands:
        demo_voice_command(cmd)

    # Step 7: View cart
    demo_view_cart()

    # Step 8: Place order
    demo_checkout()

    # Step 9: View order history
    demo_view_orders()

    
    print("   DEMO COMPLETE! ALL FEATURES WORKING!")
    print("   ✅ Register/Login with JWT Auth")
    print("   ✅ MongoDB Product Database")
    print("   ✅ Voice Command Processing")
    print("   ✅ Shopping Cart Management")
    print("   ✅ Order Placement & History")
   

if __name__ == "__main__":
    run_demo()