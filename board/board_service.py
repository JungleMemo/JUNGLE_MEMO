from board_repository import UserRepository  # 레포지토리 import
from datetime import datetime

#yj
import requests
from bs4 import BeautifulSoup
import nltk
from urllib.parse import urlparse

nltk.download("punkt")

class UserService:
    @staticmethod
    def create_board(url, writer, keyword, like=0):
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
        title = UserService.extract_title(url)
        summary = UserService.extract_summary(url, keyword)
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


#yj
    @staticmethod
    def extract_content_text(url):
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            print (f"Failed to fetch {url}. Status code: {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(seperator=" ", strip=True)
        text = " ".join(text.split())
        return text.strip()
    
    @staticmethod
    def extract_summary(url, keyword):
        # 🔑 키워드 입력 후 문장 추출
        text = UserService.extract_content_text(url)
        my_keyword = keyword.strip().lower()
        sentences = nltk.sent_tokenize(text)
        # filtered_sentences = [s for s in sentences if keyword in s.lower()][:3]
        filtered_sentences = [s.strip() for s in sentences if my_keyword in s.lower()]
        filtered_sentences = [s for s in filtered_sentences if s]  # ✅ 공백만 있는 문장 제거

        print(f"\n웹페이지 본문 (요약된 내용):")
        if filtered_sentences:
            for i, sentence in enumerate(filtered_sentences[:3], 1):
                print(f"{i}. {sentence}")
        else:
            print("해당 키워드가 포함된 문장을 찾을 수 없습니다.")

    @staticmethod
    def extract_title(url):
        response = requests.get(url) 
        soup = BeautifulSoup(response.text, "html.parser") 
        title = soup.title.string.strip() if soup.title else "제목 없음"
        return title



    