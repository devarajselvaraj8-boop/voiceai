from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import mongo, jwt
from routes.auth import auth_bp
from routes.products import products_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.voice import voice_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    mongo.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp,     url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp,     url_prefix='/api/cart')
    app.register_blueprint(orders_bp,   url_prefix='/api/orders')
    app.register_blueprint(voice_bp,    url_prefix='/api/voice')

    @app.route('/')
    def index():
        return send_from_directory('templates', 'index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)