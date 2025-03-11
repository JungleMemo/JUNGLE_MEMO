import sys
import os 
from datetime import datetime

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import db  # 이제 상위 폴더의 config.py를 불러올 수 있음

class BoardRepository:
    collection = db["boards"]  # 'users' 컬렉션

    @staticmethod
    def find_by_writer(writer):
        """글쓴이로 보드 조회"""
        return BoardRepository.collection.find_one({"writer": writer})

    @staticmethod
    def create_board(url, writer, title, keyword, summary, like, create):
        """보드 생성"""
        new_user = {
            "url": url,          
            "write": writer,    
            "title": title,  
            "keyword": keyword, 
            "summary": summary, 
            "like": like,       
            "create": create    
        }
        result = BoardRepository.collection.insert_one(new_user)
        print("✅ Board Inserted:", result.inserted_id)  # ✅ MongoDB에 삽입 여부 확인
        return result.inserted_id


if __name__ == "__main__":
    BoardRepository.create_board("123.com", "sk", "title", "key", "summ", 0, datetime.now())