import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from app import create_app
from config import Config
from dotenv import load_dotenv

load_dotenv()
app = create_app()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    from flask import send_from_directory
    if path != '' and os.path.exists('static/' + path):
        return send_from_directory('static', path)
    return send_from_directory('templates', 'index.html')

module = app
