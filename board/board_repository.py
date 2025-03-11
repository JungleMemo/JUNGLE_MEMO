import sys
import os 

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import db  # 이제 상위 폴더의 config.py를 불러올 수 있음

class BoardRepository:
    collection = db["boards"]  # 'users' 컬렉션

    @staticmethod
    def find_by_email(url):
        """이메일로 사용자 조회"""
        return BoardRepository.collection.find_one({"url": url})

    @staticmethod
    def create_board(url, title, keyword,summary, like, create):
        """사용자 생성"""
        new_board = {
            "url": url,
            "title": title,
            "keyword": keyword,
            "summary": summary,
            "like":like,
            "create":create
        }
        result = BoardRepository.collection.insert_one(new_board)
        return result.inserted_id


