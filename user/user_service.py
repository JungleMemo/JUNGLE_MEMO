from user.user_repository import UserRepository
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token

class UserService:
    @staticmethod
    def register_user(username, email, password):
        """회원가입: 중복 체크 후 저장"""
        if UserRepository.find_by_email(email):
            raise ValueError("이미 존재하는 이메일입니다.")

        hashed_password = generate_password_hash(password)
        UserRepository.create_user(username, email, hashed_password)
        return {"message": "회원가입 성공!"}

    @staticmethod
    def login_user(email, password):
        """로그인: 비밀번호 검증 후 JWT 발급"""
        user = UserRepository.find_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return None

        # JWT 토큰 생성 시 identity 값을 문자열로 변환
        access_token = create_access_token(identity=user["email"])  
        return access_token
    
    @staticmethod
    def get_user_by_email(email):
        """
        🔍 이메일을 통해 사용자 정보 조회
        :param email: 사용자 이메일
        :return: 사용자 정보 (없으면 None)
        """
        return UserRepository.find_by_email(email)
