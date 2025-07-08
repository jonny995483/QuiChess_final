# --- START OF FILE constants.py (최종 완성본) ---

import pygame
pygame.init()

WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('QuiChess: The Ultimate Quiz Chess!')

try:
    font = pygame.font.SysFont('malgungothic', 20)
    medium_font = pygame.font.SysFont('malgungothic', 40)
    big_font = pygame.font.SysFont('malgungothic', 50)
    print("'맑은 고딕' 폰트를 성공적으로 불러왔습니다.")
except pygame.error:
    print("경고: '맑은 고딕' 폰트를 찾을 수 없습니다. 기본 폰트로 대체합니다. 한글이 깨질 수 있습니다.")
    font = pygame.font.Font(None, 24)
    medium_font = pygame.font.Font(None, 48)
    big_font = pygame.font.Font(None, 60)

timer = pygame.time.Clock()
fps = 60
# game variables and images
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
captured_pieces_white, captured_pieces_black = [], []
turn_step, selection = 0, 100
valid_moves = []

# 이미지 로딩 (기존과 동일)
black_queen = pygame.image.load('assets/1024px/b_queen_png_shadow_1024px.png'); black_queen = pygame.transform.scale(black_queen, (80, 80)); black_queen_small = pygame.transform.scale(black_queen, (45, 45))
black_king = pygame.image.load('assets/1024px/b_king_png_shadow_1024px.png'); black_king = pygame.transform.scale(black_king, (80, 80)); black_king_small = pygame.transform.scale(black_king, (45, 45))
black_rook = pygame.image.load('assets/1024px/b_rook_png_shadow_1024px.png'); black_rook = pygame.transform.scale(black_rook, (80, 80)); black_rook_small = pygame.transform.scale(black_rook, (45, 45))
black_bishop = pygame.image.load('assets/1024px/b_bishop_png_shadow_1024px.png'); black_bishop = pygame.transform.scale(black_bishop, (80, 80)); black_bishop_small = pygame.transform.scale(black_bishop, (45, 45))
black_knight = pygame.image.load('assets/1024px/b_knight_png_shadow_1024px.png'); black_knight = pygame.transform.scale(black_knight, (80, 80)); black_knight_small = pygame.transform.scale(black_knight, (45, 45))
black_pawn = pygame.image.load('assets/1024px/b_pawn_png_shadow_1024px.png'); black_pawn = pygame.transform.scale(black_pawn, (65, 65)); black_pawn_small = pygame.transform.scale(black_pawn, (45, 45))
white_queen = pygame.image.load('assets/1024px/w_queen_png_shadow_1024px.png'); white_queen = pygame.transform.scale(white_queen, (80, 80)); white_queen_small = pygame.transform.scale(white_queen, (45, 45))
white_king = pygame.image.load('assets/1024px/w_king_png_shadow_1024px.png'); white_king = pygame.transform.scale(white_king, (80, 80)); white_king_small = pygame.transform.scale(white_king, (45, 45))
white_rook = pygame.image.load('assets/1024px/w_rook_png_shadow_1024px.png'); white_rook = pygame.transform.scale(white_rook, (80, 80)); white_rook_small = pygame.transform.scale(white_rook, (45, 45))
white_bishop = pygame.image.load('assets/1024px/w_bishop_png_shadow_1024px.png'); white_bishop = pygame.transform.scale(white_bishop, (80, 80)); white_bishop_small = pygame.transform.scale(white_bishop, (45, 45))
white_knight = pygame.image.load('assets/1024px/w_knight_png_shadow_1024px.png'); white_knight = pygame.transform.scale(white_knight, (80, 80)); white_knight_small = pygame.transform.scale(white_knight, (45, 45))
white_pawn = pygame.image.load('assets/1024px/w_pawn_png_shadow_1024px.png'); white_pawn = pygame.transform.scale(white_pawn, (65, 65)); white_pawn_small = pygame.transform.scale(white_pawn, (45, 45))

white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
white_promotions = ['bishop', 'knight', 'rook', 'queen']
white_moved = [False] * 16
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small, white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small, black_rook_small, black_bishop_small]
black_promotions = ['bishop', 'knight', 'rook', 'queen']
black_moved = [False] * 16
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
counter, winner, game_over = 0, '', False
white_ep, black_ep = (100, 100), (100, 100)
white_promote, black_promote, promo_index = False, False, 100
check = False
castling_moves = []

# 퀴즈 관련 변수
QUIZ_CATEGORIES = ['상식', '시사', '경제', '스포츠', '속담', '사자성어', '역사', '과학', '문화/예술']
# #### 킹 스킬 기능 추가 ####
quiz_state = 'INACTIVE' # INACTIVE, VERSUS, KING_SKILL_SELECTION, CATEGORY_SELECTION, ANSWERING, RESULT

# 퀴즈 한 판에 대한 정보를 담는 변수
quiz_info = {
    'categories': [],
    'question': '',
    'answer': '',
    'answer_clean': '',
    'user_answer': '',
    'result': None,
    'start_time': 0,
    'result_time': 0,
    'limit_time': 30, # 기본 제한 시간
    'hint_time_ratio': 0.5, # 힌트가 나오는 시간 비율 (절반)
    'reroll_available': False, # 비숍 스킬: 퀴즈 교체 가능 여부
    'questions_to_solve': 1, # 퀸 방어 스킬: 풀어야 할 문제 수
    'current_question_index': 0,
    'king_skill_options': [], # 킹 스킬: 선택 가능한 스킬 목록
}

# 공격 정보를 저장할 변수
attack_context = {'attacker_color': None, 'attacker_piece': '', 'defender_piece': '', 'attacker_index': None, 'defender_index': None, 'target_coords': None, 'original_attacker_coords': None, 'original_turn_step': 0}