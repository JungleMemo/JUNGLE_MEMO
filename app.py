import sys
import os

# 현재 파일의 상위 디렉터리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask_wtf.csrf import CSRFProtect
from flask import Flask
from flask_jwt_extended import JWTManager
from user.user_controller import user_bp
from board.board_controller import board_blueprint
from settings import Config


app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY  # 세션 키
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY  # JWT 시크릿 키
app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # ✅ JWT 기반 CSRF 보호 비활성화


jwt = JWTManager(app)

# Blueprint 등록
app.register_blueprint(user_bp)
app.register_blueprint(board_blueprint)

if __name__ == "__main__":
    app.run(debug=True)
