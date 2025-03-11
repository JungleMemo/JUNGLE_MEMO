from board_repository import UserRepository  # 레포지토리 import
from datetime import datetime

class UserService:
    @staticmethod
    def create_board(url, writer, title, keyword, summary, like=0):
        """
        글 작성 서비스
        :param url: 게시글 URL
        :param writer: 작성자
        :param title: 제목
        :param keyword: 키워드
        :param summary: 요약
        :param like: 좋아요 수 (기본값 0)
        :return: 생성된 게시글 ID
        """
        create_time = datetime  # 현재 UTC 시간 기록
        return UserRepository.create_board(url, writer, title, keyword, summary, like, create_time)

    @staticmethod
    def find_by_writer(writer):
        """
        작성자의 글 검색
        :param writer: 검색할 작성자
        :return: 해당 작성자의 게시글 (없으면 None)
        """
        return UserRepository.find_by_writer(writer)
