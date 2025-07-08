# --- START OF FILE main_with_quiz.py (최종 수정본) ---

import pygame
import random
import time
from constants import *
import gemini_quiz

# Gemini API 설정
gemini_quiz.setup_gemini()


# 화면 중앙에 텍스트를 그리는 헬퍼 함수
def draw_text_center(text, font_obj, color, surface, rect):
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


# 퀴즈 UI 그리기 함수
def draw_quiz_ui():
    overlay = pygame.Surface((800, 800))
    overlay.set_alpha(220)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    if quiz_state == 'CATEGORY_SELECTION':
        draw_text_center('퀴즈 분야를 선택하세요!', big_font, 'white', screen, pygame.Rect(0, 100, 800, 100))
        for i, category in enumerate(quiz_info['categories']):
            btn_rect = pygame.Rect(250, 250 + i * 100, 300, 80)
            pygame.draw.rect(screen, 'dark cyan', btn_rect)
            pygame.draw.rect(screen, 'white', btn_rect, 3)
            draw_text_center(category, medium_font, 'white', screen, btn_rect)

    elif quiz_state == 'ANSWERING':
        q_rect = pygame.Rect(50, 150, 700, 200)
        # 긴 질문 줄바꿈 처리
        words = quiz_info['question'].split(' ')
        lines = []
        current_line = ""
        for word in words:
            if font.size(current_line + " " + word)[0] < q_rect.width - 20:  # 여백 추가
                current_line += " " + word
            else:
                lines.append(current_line.strip())
                current_line = word
        lines.append(current_line.strip())

        for i, line in enumerate(lines):
            line_rect = pygame.Rect(q_rect.x, q_rect.y + 50 + i * (font.get_linesize()), q_rect.width,
                                    font.get_linesize())
            draw_text_center(line, font, 'white', screen, line_rect)

        input_box = pygame.Rect(150, 400, 500, 60)
        pygame.draw.rect(screen, 'white', input_box)
        pygame.draw.rect(screen, 'black', input_box, 3)
        # 텍스트를 input_box 안에 그리기
        input_surface = medium_font.render(quiz_info['user_answer'], True, 'black')
        screen.blit(input_surface,
                    (input_box.x + 10, input_box.y + (input_box.height - input_surface.get_height()) / 2))

        draw_text_center("답을 입력하고 Enter를 누르세요", font, 'light gray', screen, pygame.Rect(0, 470, 800, 50))

    elif quiz_state == 'RESULT':
        msg = "정답입니다!" if quiz_info['result'] else "오답입니다!"
        msg_color = 'green' if quiz_info['result'] else 'red'
        draw_text_center(msg, big_font, msg_color, screen, pygame.Rect(0, 200, 800, 100))

        correct_answer_text = f"정답: {quiz_info['answer']}"
        draw_text_center(correct_answer_text, medium_font, 'white', screen, pygame.Rect(0, 350, 800, 100))

        draw_text_center("잠시 후 게임으로 돌아갑니다...", font, 'light gray', screen, pygame.Rect(0, 500, 800, 100))


# 퀴즈 결과에 따라 기물 처리
def resolve_attack():
    global turn_step, selection, valid_moves, white_options, black_options, white_ep, black_ep, winner

    attacker_color = attack_context['attacker_color']
    attacker_idx = attack_context['attacker_index']
    defender_idx = attack_context['defender_index']
    target_coords = attack_context['target_coords']

    if quiz_info['result']:  # 공격 성공
        if attacker_color == 'white':
            white_locations[attacker_idx] = target_coords
            white_moved[attacker_idx] = True
            captured_pieces_white.append(black_pieces[defender_idx])
            if black_pieces[defender_idx] == 'king': winner = 'white'
            black_pieces.pop(defender_idx)
            black_locations.pop(defender_idx)
            black_moved.pop(defender_idx)
        else:
            black_locations[attacker_idx] = target_coords
            black_moved[attacker_idx] = True
            captured_pieces_black.append(white_pieces[defender_idx])
            if white_pieces[defender_idx] == 'king': winner = 'black'
            white_pieces.pop(defender_idx)
            white_locations.pop(defender_idx)
            white_moved.pop(defender_idx)

    else:  # 공격 실패
        if attacker_color == 'white':
            captured_pieces_black.append(white_pieces[attacker_idx])
            if white_pieces[attacker_idx] == 'king': winner = 'black'
            white_pieces.pop(attacker_idx)
            white_locations.pop(attacker_idx)
            white_moved.pop(attacker_idx)
        else:
            captured_pieces_white.append(black_pieces[attacker_idx])
            if black_pieces[attacker_idx] == 'king': winner = 'white'
            black_pieces.pop(attacker_idx)
            black_locations.pop(attacker_idx)
            black_moved.pop(attacker_idx)

    if attacker_color == 'white':
        white_ep = check_ep(attack_context['original_attacker_coords'], target_coords)
        turn_step = 2
    else:
        black_ep = check_ep(attack_context['original_attacker_coords'], target_coords)
        turn_step = 0

    # 게임 상태 재계산
    black_options = check_options(black_pieces, black_locations, 'black')
    white_options = check_options(white_pieces, white_locations, 'white')
    selection = 100
    valid_moves = []


