from flask import Flask
from board.board_controller import board_blueprint

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(board_blueprint)

if __name__ == "__main__":
    app.run("0.0.0.0",port=5001, debug=True)
