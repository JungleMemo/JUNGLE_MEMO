import sys
import os 

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from board.board_repository import BoardRepository
from urllib.parse import urlparse
import pytz 
from bson.objectid import ObjectId


class BoardService:

    KST = pytz.timezone("Asia/Seoul")  # ✅ 한국 표준시 (KST)

    @staticmethod
    def get_board_by_id(post_id):
        try:
            post_id = ObjectId(post_id)
        except:
            return None

        return BoardRepository.find_by_id(post_id)

    @staticmethod
    def create_board(url, writer, keyword, like=0):
        """
        🔹 글 작성 서비스 (웹페이지에서 정보 추출하여 DB에 저장)
        :param url: 게시글 URL
        :param writer: 작성자
        :param keyword: 키워드
        :param like: 좋아요 수 (기본값 0)
        :return: 생성된 게시글 ID
        """
        title = BoardService.extract_title(url)
        summary = BoardService.extract_summary(url, keyword)
        create_time = datetime.now()  # ✅ 현재 UTC 시간 기록

        print(f"📌 Creating board with data: {url}, {writer}, {title}, {keyword}, {summary}, {like}, {create_time}")

        return BoardRepository.create_board(url, writer, title, keyword, summary, like, create_time)
    
    @staticmethod
    def get_board_list(keyword="", sort_by="like"):
        """
        🔹 정확한 키워드 검색 + 정렬 기능 포함
        :param keyword: 검색 키워드 (없으면 전체 조회)
        :param sort_by: 정렬 방식 ("like" | "latest")
        :return: 정렬된 게시글 리스트
        """
        if keyword:
            boards = BoardRepository.find_by_exact_keyword(keyword)  # 🔍 정확한 키워드 검색
        else:
            boards = BoardRepository.find_all()  # 🔥 전체 게시글 조회

        # 정렬 기준 설정
        sort_field = "like" if sort_by == "like" else "create"
        sort_order = -1  # 내림차순 정렬

        return sorted(boards, key=lambda x: x.get(sort_field, 0), reverse=True)

    @staticmethod
    def extract_content_text(url):
        """
        🔹 웹페이지의 모든 텍스트 추출 (HTML 제거)
        :param url: 웹페이지 URL
        :return: 정제된 텍스트
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url}. Status code: {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split()).strip()  # ✅ 공백 정리 후 반환
    
    @staticmethod
    def extract_summary(url, keyword, max_length=200):
        """
        🔹 웹페이지 본문에서 특정 키워드를 포함하는 텍스트를 가져온 후, 
           글자 개수 기준으로 요약하는 함수
        :param url: 웹페이지 URL
        :param keyword: 키워드
        :param max_length: 요약할 최대 글자 수 (기본값: 200)
        :return: 요약된 텍스트
        """
        text = BoardService.extract_content_text(url)
        my_keyword = keyword.strip().lower()

        # 🔹 키워드를 포함하는 글자 찾기 (대소문자 무시)
        keyword_index = text.lower().find(my_keyword)

        if keyword_index == -1:
            print("❌ 해당 키워드가 본문에 없음")
            return text[:max_length]  # 🔹 키워드가 없으면 앞부분 max_length만큼 반환

        # 🔹 키워드를 중심으로 max_length 길이만큼 자르기
        start_index = max(0, keyword_index - max_length // 2)
        end_index = min(len(text), start_index + max_length)

        summary = text[start_index:end_index]

        print(f"\n📌 요약된 본문:\n{summary}...")
        return summary

    @staticmethod
    def extract_title(url):
        """ 🔹 웹페이지 제목(title) 태그 추출 """
        response = requests.get(url) 
        soup = BeautifulSoup(response.text, "html.parser") 
        return soup.title.string.strip() if soup.title else "제목 없음"
    
    @staticmethod
    def get_boards_by_writer(writer):
        """
        🔍 특정 사용자의 게시글 목록 조회
        :param writer: 작성자 ID 또는 이름
        :return: 최신순 게시글 리스트
        """
        return BoardRepository.find_by_writer(writer)
    
    @staticmethod
    def delete_post(post_id, writer):
        """
        🗑 게시글 삭제 (DELETE 요청 처리)
        :param post_id: 삭제할 게시글의 ID
        :param writer: 요청한 사용자의 이름
        :return: 삭제 성공 여부 (True/False)
        """
        post = BoardRepository.collection.find_one({"_id": ObjectId(post_id)})

        if not post:
            return False  # 🔹 게시글이 존재하지 않음
        
        if post["writer"] != writer:
            return False  # 🔹 작성자 본인이 아님 (삭제 권한 없음)

        return BoardRepository.delete_by_id(post_id)  # ✅ 삭제 실행
    
    @staticmethod
    def get_total_likes(writer):
        """
        🔹 특정 사용자의 총 좋아요 수 반환
        :param writer: 사용자 이름
        :return: 총 좋아요 수 (int)
        """
        return BoardRepository.get_total_likes(writer)
    

    @staticmethod
    def get_kst_today():
        """ 🔄 현재 한국(KST) 날짜 반환 """
        return datetime.now(BoardService.KST).date()

    #TODO: 크래프톤 정글 시작날짜와 끝@staticmethod
    def create_board(url, writer, keyword, like=0):
        """
        📝 게시글 생성 (웹페이지 정보 추출 후 DB 저장)
        :param url: 게시글 URL
        :param writer: 작성자
        :param keyword: 키워드
        :param like: 좋아요 수 (기본값 0)
        :return: 생성된 게시글 ID
        """
        title = BoardService.extract_title(url)
        summary = BoardService.extract_summary(url, keyword)
        create_time = datetime.now()  # ✅ 현재 UTC 시간 기록

        return BoardRepository.create_board(url, writer, title, keyword, summary, like, create_time)
    
    @staticmethod
    def generate_heatmap(start_date, days):
        """
        🔥 기본 히트맵 데이터 생성 (빈 날짜 포함)
        :param start_date: 시작 날짜 (오늘)
        :param days: 며칠 치 데이터를 생성할 것인지
        :return: 빈 히트맵 데이터 (날짜별 0)
        """
        end_date = start_date + timedelta(days=days)
        return {
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d"): 0
            for i in range((end_date - start_date).days + 1)
        }

    @staticmethod
    def update_heatmap_data(heatmap_data, db_data):
        """
        🔄 데이터베이스에서 가져온 날짜를 반영하여 히트맵 업데이트
        :param heatmap_data: 기본 히트맵 데이터 (딕셔너리)
        :param db_data: 데이터베이스에서 가져온 날짜 리스트
        :return: 업데이트된 히트맵 데이터
        """
        for date in db_data:
            if date in heatmap_data:
                heatmap_data[date] = 1  # ✅ 해당 날짜에 글이 있음을 표시
        return heatmap_data

    @staticmethod
    def get_heatmap_data(writer, days=30):
        """
        🔥 특정 사용자의 게시글 작성 데이터를 반영한 히트맵 생성
        :param writer: 작성자 ID 또는 이름
        :param days: 최근 며칠 치 데이터를 표시할 것인지
        :return: 날짜별 글 작성 여부 (딕셔너리 형태)
        """
        posts = BoardRepository.find_by_writer(writer)  # ✅ 사용자의 게시글 가져오기
        db_data = []

        for post in posts:
            if isinstance(post["create"], datetime):
                # ✅ UTC → KST 변환 후 날짜 포맷 변경
                date_kst = post["create"].replace(tzinfo=pytz.utc).astimezone(BoardService.KST).strftime("%Y-%m-%d")
            else:
                date_kst = post["create"]  # ✅ 문자열로 저장된 경우 그대로 사용
            db_data.append(date_kst)

        # ✅ 한국(KST) 기준 오늘 날짜로 시작
        start_date = BoardService.get_kst_today() - timedelta(days=days)
        heatmap_data = BoardService.generate_heatmap(start_date, days)
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