# 게임 보드 및 기물 그리기 함수들
def draw_board():
    for r in range(8):
        for c in range(8):
            color = 'light gray' if (r + c) % 2 == 0 else (181, 136, 99)  # 나무색 느낌
            pygame.draw.rect(screen, color, [c * 100, r * 100, 100, 100])

    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100])
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
    status_text = ['하양: 기물 선택', '하양: 이동 위치 선택', '검정: 기물 선택', '검정: 이동 위치 선택']
    if turn_step < len(status_text):
        screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))

    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2)
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))
    if white_promote or black_promote:
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH - 200, 100])
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH - 200, 100], 5)
        screen.blit(big_font.render('승진할 기물을 선택하세요', True, 'black'), (20, 820))


def draw_pieces():
    for i in range(len(white_pieces)):
        index = piece_list.index(white_pieces[i])
        if white_pieces[i] == 'pawn':
            screen.blit(white_pawn, (white_locations[i][0] * 100 + 17, white_locations[i][1] * 100 + 17))
        else:
            screen.blit(white_images[index], (white_locations[i][0] * 100 + 10, white_locations[i][1] * 100 + 10))
        if turn_step < 2 and selection == i:
            pygame.draw.rect(screen, 'red', [white_locations[i][0] * 100, white_locations[i][1] * 100, 100, 100], 4)

    for i in range(len(black_pieces)):
        index = piece_list.index(black_pieces[i])
        if black_pieces[i] == 'pawn':
            screen.blit(black_pawn, (black_locations[i][0] * 100 + 17, black_locations[i][1] * 100 + 17))
        else:
            screen.blit(black_images[index], (black_locations[i][0] * 100 + 10, black_locations[i][1] * 100 + 10))
        if turn_step >= 2 and selection == i:
            pygame.draw.rect(screen, 'blue', [black_locations[i][0] * 100, black_locations[i][1] * 100, 100, 100], 4)


# 기물 이동 로직 함수들
def check_options(pieces, locations, turn):
    global castling_moves
    moves_list, all_moves_list = [], []
    castling_moves = []

    opponent_options = black_options if turn == 'white' else white_options

    for i in range(len(pieces)):
        location = locations[i]
        piece = pieces[i]
        if piece == 'pawn':
            moves_list = check_pawn(location, turn)
        elif piece == 'rook':
            moves_list = check_rook(location, turn)
        elif piece == 'knight':
            moves_list = check_knight(location, turn)
        elif piece == 'bishop':
            moves_list = check_bishop(location, turn)
        elif piece == 'queen':
            moves_list = check_queen(location, turn)
        elif piece == 'king':
            moves_list, castling_moves = check_king(location, turn, opponent_options)
        all_moves_list.append(moves_list)
    return all_moves_list


def check_king(position, color, opponent_options):
    moves_list = []
    castle_moves = check_castling(color, opponent_options)
    friends_list = white_locations if color == 'white' else black_locations
    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list, castle_moves


def check_queen(position, color):
    moves_list = check_bishop(position, color)
    moves_list.extend(check_rook(position, color))
    return moves_list


def check_bishop(position, color):
    moves_list = []
    friends_list, enemies_list = (white_locations, black_locations) if color == 'white' else (black_locations,
                                                                                              white_locations)
    for dx, dy in [(1, -1), (-1, -1), (1, 1), (-1, 1)]:
        for i in range(1, 8):
            target = (position[0] + i * dx, position[1] + i * dy)
            if not (0 <= target[0] <= 7 and 0 <= target[1] <= 7): break
            if target in friends_list: break
            moves_list.append(target)
            if target in enemies_list: break
    return moves_list


def check_rook(position, color):
    moves_list = []
    friends_list, enemies_list = (white_locations, black_locations) if color == 'white' else (black_locations,
                                                                                              white_locations)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        for i in range(1, 8):
            target = (position[0] + i * dx, position[1] + i * dy)
            if not (0 <= target[0] <= 7 and 0 <= target[1] <= 7): break
            if target in friends_list: break
            moves_list.append(target)
            if target in enemies_list: break
    return moves_list


