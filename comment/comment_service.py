import sys
import os
from datetime import datetime
from bson.objectid import ObjectId  # ✅ ObjectId 임포트 추가
from comment.comment_repository import CommentRepository

class CommentService:
    """🔧 댓글 서비스 (비즈니스 로직)"""

    @staticmethod
    def get_comments_by_board(board_id):
        """🔍 특정 게시글(board_id)에 대한 최신 댓글 리스트 반환"""
        return CommentRepository.find_by_board_id(board_id)

    @staticmethod
    def add_comment(writer_name, writer_email, content, board_id):
        """✏️ 새로운 댓글 추가"""
        create_time = datetime.now()  # ✅ UTC 시간 기준 저장
        print(f"📌 댓글 저장: 작성자={writer_name}, 내용={content}, 게시글ID={board_id}")  # ✅ 디버깅용 로그 추가

        # ✅ ObjectId 변환 (보드 ID가 문자열로 전달될 가능성 대비)
        if not isinstance(board_id, ObjectId):
            try:
                board_id = ObjectId(board_id)
            except:
                print("❌ 유효하지 않은 ObjectId 변환 실패")
                return False

        # 댓글 저장
        CommentRepository.create_comment(writer_name, writer_email, content, create_time, board_id)

        return True

    @staticmethod
    def delete_comment(comment_id):
        """
        ❌ 댓글 삭제
        :param comment_id: 삭제할 댓글 ID
        :return: 삭제 성공 여부 (True/False)
        """
        return CommentRepository.delete_comment(comment_id)

    @staticmethod
    def get_comment_by_id(comment_id):
        return CommentRepository.find_by_id(comment_id)

