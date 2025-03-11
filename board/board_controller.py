from flask import Blueprint, render_template
from board.board_service import BoardService

# 블루프린트 생성
board_blueprint = Blueprint("board", __name__)
# 서비스 객체 생성
board_service = BoardService()

@board_blueprint.route("/boards", methods=["GET"])
def get_boards():
    """
    게시글 전체 목록 조회 API (페이징 없이)
    """
    boards = board_service.get_board_list()
    #  # 🛠 디버깅 출력 (터미널에서 확인 가능)
    # print("📌 가져온 게시글 목록:", boards)  
    return render_template("board_list.html", boards=boards)