def check_pawn(position, color):
    moves_list = []
    if color == 'white':
        # 한 칸 앞으로
        if position[1] < 7 and (position[0], position[1] + 1) not in white_locations and (position[0], position[
                                                                                                           1] + 1) not in black_locations:
            moves_list.append((position[0], position[1] + 1))
            # 처음 움직일 때 두 칸 앞으로
            if position[1] == 1 and (position[0], position[1] + 2) not in white_locations and (position[0], position[
                                                                                                                1] + 2) not in black_locations:
                moves_list.append((position[0], position[1] + 2))
        # 대각선 공격
        if (position[0] + 1, position[1] + 1) in black_locations: moves_list.append((position[0] + 1, position[1] + 1))
        if (position[0] - 1, position[1] + 1) in black_locations: moves_list.append((position[0] - 1, position[1] + 1))
        # 앙파상
        if black_ep in [(position[0] + 1, position[1] + 1), (position[0] - 1, position[1] + 1)]: moves_list.append(
            black_ep)
    else:  # black
        if position[1] > 0 and (position[0], position[1] - 1) not in white_locations and (position[0], position[
                                                                                                           1] - 1) not in black_locations:
            moves_list.append((position[0], position[1] - 1))
            if position[1] == 6 and (position[0], position[1] - 2) not in white_locations and (position[0], position[
                                                                                                                1] - 2) not in black_locations:
                moves_list.append((position[0], position[1] - 2))
        if (position[0] + 1, position[1] - 1) in white_locations: moves_list.append((position[0] + 1, position[1] - 1))
        if (position[0] - 1, position[1] - 1) in white_locations: moves_list.append((position[0] - 1, position[1] - 1))
        if white_ep in [(position[0] + 1, position[1] - 1), (position[0] - 1, position[1] - 1)]: moves_list.append(
            white_ep)
    return moves_list


def check_knight(position, color):
    moves_list = []
    friends_list = white_locations if color == 'white' else black_locations
    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for dx, dy in targets:
        target = (position[0] + dx, position[1] + dy)
        if 0 <= target[0] <= 7 and 0 <= target[1] <= 7 and target not in friends_list:
            moves_list.append(target)
    return moves_list


def check_valid_moves():
    options_list = white_options if turn_step < 2 else black_options
    if selection >= len(options_list): return []  # 안전장치
    return options_list[selection]


def draw_valid(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves:
        pygame.draw.circle(screen, color, (move[0] * 100 + 50, move[1] * 100 + 50), 15, 4)


def draw_captured():
    for i, piece in enumerate(captured_pieces_white):
        index = piece_list.index(piece)
        screen.blit(small_black_images[index], (825, 5 + 50 * i))
    for i, piece in enumerate(captured_pieces_black):
        index = piece_list.index(piece)
        screen.blit(small_white_images[index], (925, 5 + 50 * i))


def draw_check():
    global check
    check = False

    # #### 오류 수정 부분 ####
    # nonlocal 대신 global을 사용합니다.
    def find_king_and_check(king_color, current_turn_options, rect_color):
        global check
        pieces, locations = (white_pieces, white_locations) if king_color == 'white' else (black_pieces,
                                                                                           black_locations)
        if 'king' in pieces:
            king_idx = pieces.index('king')
            king_loc = locations[king_idx]
            for moves in current_turn_options:
                if king_loc in moves:
                    check = True
                    if counter < 15:
                        pygame.draw.rect(screen, rect_color, [king_loc[0] * 100, king_loc[1] * 100, 100, 100], 5)
                    return  # 킹을 찾았으면 함수 종료

    if turn_step < 2:
        find_king_and_check('white', black_options, 'dark red')
    else:
        find_king_and_check('black', white_options, 'dark blue')


def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 100])
    draw_text_center(f'{winner} wins!', big_font, 'white', screen, pygame.Rect(200, 200, 400, 50))
    draw_text_center('Press ENTER to Restart', font, 'white', screen, pygame.Rect(200, 250, 400, 50))


