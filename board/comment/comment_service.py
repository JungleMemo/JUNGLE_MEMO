from datetime import datetime
from comment_repository import CommentRepository

class CommentService:
    """🔧 댓글 서비스 (비즈니스 로직)"""

    @staticmethod
    def get_comments_by_board(board_id):
        """
        🔍 특정 게시글(board_id)에 대한 최신 댓글 리스트 반환
        :param board_id: 게시글 ID
        :return: 최신순 정렬된 댓글 리스트
        """
        return CommentRepository.find_by_board_id(board_id)

    @staticmethod
    def add_comment(writer, content, board_id):
        """
        ✏️ 새로운 댓글 추가
        :param writer: 작성자 이름
        :param content: 댓글 내용
        :param board_id: 게시글 ID
        :return: 생성된 댓글 ID
        """
        create_time = datetime.now()  # UTC 기준 현재 시간 기록
        return CommentRepository.create_comment(writer, content, create_time, board_id)
