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