import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import db  # MongoDB 설정 가져오기
from bson import ObjectId

class UserRepository:
    collection = db["users"]  # 'users' 컬렉션

    @staticmethod
    def find_by_email(email):
        """이메일로 사용자 조회"""
        return UserRepository.collection.find_one({"email": email})

    @staticmethod
    def create_user(username, email, hashed_password):
        """사용자 생성"""
        default_profile_photo = "/static/images/default_profile.png"  # 기본 이미지 경로
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "profile_photo": default_profile_photo  # 기본 프로필 사진 저장
        }
        result = UserRepository.collection.insert_one(new_user)
        return result.inserted_id

    @staticmethod
    def update_profile_photo(email, photo_base64):
        """프로필 사진 업데이트"""
        return UserRepository.collection.update_one(
            {"email": email},
            {"$set": {"profile_photo": photo_base64}}
        )
