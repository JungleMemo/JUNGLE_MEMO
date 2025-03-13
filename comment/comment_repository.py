import sys
import os
from settings import db
from pymongo import DESCENDING
from bson.objectid import ObjectId  # MongoDB ObjectId 변환

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CommentRepository:
    """💾 댓글 데이터 관리 (MongoDB)"""
    
    collection = db["comments"]  # ✅ 컬렉션 이름 수정

    @staticmethod
    def find_by_board_id(board_id):
        """🔍 특정 게시글(board_id)에 해당하는 모든 댓글 조회 (최신순 정렬)"""
        return list(CommentRepository.collection.find({"board_id": ObjectId(board_id)}).sort("create", DESCENDING))

    @staticmethod
    def find_by_id(comment_id):
        return CommentRepository.collection.find_one({"_id": ObjectId(comment_id)})

    @staticmethod
    def create_comment(writer_name, writer_email, content, create, board_id):
        """✏️ 새로운 댓글 작성"""
        new_comment = {
            "writer_name": writer_name,
            "writer_email":writer_email,
            "content": content,
            "create": create,
            "board_id": ObjectId(board_id)  # ✅ ObjectId 변환 추가
        }
        result = CommentRepository.collection.insert_one(new_comment)
        print(f"✅ Comment Inserted: {result.inserted_id}")  # ✅ 저장된 ID 확인
        return result.inserted_id

    @staticmethod
    def delete_comment(comment_id):
        """
        ❌ 댓글 삭제
        :param comment_id: 삭제할 댓글 ID
        :return: 삭제 성공 여부 (True/False)
        """
        try:
            result = CommentRepository.collection.delete_one({"_id": ObjectId(comment_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ 댓글 삭제 실패: {e}")
            return False


