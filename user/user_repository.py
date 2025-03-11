from config import db

class UserRepository:
    collection = db["users"]  # MongoDB의 'users' 컬렉션

    @staticmethod
    def find_by_email(email):
        return UserRepository.collection.find_one({"email": email})

    @staticmethod
    def create_user(username, email, hashed_password):
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password
        }
        result = UserRepository.collection.insert_one(new_user)
        return result.inserted_id

    @staticmethod
    def clear_store():
        UserRepository.collection.delete_many({})
        print("user 데이터 삭제 완료")
