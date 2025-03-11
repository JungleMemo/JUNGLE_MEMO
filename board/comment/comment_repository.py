import sys
import os 

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import db

class CommentRepository:
    collection = db["comment"]

    @staticmethod
    def find_by_board_id(board_id):
        """✅ 특정 작성자의 게시글 조회"""
        return CommentRepository.collection.find({"board_id": board_id})

    @staticmethod
    def create_comment(writer, content, create, board_id):
        """✅ 게시글 생성"""
        new_board = {
            "writer": writer,
            "content": content,    
            "create": create,
            "board_id": board_id    
        }
        result = CommentRepository.collection.insert_one(new_board)
        print("✅ Board Inserted:", result.inserted_id)
        return result.inserted_id