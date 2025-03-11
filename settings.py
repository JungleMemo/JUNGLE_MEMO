from pymongo import MongoClient

class Config:
    MONGO_URI = "mongodb://localhost:27017/flask_auth"
    SECRET_KEY = "supersecretkey"  # Flask 시크릿 키
    JWT_SECRET_KEY = "jwtsecretkey"  # JWT 시크릿 키

# MongoDB 연결
client = MongoClient(Config.MONGO_URI)
db = client["memo3"]