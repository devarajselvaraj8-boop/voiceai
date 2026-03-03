from app import create_app
from extensions import mongo

PRODUCTS = [
    {"name":"iPhone 15 Pro","category":"Electronics","price":134900,
     "image":"https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-1inch_AV1?wid=300&hei=300",
     "tags":["iphone","phone","apple","smartphone"]},
    {"name":"Samsung Galaxy S24","category":"Electronics","price":79999,
     "image":"https://images.samsung.com/is/image/samsung/p6pim/in/2401/gallery/in-galaxy-s24-s928-sm-s928bzkgins-thumb-539573119?$344_344_PNG$",
     "tags":["samsung","phone","android","smartphone"]},
    {"name":"Nike Air Max 270","category":"Shoes","price":9995,
     "image":"https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/skwgyqrbfzhu6uyeh0gg/air-max-270-shoes-2v5C4A.png",
     "tags":["nike","shoes","sneakers","running"]},
    {"name":"Adidas Ultraboost 22","category":"Shoes","price":12999,
     "image":"https://assets.adidas.com/images/w_600,f_auto,q_auto/16655690b5f64574b6c1ad620102b9ef_9366/Ultraboost_22_Shoes_Black_GZ0127_01_standard.jpg",
     "tags":["adidas","shoes","running","sneakers"]},
    {"name":"Sony WH-1000XM5","category":"Audio","price":29990,
     "image":"https://www.sony.co.in/image/5d02da5df552836db8bb5234356b4f6d?fmt=pjpeg&wid=300&bgcolor=FFFFFF",
     "tags":["sony","headphones","wireless","audio"]},
    {"name":"boAt Rockerz 450","category":"Audio","price":1499,
     "image":"https://www.boat-lifestyle.com/cdn/shop/products/Rockerz450_1_1800x1800.jpg?v=1649062080&width=300",
     "tags":["boat","headphones","bluetooth","audio"]},
    {"name":"MacBook Pro M3","category":"Laptops","price":199900,
     "image":"https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-m3-pro-max-spacegray-select-202310?wid=300&hei=300",
     "tags":["apple","macbook","laptop","mac"]},
    {"name":"Dell XPS 15","category":"Laptops","price":149999,
     "image":"https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-9530/media-gallery/black/laptop-xps-15-9530-t-black-gallery-1.psd?fmt=pjpg&pscan=auto&scl=1&wid=300&hei=300",
     "tags":["dell","laptop","windows","xps"]},
]

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        mongo.db.products.delete_many({})
        mongo.db.products.insert_many(PRODUCTS)
        print(f"✅ Seeded {len(PRODUCTS)} products!")