import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/voice_ecommerce")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
