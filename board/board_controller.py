import sys
import os

# 현재 파일이 속한 디렉토리의 상위 디렉토리를 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import generate_csrf # ✅ CSRF 토큰 생성 함수 추가
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from board.board_service import BoardService
from user.user_service import UserService
from comment.comment_service import CommentService

# 블루프린트 생성
board_blueprint = Blueprint("board", __name__)
# 서비스 객체 생성
board_service = BoardService()

@board_blueprint.before_request
def ensure_jwt_exist():
    exempt_routes = [
        "user.login", "user.register", "static",
        "board.get_boards", "board.view_board", "board.search_boards"
    ]

    if request.endpoint in exempt_routes:
        return  # 🔹 예외 처리 대상은 인증 체크 안 함

    if "access_token_cookie" not in request.cookies:  # ✅ 쿠키 확인
        print("⚠️ JWT 쿠키 없음 -> 로그인 페이지로 이동")
        return redirect(url_for("user.login"))

    try:
        verify_jwt_in_request()  # ✅ JWT 검증 시도
    except Exception as e:
        print(f"⚠️ JWT 검증 실패: {str(e)} -> 그냥 사십쇼")

@board_blueprint.route("/boards", methods=["GET"])
def get_boards():
    """ 게시글 전체 목록 조회 API (페이징 없이) """
    boards = board_service.get_board_list()
    return redirect(url_for("board.search_boards"))

@board_blueprint.route("/board/<post_id>", methods=["GET"])
@jwt_required(optional=True)  # ✅ 로그인하지 않아도 접근 가능
def view_board(post_id):
    """
    🔹 특정 게시글 상세 조회
    """
    board = BoardService.get_board_by_id(post_id)
    
    if not board:
        flash("게시글을 찾을 수 없습니다.", "danger")
        return redirect(url_for("board.get_boards"))

    comments = CommentService.get_comments_by_board(post_id)

    current_user_email = get_jwt_identity()  # ✅ 로그인한 유저만 가져오기 (비로그인 사용자는 None)
    return render_template("contentview.html", board=board, comments=comments, current_user_email=current_user_email)

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

        #제목 가져오기
        title = BoardService.extract_title(url)

        # ✅ 키워드 포함 여부 확인
        summary = BoardService.extract_summary(url, keyword)
        keyword_valid = keyword.lower() in summary.lower()

        if "check_keyword" in request.form:
            return render_template("board_create.html", url=url, title = title,keyword=keyword, summary=summary, keyword_valid=keyword_valid, csrf_token=csrf_token)

        elif "submit_board" in request.form:
            if not keyword_valid:
                flash("❌ 키워드가 본문에 포함되지 않았습니다. 다른 키워드를 사용해주세요.", "danger")
                return render_template("board_create.html", url=url,title = title, keyword=keyword, summary=summary, keyword_valid=keyword_valid, csrf_token=csrf_token)

            post_id = BoardService.create_board(url, writer, keyword)
            flash("✅ 게시글이 성공적으로 등록되었습니다!", "success")
            return redirect(url_for("board.get_boards"))

    return render_template("board_create.html", csrf_token=csrf_token)


@board_blueprint.route("/mypage", methods=["GET"])
@jwt_required(locations=["cookies"])
def mypage():
    email = get_jwt_identity()
    user = UserService.get_user_by_email(email)

    if not user:
        return redirect(url_for("user.login"))

    writer = user["username"]
    total_likes = BoardService.get_total_likes(writer)
    posts = BoardService.get_boards_by_writer(writer)
    
    # ✅ 히트맵 데이터 추가
    heatmap_data = BoardService.get_heatmap_data(writer)

    return render_template(
        "mypage.html", 
        posts=posts, 
        writer=writer, 
        user=user, 
        heatmap_data=heatmap_data, 
        total_likes=total_likes
    )


@board_blueprint.route("/delete/<post_id>", methods=["POST"])
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

    return redirect(url_for("board.mypage"))  # ✅ 삭제 후 게시글 목록으로 리디렉트

    
@board_blueprint.route("/add_comment/<board_id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def add_comment(board_id):
    email = get_jwt_identity()  # "qwer@qwer.com"
    user = UserService.get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    data = request.get_json()
    content = data.get("content")
    if not content:
            return jsonify({"success": False, "message": "댓글 내용을 입력하세요."}), 400

        # 닉네임 + 이메일 둘 다 준비
    writer_name = user["username"]     
    writer_email = user["email"]       

    # 댓글 db에 저장
    CommentService.add_comment(writer_name, writer_email, content, board_id)

    return jsonify({"success": True, "message": "댓글이 등록되었습니다."}), 201

@board_blueprint.route("/delete_comment/<comment_id>", methods=["DELETE"])
@jwt_required(locations=["cookies"])
def delete_comment(comment_id):
    email = get_jwt_identity()  # "qwer@qwer.com"
    user = UserService.get_user_by_email(email)
    if not user:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    comment = CommentService.get_comment_by_id(comment_id)
    if not comment:
        return jsonify({"success": False, "message": "삭제할 댓글이 없습니다."}), 404

    # writer_email로 본인 여부 확인
    if comment["writer_email"] != user["email"]:
        return jsonify({"success": False, "message": "자신의 댓글만 삭제할 수 있습니다."}), 403

    CommentService.delete_comment(comment_id)
    return jsonify({"success": True, "message": "댓글이 삭제되었습니다."}), 200

@board_blueprint.route("/search", methods=["GET"])
def search_boards():
    """
    🔹 정확한 키워드 검색, 좋아요순 정렬, 최신순 정렬 기능
    """
    keyword = request.args.get("keyword", "").strip()
    sort_by = request.args.get("sort", "like")  # 기본 정렬: 좋아요순

    # 🔍 정확한 키워드 일치 검색 적용
    boards = BoardService.get_board_list(keyword, sort_by)

    return render_template("search.html", boards=boards)

@board_blueprint.route("/like/<post_id>", methods=["POST"])
@jwt_required(locations=["cookies"])
def like_post(post_id):
    """👍 좋아요 기능 (POST 요청)"""
    email = get_jwt_identity()
    user = UserService.get_user_by_email(email)

    if not user:
        return jsonify({"success": False, "message": "로그인이 필요합니다."}), 401

    user_id = user["email"]  # 사용자 식별자로 이메일 사용

    success, message = BoardService.like_post(post_id, user_id)

    return jsonify({"success": success, "message": message})