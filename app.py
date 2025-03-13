import sys
import os

# 현재 파일의 상위 디렉터리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_wtf.csrf import CSRFProtect
from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager
from user.user_controller import user_bp
from board.board_controller import board_blueprint
from settings import Config
from datetime import timedelta


app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY  # 세션 키
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY  # JWT 시크릿 키
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # CSRF 보호 비활성화
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token_cookie"  # ✅ 기본값 유지
app.config["JWT_ACCESS_CSRF_HEADER_NAME"] = "X-CSRF-TOKEN"
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_SECURE"] = False  # 개발환경에서는 False로 설정
app.config["JWT_SESSION_COOKIE"] = True
app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # 꼭 cookies가 포함되어 있어야 합니다!

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=365 * 100)  # 100년 후 만료 (최대한 길게)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=365 * 100)  # 100년 후 만료 (최대한 길게)

# 기본 루트 /login으로 리다이렉트
@app.route("/")
def index():
    return redirect(url_for("user.login"))


jwt = JWTManager(app)

# Blueprint 등록
app.register_blueprint(user_bp)
app.register_blueprint(board_blueprint)

if __name__ == "__main__":
    app.run(port=5001, debug=True)