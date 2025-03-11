import sys
import os

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import db  # 이제 상위 폴더의 config.py를 불러올 수 있음


class UserRepository:
    collection = db["users"]  # 'users' 컬렉션

    @staticmethod
    def find_by_email(email):
        """이메일로 사용자 조회"""
        return UserRepository.collection.find_one({"email": email})

    @staticmethod
    def create_user(username, email, hashed_password):
        """사용자 생성"""
        new_user = {
            "username": username,
            "email": email,
            "password": hashed_password
        }
        result = UserRepository.collection.insert_one(new_user)
        return result.inserted_id



