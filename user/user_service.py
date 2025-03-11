from user_repository import UserRepository
from werkzeug.security import generate_password_hash, check_password_hash

class UserService:
    @staticmethod
    def register_user(username, email, password):
        if UserRepository.find_by_email(email):
            raise ValueError("Username or email already exists.")

        hashed_password = generate_password_hash(password)
        return UserRepository.create_user(username, email, hashed_password)

    @staticmethod
    def login_user(email, password):
        user = UserRepository.find_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return None  # 로그인 실패
        return user  # 로그인 성공


if __name__ == "__main__":
    #user_id = UserService.register_user("test","test@naver.com", "test123")
    #print(f"✅ 사용자 생성 완료! ID: {user_id}")
    user = UserService.login_user("test@naver.com", "test123")
    print("로그인 성공 %d", user)
