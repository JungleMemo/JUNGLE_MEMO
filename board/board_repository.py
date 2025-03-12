import sys
import os 
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId  # ✅ MongoDB ObjectId 처리

# 현재 파일의 상위 디렉토리를 Python 모듈 검색 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from settings import db

class BoardRepository:
    """💾 게시글 데이터 관리 (MongoDB)"""

    collection = db["boards"]
    likes_collection = db["likes"]

    @staticmethod
    def find_by_id(post_id):
        """✅ 특정 ID의 게시글 조회"""
        return BoardRepository.collection.find_one({"_id": ObjectId(post_id)})

    @staticmethod
    def find_all():
        """🔥 모든 게시글 조회 (최신순)"""
        return list(BoardRepository.collection.find().sort("create", DESCENDING))

    @staticmethod
    def find_by_writer(writer):
        """
        🔍 특정 사용자가 작성한 게시글 조회 (최신순 정렬)
        :param writer: 사용자 ID 또는 이름
        :return: 최신순 정렬된 게시글 리스트
        """
        return list(BoardRepository.collection.find({"writer": writer}).sort("create", DESCENDING))

    @staticmethod
    def find_by_exact_keyword(keyword):
        """✅ `keyword`가 정확히 일치하는 게시글 조회"""
        return list(BoardRepository.collection.find({"keyword": keyword}))

    @staticmethod
    def create_board(url, writer, title, keyword, summary, like, create):
        """
        📝 게시글 생성 (DB 저장)
        """
        new_board = {
            "url": url,          
            "writer": writer,    
            "title": title,  
            "keyword": keyword, 
            "summary": summary, 
            "like": like,       
            "create": create    
        }
        result = BoardRepository.collection.insert_one(new_board)
        return result.inserted_id
    
    @staticmethod
    def get_total_likes(writer):
        """
        🔹 특정 사용자가 받은 좋아요 총합 계산
        :param writer: 사용자 이름
        :return: 총 좋아요 수 (int)
        """
        pipeline = [
            {"$match": {"writer": writer}},  # ✅ 특정 사용자가 작성한 게시글 필터링
            {"$group": {"_id": None, "total_likes": {"$sum": "$like"}}}  # ✅ 좋아요 총합 계산
        ]
        result = list(BoardRepository.collection.aggregate(pipeline))
        return result[0]["total_likes"] if result else 0  # 🔹 결과가 없으면 0 반환
    
    @staticmethod
    def delete_by_id(post_id):
        """
        ❌ 특정 게시글 삭제 (DELETE 방식)
        :param post_id: 삭제할 게시글의 MongoDB ObjectId
        :return: 삭제 성공 여부 (True/False)
        """
        try:
            result = BoardRepository.collection.delete_one({"_id": ObjectId(post_id)})
            return result.deleted_count > 0  # ✅ 삭제된 문서가 있다면 True 반환
        except Exception as e:
            print(f"❌ 게시글 삭제 실패: {e}")
            return False  # 🔹 삭제 실패 시 False 반환
        

    @staticmethod
    def increase_like(post_id, user_id):
        """👍 좋아요 추가"""
        board = BoardRepository.find_by_id(post_id)
        if not board:
            return False  # 게시글이 존재하지 않음

        if user_id in board.get("liked_users", []):
            return False  # 이미 좋아요를 눌렀음

        BoardRepository.collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$inc": {"like": 1}, "$push": {"liked_users": user_id}}
        )
        return True
    
    @staticmethod
    def has_user_liked(post_id, user_id):
        """✅ 사용자가 이미 좋아요를 눌렀는지 확인"""
        board = BoardRepository.find_by_id(post_id)
        if not board:
            return False
        
        liked_users = board.get("liked_users", [])
        return user_id in liked_users

    
    @staticmethod
    def get_board_by_id(post_id):
        """✅ 특정 ID의 게시글 가져오기"""
        return BoardRepository.collection.find_one({"_id": ObjectId(post_id)})