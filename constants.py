# --- START OF FILE constants.py (최종 수정본) ---

import pygame
pygame.init()

WIDTH = 1000
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('QuiChess: The Quiz Chess Game!')
# 폰트는 시스템에 따라 없을 수 있으므로, 기본 폰트로 변경하거나 맞는 폰트 파일을 준비해야 합니다.
# 'malgungothic'이 없다면 'freesansbold.ttf' 또는 None을 사용하세요.
try:
    font = pygame.font.SysFont('malgungothic', 20)
    medium_font = pygame.font.SysFont('malgungothic', 40)
    big_font = pygame.font.SysFont('malgungothic', 50)
except:
    print("경고: '맑은 고딕' 폰트를 찾을 수 없습니다. 기본 폰트로 대체합니다.")
    font = pygame.font.Font(None, 24)
    medium_font = pygame.font.Font(None, 48)
    big_font = pygame.font.Font(None, 60)

timer = pygame.time.Clock()
fps = 60
# game variables and images
white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                   (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook',
                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7),
                   (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
captured_pieces_white = []
captured_pieces_black = []
# 0 - whites turn no selection: 1-whites turn piece selected: 2- black turn no selection, 3 - black turn piece selected
turn_step = 0
selection = 100
valid_moves = []
# load in game piece images
black_queen = pygame.image.load('assets/1024px/b_queen_png_shadow_1024px.png')
black_queen = pygame.transform.scale(black_queen, (80, 80))
black_queen_small = pygame.transform.scale(black_queen, (45, 45))
black_king = pygame.image.load('assets/1024px/b_king_png_shadow_1024px.png')
black_king = pygame.transform.scale(black_king, (80, 80))
black_king_small = pygame.transform.scale(black_king, (45, 45))
black_rook = pygame.image.load('assets/1024px/b_rook_png_shadow_1024px.png')
black_rook = pygame.transform.scale(black_rook, (80, 80))
black_rook_small = pygame.transform.scale(black_rook, (45, 45))
black_bishop = pygame.image.load('assets/1024px/b_bishop_png_shadow_1024px.png')
black_bishop = pygame.transform.scale(black_bishop, (80, 80))
black_bishop_small = pygame.transform.scale(black_bishop, (45, 45))
black_knight = pygame.image.load('assets/1024px/b_knight_png_shadow_1024px.png')
black_knight = pygame.transform.scale(black_knight, (80, 80))
black_knight_small = pygame.transform.scale(black_knight, (45, 45))
black_pawn = pygame.image.load('assets/1024px/b_pawn_png_shadow_1024px.png')
black_pawn = pygame.transform.scale(black_pawn, (65, 65))
black_pawn_small = pygame.transform.scale(black_pawn, (45, 45))
white_queen = pygame.image.load('assets/1024px/w_queen_png_shadow_1024px.png')
white_queen = pygame.transform.scale(white_queen, (80, 80))
white_queen_small = pygame.transform.scale(white_queen, (45, 45))
white_king = pygame.image.load('assets/1024px/w_king_png_shadow_1024px.png')
white_king = pygame.transform.scale(white_king, (80, 80))
white_king_small = pygame.transform.scale(white_king, (45, 45))
white_rook = pygame.image.load('assets/1024px/w_rook_png_shadow_1024px.png')
white_rook = pygame.transform.scale(white_rook, (80, 80))
white_rook_small = pygame.transform.scale(white_rook, (45, 45))
white_bishop = pygame.image.load('assets/1024px/w_bishop_png_shadow_1024px.png')
white_bishop = pygame.transform.scale(white_bishop, (80, 80))
white_bishop_small = pygame.transform.scale(white_bishop, (45, 45))
white_knight = pygame.image.load('assets/1024px/w_knight_png_shadow_1024px.png')
white_knight = pygame.transform.scale(white_knight, (80, 80))
white_knight_small = pygame.transform.scale(white_knight, (45, 45))
white_pawn = pygame.image.load('assets/1024px/w_pawn_png_shadow_1024px.png')
white_pawn = pygame.transform.scale(white_pawn, (65, 65))
white_pawn_small = pygame.transform.scale(white_pawn, (45, 45))

white_images = [white_pawn, white_queen, white_king, white_knight, white_rook, white_bishop]
white_promotions = ['bishop', 'knight', 'rook', 'queen']
white_moved = [False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False]
small_white_images = [white_pawn_small, white_queen_small, white_king_small, white_knight_small,
                      white_rook_small, white_bishop_small]
black_images = [black_pawn, black_queen, black_king, black_knight, black_rook, black_bishop]
small_black_images = [black_pawn_small, black_queen_small, black_king_small, black_knight_small,
                      black_rook_small, black_bishop_small]
black_promotions = ['bishop', 'knight', 'rook', 'queen']
black_moved = [False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False]
piece_list = ['pawn', 'queen', 'king', 'knight', 'rook', 'bishop']
# check variables/ flashing counter
counter = 0
winner = ''
game_over = False
white_ep = (100, 100)
black_ep = (100, 100)
white_promote = False
black_promote = False
promo_index = 100
check = False
castling_moves = []

# 퀴즈 관련 변수
QUIZ_CATEGORIES = ['상식', '시사', '경제', '스포츠', '속담', '사자성어', '역사', '과학', '문화/예술']
quiz_state = 'INACTIVE'  # INACTIVE, CATEGORY_SELECTION, ANSWERING, RESULT
quiz_info = {
    'categories': [],
    'question': '',
    'answer': '',
    'answer_clean': '',
    'user_answer': '',
    'result': None, # True: 정답, False: 오답
    'result_time': 0
}

# 공격 정보를 저장할 변수
attack_context = {
    'attacker_color': None,
    'attacker_index': None,
    'defender_index': None,
    'target_coords': None,
    'original_attacker_coords': None
}

# --- END OF FILE constants.py (최종 수정본) ---