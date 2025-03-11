import requests
from bs4 import BeautifulSoup
from datetime import datetime
from board_repository import BoardRepository
from urllib.parse import urlparse

class BoardService:
    @staticmethod
    def create_board(url, writer, keyword, like=0):
        """
        🔹 글 작성 서비스 (웹페이지에서 정보 추출하여 DB에 저장)
        :param url: 게시글 URL
        :param writer: 작성자
        :param keyword: 키워드
        :param like: 좋아요 수 (기본값 0)
        :return: 생성된 게시글 ID
        """
        title = BoardService.extract_title(url)
        summary = BoardService.extract_summary(url, keyword)
        create_time = datetime.now()  # ✅ 현재 UTC 시간 기록

        print(f"📌 Creating board with data: {url}, {writer}, {title}, {keyword}, {summary}, {like}, {create_time}")

        return BoardRepository.create_board(url, writer, title, keyword, summary, like, create_time)

    @staticmethod
    def extract_content_text(url):
        """
        🔹 웹페이지의 모든 텍스트 추출 (HTML 제거)
        :param url: 웹페이지 URL
        :return: 정제된 텍스트
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch {url}. Status code: {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return " ".join(text.split()).strip()  # ✅ 공백 정리 후 반환
    
    @staticmethod
    def extract_summary(url, keyword, max_length=200):
        """
        🔹 웹페이지 본문에서 특정 키워드를 포함하는 텍스트를 가져온 후, 
           글자 개수 기준으로 요약하는 함수
        :param url: 웹페이지 URL
        :param keyword: 키워드
        :param max_length: 요약할 최대 글자 수 (기본값: 200)
        :return: 요약된 텍스트
        """
        text = BoardService.extract_content_text(url)
        my_keyword = keyword.strip().lower()

        # 🔹 키워드를 포함하는 글자 찾기 (대소문자 무시)
        keyword_index = text.lower().find(my_keyword)

        if keyword_index == -1:
            print("❌ 해당 키워드가 본문에 없음")
            return text[:max_length]  # 🔹 키워드가 없으면 앞부분 max_length만큼 반환

        # 🔹 키워드를 중심으로 max_length 길이만큼 자르기
        start_index = max(0, keyword_index - max_length // 2)
        end_index = min(len(text), start_index + max_length)

        summary = text[start_index:end_index]

        print(f"\n📌 요약된 본문:\n{summary}...")
        return summary

    @staticmethod
    def extract_title(url):
        """
        🔹 웹페이지의 제목(title) 태그 추출
        :param url: 웹페이지 URL
        :return: 제목 문자열
        """
        response = requests.get(url) 
        soup = BeautifulSoup(response.text, "html.parser") 
        title = soup.title.string.strip() if soup.title else "제목 없음"
        return title
    

if __name__ == "__main__":
    print(BoardService.create_board(
        "https://puleugo.tistory.com/107", "sk", "git"
    ))
