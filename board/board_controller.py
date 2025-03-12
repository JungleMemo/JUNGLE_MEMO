import sys
import os

# 현재 파일이 속한 디렉토리의 상위 디렉토리를 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import generate_csrf # ✅ CSRF 토큰 생성 함수 추가
from flask_jwt_extended import jwt_required, get_jwt_identity
from board.board_service import BoardService
from user.user_service import UserService

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

@board_blueprint.route("/create", methods=["GET", "POST"])
@jwt_required(locations=["cookies"])  # ✅ JWT 인증 필요
def create_board():
    """
    📝 게시글 작성 (CSRF 토큰 포함)
    """
    email = get_jwt_identity()  # ✅ 로그인한 사용자의 이메일 가져오기
    user = UserService.get_user_by_email(email)  # ✅ 사용자 조회

    if not user:
        return redirect(url_for("user.login"))  # 🔹 로그인되지 않으면 로그인 페이지로 이동

    writer = user["username"]
    csrf_token = generate_csrf()  # ✅ CSRF 토큰 생성

    if request.method == "POST":
        # ✅ CSRF 토큰 검증
        csrf_token_form = request.form.get("csrf_token")
        if not csrf_token_form:
            flash("❌ CSRF 토큰이 없습니다.", "danger")
            return redirect(url_for("board.create_board"))

        url = request.form["url"]
        keyword = request.form["keyword"]

        # ✅ 키워드 포함 여부 확인
        summary = BoardService.extract_summary(url, keyword)
        keyword_valid = keyword.lower() in summary.lower()

        if "check_keyword" in request.form:
            return render_template("board_create.html", url=url, keyword=keyword, summary=summary, keyword_valid=keyword_valid, csrf_token=csrf_token)

        elif "submit_board" in request.form:
            if not keyword_valid:
                flash("❌ 키워드가 본문에 포함되지 않았습니다. 다른 키워드를 사용해주세요.", "danger")
                return render_template("board_create.html", url=url, keyword=keyword, summary=summary, keyword_valid=keyword_valid, csrf_token=csrf_token)

            post_id = BoardService.create_board(url, writer, keyword)
            flash("✅ 게시글이 성공적으로 등록되었습니다!", "success")
            return redirect(url_for("board.get_boards"))

    return render_template("board_create.html", csrf_token=csrf_token)


@board_blueprint.route("/mypage", methods=["GET"])
@jwt_required(locations=["cookies"])  # ✅ JWT 인증 필요
def mypage():
    email = get_jwt_identity()  # ✅ JWT에서 `email` 가져오기
    user = UserService.get_user_by_email(email)  # ✅ 사용자 조회

    if not user:
        return redirect(url_for("user.login"))  # 🔹 사용자 정보가 없으면 로그인 페이지로 이동

    writer = user["username"]
    likes = BoardService.get_total_likes(writer)  # ✅ 총 좋아요 수 가져오기
    posts = BoardService.get_boards_by_writer(writer)  # ✅ 해당 사용자가 작성한 게시글 조회
    heatmap_data = BoardService.get_heatmap_data(writer, days=30)  # ✅ 히트맵 데이터 생성

    print("🔥 Heatmap Data:", heatmap_data)  # ✅ 디버깅 로그 추가

    return render_template("mypage.html", posts=posts, writer=writer, user=user, heatmap_data=heatmap_data)

@board_blueprint.route("/delete/<post_id>", methods=["DELETE"])
@jwt_required(locations=["cookies"])  # ✅ JWT 인증 필요
def delete_post(post_id):
    """
    ❌ 게시글 삭제 (DELETE 방식)
    """
    email = get_jwt_identity()
    user = UserService.get_user_by_email(email)

    if not user:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    writer = user["username"]
    success = BoardService.delete_post(post_id, writer)

    if success:
        return jsonify({"success": True, "message": "게시글이 삭제되었습니다."}), 200
    else:
        return jsonify({"success": False, "message": "삭제 권한이 없거나 존재하지 않는 게시글입니다."}), 403