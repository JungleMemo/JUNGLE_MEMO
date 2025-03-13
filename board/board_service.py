import sys
import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from board.board_repository import BoardRepository
import pytz
from bson.objectid import ObjectId

# ✅ Python 모듈 검색 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class BoardService:
    """ 게시글 서비스 로직 """

    KST = pytz.timezone("Asia/Seoul")  # ✅ 한국 표준시 (KST)

    @staticmethod
    def get_board_by_id(post_id):
        """ ✅ 게시글 ID로 게시글 가져오기 """
        try:
            post_id = ObjectId(post_id)
        except:
            return None

        return BoardRepository.find_by_id(post_id)

    @staticmethod
    def create_board(url, writer_email, keyword, like=0):
        """
        📝 게시글 생성 (티스토리 본문 크롤링)
        """
        title = BoardService.extract_title(url)
        summary = BoardService.extract_summary(url, keyword)
        create_time = datetime.now(BoardService.KST)  # ✅ 한국 시간(KST)으로 저장

        print(f"📌 Creating board: {title}, {writer_email}, {summary}, {like}, {create_time}")

        return BoardRepository.create_board(url, writer_email, title, keyword, summary, like, create_time)

    @staticmethod
    def extract_content_text(url):
        """
        🔹 티스토리 블로그 본문(article 태그)만 추출
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code != 200:
            print(f"❌ Failed to fetch {url}. Status code: {response.status_code}")
            return ""

        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ <article> 태그 찾기 (티스토리 본문)
        article = soup.find("article")
        if article:
            text = article.get_text(separator=" ", strip=True)
        else:
            # 🔹 <article> 태그가 없으면, 일반적인 본문 div 찾기
            content_div = soup.find("div", class_=re.compile("article|content|entry|post"))
            text = content_div.get_text(separator=" ", strip=True) if content_div else ""

        return " ".join(text.split()).strip()  # ✅ 공백 정리 후 반환

    @staticmethod
    def extract_summary(url, keyword, max_length=200):
        """
        🔹 본문에서 키워드 중심으로 요약
        """
        text = BoardService.extract_content_text(url)

        # ✅ 문장 단위로 분할
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # ✅ 키워드 포함된 문장 선택
        keyword_sentences = [s for s in sentences if keyword.lower() in s.lower()]

        # ✅ 키워드 포함된 첫 2~3 문장 요약
        if keyword_sentences:
            summary = " ".join(keyword_sentences[:3])
        else:
            summary = " ".join(sentences[:3])  # 키워드 없으면 첫 3문장 요약

        return summary[:max_length]  # ✅ 최대 글자 제한

    @staticmethod
    def extract_title(url):
        """ ✅ 웹페이지 제목(title) 태그 추출 """
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.title.string.strip() if soup.title else "제목 없음"

    @staticmethod
    def get_board_list(keyword="", sort_by="like"):
        """
        🔹 정확한 키워드 검색 + 정렬 기능
        """
        if keyword:
            boards = BoardRepository.find_by_exact_keyword(keyword)
        else:
            boards = BoardRepository.find_all()

        # 정렬 기준 설정
        sort_field = "like" if sort_by == "like" else "create"
        return sorted(boards, key=lambda x: x.get(sort_field, 0), reverse=True)

    @staticmethod
    def delete_post(post_id, email):
        """
        🗑 게시글 삭제
        """
        post = BoardRepository.collection.find_one({"_id": ObjectId(post_id)})

        if not post:
            return False  # 🔹 게시글이 존재하지 않음

        if post["writer_email"] != email:
            return False  # 🔹 작성자 본인이 아님 (삭제 권한 없음)

        return BoardRepository.delete_by_id(post_id)  # ✅ 삭제 실행

    @staticmethod
    def get_total_likes(email):
        """
        🔹 특정 사용자의 총 좋아요 수 반환
        """
        return BoardRepository.get_total_likes(email)

    @staticmethod
    def get_kst_today():
        """ 🔄 현재 한국(KST) 날짜 반환 """
        return datetime.now(BoardService.KST).date()

    @staticmethod
    def generate_heatmap(start_date, end_date):
        """
        🔥 기본 히트맵 데이터 생성 (빈 날짜 포함)
        """
        return {
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d"): 0
            for i in range((end_date - start_date).days + 1)
        }

    @staticmethod
    def update_heatmap_data(heatmap_data, db_data):
        """
        🔄 데이터베이스에서 가져온 날짜를 반영하여 히트맵 업데이트
        """
        for date in db_data:
            if date in heatmap_data:
                heatmap_data[date] = 1  # ✅ 해당 날짜에 글이 있음을 표시
        return heatmap_data

    @staticmethod
    def get_heatmap_data(email):
        """
        🔥 특정 사용자의 게시글 작성 데이터를 반영한 히트맵 생성
        """
        posts = BoardRepository.find_by_writer(email)
        db_data = []

        for post in posts:
            if isinstance(post["create"], datetime):
                date_kst = post["create"].replace(tzinfo=pytz.utc).astimezone(BoardService.KST).strftime("%Y-%m-%d")
            else:
                date_kst = post["create"]
            db_data.append(date_kst)

        # ✅ 히트맵 기간 (2025년 3월 10일 ~ 2025년 7월 31일)
        start_date = date(2025, 3, 10)
        end_date = date(2025, 7, 31)

        heatmap_data = BoardService.generate_heatmap(start_date, end_date)
        return BoardService.update_heatmap_data(heatmap_data, db_data)

    @staticmethod
    def increase_like(post_id, user_email):
        """
        ✅ 사용자가 특정 게시글에 좋아요를 누르면 증가
        """
        return BoardRepository.increase_like(post_id, user_email)

    @staticmethod
    def has_user_liked(post_id, user_email):
        """
        ✅ 사용자가 좋아요 했는지 확인
        """
        return BoardRepository.has_user_liked(post_id, user_email)

    @staticmethod
    def get_board_by_id(post_id):
        """✅ 특정 게시글 가져오기"""
        return BoardRepository.get_board_by_id(post_id)

    @staticmethod
    def like_post(post_id, user_id):
        """👍 사용자가 게시글에 좋아요를 누름"""
        if BoardRepository.has_user_liked(post_id, user_id):
            return False, "이미 좋아요를 눌렀습니다."

        success = BoardRepository.increase_like(post_id, user_id)
        return success, "좋아요가 반영되었습니다." if success else "게시글이 존재하지 않습니다."


if __name__ == "__main__":
    print(BoardService.create_board(
        "https://puleugo.tistory.com/107", "123", "git"
    ))