def check_ep(old_coords, new_coords):
    pieces, locations = (white_pieces, white_locations) if turn_step < 2 else (black_pieces, black_locations)
    if old_coords not in locations: return (100, 100)
    piece = pieces[locations.index(old_coords)]
    if piece == 'pawn' and abs(old_coords[1] - new_coords[1]) > 1:
        return (new_coords[0], (new_coords[1] + old_coords[1]) // 2)
    return (100, 100)


def check_castling(color, opponent_options):
    castle_moves = []
    pieces, locs, moved, start_row, king_start_col = (white_pieces, white_locations, white_moved, 0,
                                                      4) if color == 'white' else (black_pieces, black_locations,
                                                                                   black_moved, 7, 4)

    if 'king' not in pieces: return []
    king_index = pieces.index('king')
    if moved[king_index] or check: return []

    # 캐슬링 경로상의 모든 칸을 확인
    all_opponent_moves = {move for moves in opponent_options for move in moves}

    # 퀸사이드 (a파일 룩)
    if (0, start_row) in locs and not moved[locs.index((0, start_row))]:
        path = [(c, start_row) for c in range(1, king_start_col)]
        if all(p not in white_locations and p not in black_locations for p in path):
            if not any(p in all_opponent_moves for p in path[1:]):  # 킹이 지나가는 두 칸만 확인
                castle_moves.append(((king_start_col - 2, start_row), (king_start_col - 1, start_row)))

    # 킹사이드 (h파일 룩)
    if (7, start_row) in locs and not moved[locs.index((7, start_row))]:
        path = [(c, start_row) for c in range(king_start_col + 1, 7)]
        if all(p not in white_locations and p not in black_locations for p in path):
            if not any(p in all_opponent_moves for p in path):
                castle_moves.append(((king_start_col + 2, start_row), (king_start_col + 1, start_row)))

    return castle_moves


def draw_castling(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves:
        pygame.draw.circle(screen, color, (move[0][0] * 100 + 50, move[0][1] * 100 + 50), 20, 4)


def check_promotion():
    for i, loc in enumerate(white_locations):
        if white_pieces[i] == 'pawn' and loc[1] == 7: return True, False, i
    for i, loc in enumerate(black_locations):
        if black_pieces[i] == 'pawn' and loc[1] == 0: return False, True, i
    return False, False, 100


def draw_promotion():
    color, promotions, images = ('white', white_promotions, white_images) if white_promote else ('black',
                                                                                                 black_promotions,
                                                                                                 black_images)
    pygame.draw.rect(screen, 'dark gray', [800, 0, 200, 420])
    for i, piece_name in enumerate(promotions):
        index = piece_list.index(piece_name)
        screen.blit(images[index], (860, 5 + 100 * i))
    pygame.draw.rect(screen, color, [800, 0, 200, 420], 8)


def select_promotion():
    global white_promote, black_promote, white_options, black_options
    mouse_pos, left_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]
    x_pos, y_pos = mouse_pos[0] // 100, mouse_pos[1] // 100
    if left_click and x_pos > 7 and y_pos < 4:
        promoted_piece = white_promotions[y_pos]
        if white_promote:
            white_pieces[promo_index] = promoted_piece
            white_promote = False
        elif black_promote:
            black_pieces[promo_index] = promoted_piece
            black_promote = False
        # 승진 후 게임 상태 즉시 업데이트
        black_options = check_options(black_pieces, black_locations, 'black')
        white_options = check_options(white_pieces, white_locations, 'white')


# ===== Main Game Loop =====
white_options, black_options = [], []
black_options = check_options(black_pieces, black_locations, 'black')
white_options = check_options(white_pieces, white_locations, 'white')
run = True
selected_piece = None

while run:
    timer.tick(fps)
    counter = (counter + 1) % 30
    screen.fill('dark gray')
    draw_board()
    draw_pieces()
    draw_captured()
    draw_check()

    if not game_over:
        white_promote, black_promote, promo_index = check_promotion()
        if white_promote or black_promote:
            draw_promotion()
            select_promotion()

    if selection != 100:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)
        if selected_piece == 'king':
            draw_castling(castling_moves)

    if quiz_state != 'INACTIVE':
        draw_quiz_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if quiz_state != 'INACTIVE':
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and quiz_state == 'CATEGORY_SELECTION':
                for i, category in enumerate(quiz_info['categories']):
                    btn_rect = pygame.Rect(250, 250 + i * 100, 300, 80)
                    if btn_rect.collidepoint(event.pos):
                        quiz_data = gemini_quiz.generate_quiz(category)
                        quiz_info.update({k: v for k, v in quiz_data.items() if k in quiz_info})
                        quiz_info.update(quiz_data)
                        quiz_state = 'ANSWERING'
                        break

            if event.type == pygame.KEYDOWN and quiz_state == 'ANSWERING':
                if event.key == pygame.K_RETURN:
                    user_ans_clean = ''.join(filter(str.isalnum, quiz_info['user_answer'].lower()))
                    quiz_info['result'] = (user_ans_clean == quiz_info['answer_clean'])
                    quiz_state = 'RESULT'
                    quiz_info['result_time'] = time.time()
                elif event.key == pygame.K_BACKSPACE:
                    quiz_info['user_answer'] = quiz_info['user_answer'][:-1]
                else:
                    quiz_info['user_answer'] += event.unicode
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            x, y = event.pos[0] // 100, event.pos[1] // 100
            click_coords = (x, y)

            # 턴 처리 로직
            current_pieces, current_locations, opponent_locations, current_moved = (white_pieces, white_locations,
                                                                                    black_locations,
                                                                                    white_moved) if turn_step < 2 else (
                black_pieces, black_locations, white_locations, black_moved)

            # 기물 선택
            if click_coords in current_locations:
                selection = current_locations.index(click_coords)
                selected_piece = current_pieces[selection]
                if turn_step % 2 == 0: turn_step += 1
            # 기물 이동
            elif selection != 100:
                original_coords = current_locations[selection]
                # 일반 이동
                if click_coords in valid_moves and click_coords not in opponent_locations:
                    current_locations[selection] = click_coords
                    current_moved[selection] = True
                    # 앙파상 처리
                    ep_target = white_ep if turn_step >= 2 else black_ep
                    ep_victim_y = ep_target[1] + (1 if turn_step >= 2 else -1)
                    if click_coords == ep_target:
                        victim_coord = (ep_target[0], ep_victim_y)
                        if victim_coord in opponent_locations:
                            v_idx = opponent_locations.index(victim_coord)
                            (captured_pieces_black if turn_step >= 2 else captured_pieces_white).append(
                                opponent_locations.pop(v_idx))
                            (white_pieces if turn_step >= 2 else black_pieces).pop(v_idx)
                            (white_moved if turn_step >= 2 else black_moved).pop(v_idx)

                    # 턴 넘기기
                    turn_step = (turn_step + 1) % 4
                    if turn_step % 2 == 0: turn_step = (turn_step + 2) % 4
                    white_ep, black_ep = (100, 100), (100, 100)
                    if selected_piece == 'pawn' and abs(original_coords[1] - click_coords[1]) == 2:
                        if turn_step < 2:
                            black_ep = (click_coords[0], click_coords[1] - 1)
                        else:
                            white_ep = (click_coords[0], click_coords[1] + 1)

                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')
                    selection, valid_moves = 100, []

                # 퀴즈로 이어지는 공격
                elif click_coords in valid_moves and click_coords in opponent_locations:
                    quiz_state, quiz_info['categories'] = 'CATEGORY_SELECTION', random.sample(QUIZ_CATEGORIES, 3)
                    attack_context.update(
                        {'attacker_color': 'white' if turn_step < 2 else 'black', 'attacker_index': selection,
                         'defender_index': opponent_locations.index(click_coords), 'target_coords': click_coords,
                         'original_attacker_coords': original_coords})
                    selection, valid_moves = 100, []

                # 캐슬링
                elif selected_piece == 'king' and any(click_coords == move[0] for move in castling_moves):
                    move = next(m for m in castling_moves if click_coords == m[0])
                    start_row = 0 if turn_step < 2 else 7
                    king_idx = current_locations.index((4, start_row))
                    rook_start_x = 0 if click_coords[0] < 4 else 7
                    rook_idx = current_locations.index((rook_start_x, start_row))
                    current_locations[king_idx], current_locations[rook_idx] = move[0], move[1]
                    current_moved[king_idx], current_moved[rook_idx] = True, True

                    turn_step = 2 if turn_step < 2 else 0
                    selection, valid_moves = 100, []
                    black_options = check_options(black_pieces, black_locations, 'black')
                    white_options = check_options(white_pieces, white_locations, 'white')

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                # Reset all variables
                white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook', 'pawn', 'pawn',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                white_locations = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (0, 1), (1, 1),
                                   (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
                black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook', 'pawn', 'pawn',
                                'pawn', 'pawn', 'pawn', 'pawn', 'pawn', 'pawn']
                black_locations = [(0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (0, 6), (1, 6),
                                   (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)]
                captured_pieces_white, captured_pieces_black = [], []
                white_moved = [False] * 16
                black_moved = [False] * 16
                turn_step, selection = 0, 100
                valid_moves, winner, game_over = [], '', False
                white_ep, black_ep = (100, 100), (100, 100)
                white_options, black_options = [], []
                black_options = check_options(black_pieces, black_locations, 'black')
                white_options = check_options(white_pieces, white_locations, 'white')

    if quiz_state == 'RESULT' and time.time() - quiz_info['result_time'] > 2:
        resolve_attack()
        quiz_state = 'INACTIVE'

    if winner != '':
        game_over = True
        draw_game_over()

    pygame.display.flip()
pygame.quit()