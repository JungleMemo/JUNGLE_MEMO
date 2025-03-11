from board.board_repository import BoardRepository

class BoardService:
    def __init__(self):
        self.board_repository = BoardRepository()

    def get_board_list(self):
        """
        게시글 전체 목록 조회 (페이징 및 검색 없음)
        :return: 모든 게시글 목록
        """
        board_list = list(self.board_repository.collection.find())

        # 🛠 디버깅: 데이터 확인
        print("📌 MongoDB에서 가져온 데이터:", board_list)
        
        # MongoDB의 _id 값을 문자열로 변환 (JSON 직렬화 가능하도록)
        for board in board_list:
            board["_id"] = str(board["_id"])

        return board_list
