from pymongo import MongoClient

class Config:
    MONGO_URI = "mongodb://localhost:27017/"  # 로컬 MongoDB

# MongoDB 연결
client = MongoClient(Config.MONGO_URI)

# ✅ 사용할 데이터베이스 지정 (예: user_db)
db = client["user_db"]
