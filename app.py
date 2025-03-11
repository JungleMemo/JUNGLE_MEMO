from flask import Flask
from flask_jwt_extended import JWTManager
from user.user_controller import user_bp
from settings import Config

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY  # 세션 키
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY  # JWT 시크릿 키

jwt = JWTManager(app)

# Blueprint 등록
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)
