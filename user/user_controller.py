from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies, set_access_cookies
from user.user_service import UserService
from user.user_repository import UserRepository

import base64

user_bp = Blueprint("user", __name__)

@user_bp.route("/update_profile_photo", methods=["POST"])
@jwt_required(locations=["cookies"])
def update_profile_photo():
    """ 프로필 사진 변경 """
    email = get_jwt_identity()
    user = UserService.get_user_by_email(email)

    if not user:
        return jsonify({"success": False, "message": "사용자를 찾을 수 없습니다."}), 404

    file = request.files.get("profile_photo")
    if not file:
        return jsonify({"success": False, "message": "파일을 업로드하세요."}), 400

    # Base64로 변환 후 DB에 저장
    photo_base64 = base64.b64encode(file.read()).decode("utf-8")
    UserService.update_profile_photo(email, photo_base64)

    return jsonify({"success": True, "message": "프로필 사진이 업데이트되었습니다."}), 200

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    """회원가입 라우트"""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        try:
            UserService.register_user(username, email, password)
            flash("회원가입 성공! 로그인 해주세요.", "success")
            return redirect(url_for("user.login"))
        except ValueError as e:
            flash(str(e), "danger")

    return render_template("register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    """로그인 라우트"""
    token = request.cookies.get("access_token_cookie")  # ✅ JWT 쿠키가 있는지 확인
    if token:
        return redirect(url_for("board.mypage"))

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        token = UserService.login_user(email, password)

        if token:
            response = make_response(redirect(url_for("board.mypage")))
            set_access_cookies(response, token)  # ✅ JWT를 쿠키에 저장
            return response
        else:
            flash("잘못된 로그인 정보입니다.", "danger")

    return render_template("login.html")


@user_bp.route("/mainpage")
@jwt_required(locations=["cookies"])  # ✅ JWT를 쿠키에서 가져오기
def mainpage():
    """JWT가 있는 경우만 메인 페이지 렌더링"""
    email = get_jwt_identity()  # ✅ JWT에서 `email`을 가져오기
    user = UserRepository.find_by_email(email)  # ✅ 이메일을 통해 사용자 조회

    if not user:
        return redirect(url_for("user.login"))

    return render_template("mainpage.html", username=user["username"])


@user_bp.route("/logout")
def logout():
    """로그아웃 (JWT 쿠키 삭제)"""
    response = make_response(redirect(url_for("user.login")))
    unset_jwt_cookies(response)  #  JWT 토큰 삭제
    return response