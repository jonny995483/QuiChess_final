# 퀴즈 탑재 체스 최종 완성본

import pygame
import random
import time
from constants import *
import gemini_quiz

# Gemini API 설정
gemini_quiz.setup_gemini()

regame_btn_rect = pygame.Rect(810, 820, 180, 60)


# 재시작시 메세지 표시시
def reset_game(show_message=True):
    global white_pieces, white_locations, white_moved, black_pieces, black_locations, black_moved
    global captured_pieces_white, captured_pieces_black, turn_step, selection, valid_moves
    global winner, game_over, white_ep, black_ep, white_options, black_options, selected_piece
    global notification_message

    white_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook'] + ['pawn'] * 8
    white_locations = [(i, 0) for i in range(8)] + [(i, 1) for i in range(8)]
    white_moved = [False] * 16
    black_pieces = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop', 'knight', 'rook'] + ['pawn'] * 8
    black_locations = [(i, 7) for i in range(8)] + [(i, 6) for i in range(8)]
    black_moved = [False] * 16

    captured_pieces_white, captured_pieces_black = [], []
    turn_step, selection, valid_moves = 0, 100, []
    winner, game_over = '', False
    white_ep, black_ep = (100, 100), (100, 100)
    white_options, black_options = [], []
    selected_piece = None

    black_options = check_options(black_pieces, black_locations, 'black')
    white_options = check_options(white_pieces, white_locations, 'white')

    if show_message:
        notification_message['text'] = '게임을 다시 시작합니다.'
        notification_message['display_time'] = time.time() + 2
        print("게임이 재시작되었습니다.")


def draw_text_center(text, font_obj, color, surface, rect):
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_notification():
    if notification_message['text'] and time.time() < notification_message['display_time']:
        text = notification_message['text']
        rect = pygame.Rect(100, 50, 600, 60)
        bg_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (0, 0, 0, 180), bg_surface.get_rect(), border_radius=15)
        screen.blit(bg_surface, rect.topleft)
        draw_text_center(text, font, 'white', screen, rect)
    else:
        notification_message['text'] = ''


def draw_quiz_ui():
    overlay = pygame.Surface((800, 800), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    if quiz_state == 'VERSUS':
        attacker_color = attack_context['attacker_color']
        attacker_images = white_images if attacker_color == 'white' else black_images
        attacker_img = attacker_images[piece_list.index(attack_context['attacker_piece'])]
        defender_images = black_images if attacker_color == 'white' else white_images
        defender_img = defender_images[piece_list.index(attack_context['defender_piece'])]
        attacker_img_large = pygame.transform.scale(attacker_img, (150, 150))
        defender_img_large = pygame.transform.scale(defender_img, (150, 150))

        screen.blit(attacker_img_large, (150, 325));
        screen.blit(defender_img_large, (500, 325))
        draw_text_center('VS', big_font, 'red', screen, pygame.Rect(0, 350, 800, 100))
        draw_text_center('잠시 후 퀴즈가 시작됩니다...', font, 'light gray', screen, pygame.Rect(0, 500, 800, 100))

    elif quiz_state == 'KING_SKILL_SELECTION':
        draw_text_center('킹의 수비 스킬 발동!', big_font, 'gold', screen, pygame.Rect(0, 100, 800, 100))
        draw_text_center('사용할 아군 기물의 스킬을 선택하세요.', font, 'white', screen, pygame.Rect(0, 180, 800, 50))
        for i, (piece_name, skill_desc) in enumerate(quiz_info['king_skill_options']):
            btn_rect = pygame.Rect(150, 250 + i * 80, 500, 60)
            pygame.draw.rect(screen, 'dark violet', btn_rect);
            pygame.draw.rect(screen, 'white', btn_rect, 3)
            draw_text_center(f"{piece_name.title()}: {skill_desc}", font, 'white', screen, btn_rect)

    elif quiz_state == 'CATEGORY_SELECTION':
        draw_text_center('퀴즈 분야를 선택하세요!', big_font, 'white', screen, pygame.Rect(0, 100, 800, 100))
        for i, category in enumerate(quiz_info['categories']):
            btn_rect = pygame.Rect(250, 250 + i * 100, 300, 80)
            pygame.draw.rect(screen, 'dark cyan', btn_rect);
            pygame.draw.rect(screen, 'white', btn_rect, 3)
            draw_text_center(category, medium_font, 'white', screen, btn_rect)

    elif quiz_state == 'ANSWERING':
        current_time = time.time();
        elapsed_time = current_time - quiz_info['start_time']
        remaining_time = max(0, quiz_info['limit_time'] - elapsed_time)
        timer_text = f"남은 시간: {remaining_time:.1f}초";
        timer_color = 'yellow' if remaining_time > 10 else 'red'
        draw_text_center(timer_text, font, timer_color, screen, pygame.Rect(0, 50, 800, 50))

        if quiz_info['questions_to_solve'] > 1:
            draw_text_center(f"문제 {quiz_info['current_question_index'] + 1} / {quiz_info['questions_to_solve']}", font,
                             'white', screen, pygame.Rect(0, 90, 800, 50))

        q_rect = pygame.Rect(50, 150, 700, 150)
        words, lines, current_line = quiz_info['question'].split(' '), [], ""
        for word in words:
            if font.size(current_line + " " + word)[0] < q_rect.width - 20:
                current_line += " " + word
            else:
                lines.append(current_line.strip()); current_line = word
        lines.append(current_line.strip())
        for i, line in enumerate(lines):
            draw_text_center(line, font, 'white', screen,
                             pygame.Rect(q_rect.x, q_rect.y + 20 + i * font.get_linesize(), q_rect.width,
                                         font.get_linesize()))

        if quiz_info['skill_message'] and time.time() - quiz_info['start_time'] < 4:
            draw_text_center(quiz_info['skill_message'], font, 'orange', screen, pygame.Rect(0, 360, 800, 50))

        hint_text = ""
        if remaining_time <= quiz_info['limit_time'] * quiz_info['hint_time_ratio']:
            hint_text = "힌트: " + "-" * len(quiz_info['answer_clean'])
        if remaining_time <= 15:
            if attack_context['attacker_piece'] == 'queen':
                hint_text = f"힌트: {quiz_info['answer'][0]}" + "-" * (len(quiz_info['answer_clean']) - 1)
            if attack_context['attacker_piece'] == 'knight' and 'knight_hint' in quiz_info:
                hint_text = f"힌트: {quiz_info['knight_hint']}"
        if hint_text:
            draw_text_center(hint_text, font, 'cyan', screen, pygame.Rect(0, 320, 800, 50))

        if quiz_info['reroll_available']:
            reroll_btn = pygame.Rect(300, 550, 200, 50)
            pygame.draw.rect(screen, 'orange', reroll_btn);
            pygame.draw.rect(screen, 'white', reroll_btn, 2)
            draw_text_center("퀴즈 교체 (클릭)", font, 'black', screen, reroll_btn)

        input_box = pygame.Rect(150, 400, 500, 60)
        pygame.draw.rect(screen, 'white', input_box);
        pygame.draw.rect(screen, 'black', input_box, 3)
        input_surface = medium_font.render(quiz_info['user_answer'], True, 'black')
        screen.blit(input_surface,
                    (input_box.x + 10, input_box.y + (input_box.height - input_surface.get_height()) / 2))
        draw_text_center("답을 입력하고 Enter를 누르세요", font, 'light gray', screen, pygame.Rect(0, 470, 800, 50))

    elif quiz_state == 'RESULT':
        msg, msg_color = ("정답입니다!", 'green') if quiz_info['result'] else ("오답입니다!", 'red')
        draw_text_center(msg, big_font, msg_color, screen, pygame.Rect(0, 200, 800, 100))
        draw_text_center(f"정답: {quiz_info['answer']}", medium_font, 'white', screen, pygame.Rect(0, 350, 800, 100))
        draw_text_center("잠시 후 게임으로 돌아갑니다...", font, 'light gray', screen, pygame.Rect(0, 500, 800, 100))


def apply_piece_skills():
    global quiz_info
    attacker_piece, defender_piece = attack_context['attacker_piece'], attack_context['defender_piece']

    if attacker_piece == 'rook' and defender_piece == 'rook':
        quiz_info.update({'limit_time': 30, 'hint_time_ratio': 0.5, 'reroll_available': False, 'questions_to_solve': 1})
        return

    quiz_info.update({'limit_time': 30, 'hint_time_ratio': 0.5, 'reroll_available': False, 'questions_to_solve': 1,
                      'skill_message': ''})
    if 'knight_hint' in quiz_info: del quiz_info['knight_hint']

    if attacker_piece == 'rook':
        quiz_info['limit_time'] = 45; quiz_info['hint_time_ratio'] = 30 / 45
    elif attacker_piece == 'bishop':
        quiz_info['reroll_available'] = True
    elif attacker_piece == 'knight':
        answer = quiz_info['answer_clean']
        if len(answer) > 0 and all('가' <= char <= '힣' for char in answer):
            rand_idx = random.randint(0, len(answer) - 1)
            hint_chars = ['-' for _ in answer];
            chosung = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
            cho_code = (ord(answer[rand_idx]) - ord('가')) // 588
            hint_chars[rand_idx] = chosung[cho_code];
            quiz_info['knight_hint'] = "".join(hint_chars)

    if defender_piece == 'queen':
        quiz_info['questions_to_solve'] = 2
    elif defender_piece == 'rook':
        quiz_info['limit_time'] = 20; quiz_info['hint_time_ratio'] = 10 / 20
    elif defender_piece == 'bishop':
        quiz_info['question'] = quiz_info['question'][::-1]


def resolve_attack():
    global turn_step, selection, valid_moves, white_options, black_options, white_ep, black_ep, winner
    context = attack_context
    if quiz_info['result']:
        pieces, locs, moved, cap_pieces, opp_pieces, opp_locs, opp_moved = (white_pieces, white_locations, white_moved,
                                                                            captured_pieces_white, black_pieces,
                                                                            black_locations, black_moved) if context[
                                                                                                                 'attacker_color'] == 'white' else (
            black_pieces, black_locations, black_moved, captured_pieces_black, white_pieces, white_locations,
            white_moved)
        locs[context['attacker_index']] = context['target_coords'];
        moved[context['attacker_index']] = True
        cap_pieces.append(opp_pieces[context['defender_index']])
        if opp_pieces[context['defender_index']] == 'king': winner = context['attacker_color']
        opp_pieces.pop(context['defender_index']);
        opp_locs.pop(context['defender_index']);
        opp_moved.pop(context['defender_index'])
    else:
        pieces, locs, moved, cap_pieces = (white_pieces, white_locations, white_moved, captured_pieces_black) if \
        context['attacker_color'] == 'white' else (black_pieces, black_locations, black_moved, captured_pieces_white)
        cap_pieces.append(pieces[context['attacker_index']])
        if pieces[context['attacker_index']] == 'king': winner = 'black' if context[
                                                                                'attacker_color'] == 'white' else 'white'
        pieces.pop(context['attacker_index']);
        locs.pop(context['attacker_index']);
        moved.pop(context['attacker_index'])
    new_ep = check_ep(context['original_attacker_coords'], context['target_coords'], context['original_turn_step'])
    if context['attacker_color'] == 'white':
        white_ep, black_ep, turn_step = new_ep, (100, 100), 2
    else:
        black_ep, white_ep, turn_step = new_ep, (100, 100), 0
    black_options, white_options = check_options(black_pieces, black_locations, 'black'), check_options(white_pieces,
                                                                                                        white_locations,
                                                                                                        'white')
    selection, valid_moves = 100, []


def draw_board():
    for r in range(8):
        for c in range(8):
            color = (238, 238, 210) if (r + c) % 2 == 0 else (118, 150, 86)
            pygame.draw.rect(screen, color, [c * 100, r * 100, 100, 100])
    pygame.draw.rect(screen, 'gray', [0, 800, WIDTH, 100]);
    pygame.draw.rect(screen, 'gold', [0, 800, WIDTH, 100], 5)
    pygame.draw.rect(screen, 'gold', [800, 0, 200, HEIGHT], 5)
    status_text = ['하양: 기물 선택', '하양: 이동 위치 선택', '검정: 기물 선택', '검정: 이동 위치 선택']
    if turn_step < len(status_text): screen.blit(big_font.render(status_text[turn_step], True, 'black'), (20, 820))
    for i in range(9):
        pygame.draw.line(screen, 'black', (0, 100 * i), (800, 100 * i), 2);
        pygame.draw.line(screen, 'black', (100 * i, 0), (100 * i, 800), 2)
    pygame.draw.rect(screen, (210, 180, 140), regame_btn_rect);
    pygame.draw.rect(screen, 'black', regame_btn_rect, 2)
    draw_text_center('REGAME', medium_font, 'black', screen, regame_btn_rect)
    if white_promote or black_promote:
        pygame.draw.rect(screen, 'gray', [0, 800, WIDTH - 200, 100]);
        pygame.draw.rect(screen, 'gold', [0, 800, WIDTH - 200, 100], 5)
        screen.blit(big_font.render('승진할 기물을 선택하세요', True, 'black'), (20, 820))


def draw_pieces():
    for i in range(len(white_pieces)):
        x, y = white_locations[i];
        is_pawn = white_pieces[i] == 'pawn'
        screen.blit(white_images[piece_list.index(white_pieces[i])],
                    (x * 100 + (17 if is_pawn else 10), y * 100 + (17 if is_pawn else 10)))
        if turn_step < 2 and selection == i: pygame.draw.rect(screen, 'red', [x * 100, y * 100, 100, 100], 4)
    for i in range(len(black_pieces)):
        x, y = black_locations[i];
        is_pawn = black_pieces[i] == 'pawn'
        screen.blit(black_images[piece_list.index(black_pieces[i])],
                    (x * 100 + (17 if is_pawn else 10), y * 100 + (17 if is_pawn else 10)))
        if turn_step >= 2 and selection == i: pygame.draw.rect(screen, 'blue', [x * 100, y * 100, 100, 100], 4)


def check_options(pieces, locations, turn):
    global castling_moves
    all_moves_list, castling_moves = [], []
    opponent_options = black_options if turn == 'white' else white_options
    for i in range(len(pieces)):
        location, piece = locations[i], pieces[i]
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
    moves_list, castle_moves = [], check_castling(color, opponent_options)
    friends_list = white_locations if color == 'white' else black_locations
    for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]:
        target = (position[0] + dx, position[1] + dy)
        if 0 <= target[0] <= 7 and 0 <= target[1] <= 7 and target not in friends_list: moves_list.append(target)
    return moves_list, castle_moves


def check_queen(position, color): return check_bishop(position, color) + check_rook(position, color)


def check_bishop(position, color): return check_line_moves(position, color, [(1, -1), (-1, -1), (1, 1), (-1, 1)])


def check_rook(position, color): return check_line_moves(position, color, [(0, 1), (0, -1), (1, 0), (-1, 0)])


def check_line_moves(position, color, directions):
    moves_list, friends_list, enemies_list = [], *(
        (white_locations, black_locations) if color == 'white' else (black_locations, white_locations))
    for dx, dy in directions:
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
        if position[1] < 7 and (position[0], position[1] + 1) not in white_locations and (position[0], position[
                                                                                                           1] + 1) not in black_locations:
            moves_list.append((position[0], position[1] + 1))
            if position[1] == 1 and (position[0], position[1] + 2) not in white_locations and (position[0], position[
                                                                                                                1] + 2) not in black_locations: moves_list.append(
                (position[0], position[1] + 2))
        for dx in [1, -1]:
            if (position[0] + dx, position[1] + 1) in black_locations: moves_list.append(
                (position[0] + dx, position[1] + 1))
            if (position[0] + dx, position[1] + 1) == black_ep: moves_list.append(black_ep)
    else:
        if position[1] > 0 and (position[0], position[1] - 1) not in white_locations and (position[0], position[
                                                                                                           1] - 1) not in black_locations:
            moves_list.append((position[0], position[1] - 1))
            if position[1] == 6 and (position[0], position[1] - 2) not in white_locations and (position[0], position[
                                                                                                                1] - 2) not in black_locations: moves_list.append(
                (position[0], position[1] - 2))
        for dx in [1, -1]:
            if (position[0] + dx, position[1] - 1) in white_locations: moves_list.append(
                (position[0] + dx, position[1] - 1))
            if (position[0] + dx, position[1] - 1) == white_ep: moves_list.append(white_ep)
    return moves_list


def check_knight(position, color):
    moves_list, friends_list = [], white_locations if color == 'white' else black_locations
    for dx, dy in [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]:
        target = (position[0] + dx, position[1] + dy)
        if 0 <= target[0] <= 7 and 0 <= target[1] <= 7 and target not in friends_list: moves_list.append(target)
    return moves_list


def check_valid_moves():
    options_list = white_options if turn_step < 2 else black_options
    return options_list[selection] if selection < len(options_list) else []


def draw_valid(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves: pygame.draw.circle(screen, color, (move[0] * 100 + 50, move[1] * 100 + 50), 15, 4)


def draw_captured():
    for i, piece in enumerate(captured_pieces_white): screen.blit(small_black_images[piece_list.index(piece)],
                                                                  (825, 5 + 50 * i))
    for i, piece in enumerate(captured_pieces_black): screen.blit(small_white_images[piece_list.index(piece)],
                                                                  (925, 5 + 50 * i))


def draw_check():
    global check
    check = False
    king_color, opp_options, rect_color = ('white', black_options, 'dark red') if turn_step < 2 else ('black',
                                                                                                      white_options,
                                                                                                      'dark blue')
    pieces, locations = (white_pieces, white_locations) if king_color == 'white' else (black_pieces, black_locations)
    if 'king' in pieces:
        king_loc = locations[pieces.index('king')]
        if any(king_loc in moves for moves in opp_options):
            check = True
            if counter < 15: pygame.draw.rect(screen, rect_color, [king_loc[0] * 100, king_loc[1] * 100, 100, 100], 5)


def draw_game_over():
    pygame.draw.rect(screen, 'black', [200, 200, 400, 100])
    draw_text_center(f'{winner.title()} Wins!', big_font, 'white', screen, pygame.Rect(200, 200, 400, 50))
    draw_text_center('Press ENTER to Restart', font, 'white', screen, pygame.Rect(200, 250, 400, 50))


def check_ep(old_coords, new_coords, current_turn_step):
    pieces, locs = (white_pieces, white_locations) if current_turn_step < 2 else (black_pieces, black_locations)
    if old_coords not in locs: return (100, 100)
    idx = locs.index(old_coords)
    if idx >= len(pieces) or pieces[idx] != 'pawn' or abs(old_coords[1] - new_coords[1]) != 2: return (100, 100)
    return (new_coords[0], (new_coords[1] + old_coords[1]) // 2)


def check_castling(color, opponent_options):
    castle_moves, pieces, locs, moved, start_row = [], *(
        ((white_pieces, white_locations, white_moved, 0)) if color == 'white' else (
        (black_pieces, black_locations, black_moved, 7)))
    if 'king' not in pieces: return []
    king_index = pieces.index('king');
    king_loc = locs[king_index]
    if moved[king_index] or check: return []
    all_opponent_moves = {move for moves in opponent_options for move in moves}
    for rook_start_col, direction in [(0, 1), (7, -1)]:
        rook_full_coord = (rook_start_col, start_row)
        if rook_full_coord in locs and not moved[locs.index(rook_full_coord)]:
            path_end = king_loc[0] if direction == 1 else rook_start_col
            path_start = rook_start_col + direction if direction == 1 else king_loc[0] + direction
            path = [(c, start_row) for c in range(path_start, path_end, direction)]
            if all(p not in white_locations and p not in black_locations for p in path):
                king_path = [(king_loc[0] + i * direction, start_row) for i in range(1, 3)]
                if not any(p in all_opponent_moves for p in king_path): castle_moves.append(
                    ((king_loc[0] + 2 * direction, start_row), (king_loc[0] + 1 * direction, start_row)))
    return castle_moves


def draw_castling(moves):
    color = 'red' if turn_step < 2 else 'blue'
    for move in moves: pygame.draw.circle(screen, color, (move[0][0] * 100 + 50, move[0][1] * 100 + 50), 20, 4)


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
    for i, piece_name in enumerate(promotions): screen.blit(images[piece_list.index(piece_name)], (860, 5 + 100 * i))
    pygame.draw.rect(screen, color, [800, 0, 200, 420], 8)


def select_promotion():
    global white_promote, black_promote, white_options, black_options, promo_index
    mouse_pos, left_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]
    x, y = mouse_pos[0] // 100, mouse_pos[1] // 100
    if left_click and x > 7 and y < 4:
        promoted_piece = white_promotions[y]
        if white_promote:
            white_pieces[promo_index], white_promote = promoted_piece, False
        elif black_promote:
            black_pieces[promo_index], black_promote = promoted_piece, False
        black_options, white_options = check_options(black_pieces, black_locations, 'black'), check_options(
            white_pieces, white_locations, 'white')


# 메인 게임 루프
notification_message = {'text': '', 'display_time': 0}
reset_game(show_message=False)  # #### 재시작 기능 수정: 최초 실행 시 메시지 미표시 ####
run = True

while run:
    timer.tick(fps)
    counter = (counter + 1) % 30
    screen.fill('dark gray')
    draw_board();
    draw_pieces();
    draw_captured();
    draw_check()
    if not game_over and (white_promote or black_promote): draw_promotion(); select_promotion()
    if selection != 100:
        valid_moves = check_valid_moves();
        draw_valid(valid_moves)
        if selected_piece == 'king': draw_castling(castling_moves)
    if quiz_state != 'INACTIVE': draw_quiz_ui()
    draw_notification()

    if quiz_state == 'VERSUS' and time.time() - quiz_info['start_time'] > 2:
        if attack_context['defender_piece'] == 'king':
            quiz_state = 'KING_SKILL_SELECTION'
            def_color = 'black' if attack_context['attacker_color'] == 'white' else 'white'
            def_pieces = black_pieces if def_color == 'black' else white_pieces
            skill_map = {'queen': '문제 2개 풀기', 'rook': '제한시간 20초', 'bishop': '질문 뒤집기', 'knight': '주제 변경'}
            quiz_info['king_skill_options'] = [(p, skill_map[p]) for p in set(def_pieces) if p in skill_map]
        else:
            quiz_state = 'CATEGORY_SELECTION'

    if quiz_state == 'ANSWERING' and time.time() - quiz_info['start_time'] > quiz_info['limit_time']:
        pygame.key.stop_text_input();
        quiz_info['result'] = False
        quiz_state, quiz_info['result_time'] = 'RESULT', time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if regame_btn_rect.collidepoint(event.pos):
                reset_game();
                continue

        if quiz_state != 'INACTIVE':
            if quiz_state == 'KING_SKILL_SELECTION' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (piece_name, _) in enumerate(quiz_info['king_skill_options']):
                    if pygame.Rect(150, 250 + i * 80, 500, 60).collidepoint(event.pos):
                        attack_context['defender_piece'] = piece_name;
                        quiz_state = 'CATEGORY_SELECTION'
                        break
            if quiz_state == 'CATEGORY_SELECTION' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, category in enumerate(quiz_info['categories']):
                    if pygame.Rect(250, 250 + i * 100, 300, 80).collidepoint(event.pos):
                        original_category = category
                        if attack_context['defender_piece'] == 'knight':
                            new_category = random.choice([c for c in QUIZ_CATEGORIES if c != category]);
                            category = new_category
                            notification_message['text'] = f"나이트 스킬! 주제가 {original_category}에서 {new_category}로 변경됩니다!"
                            notification_message['display_time'] = time.time() + 3

                        quiz_data = gemini_quiz.generate_quiz(category)
                        quiz_info.update(quiz_data);
                        quiz_info['user_answer'] = ''
                        apply_piece_skills();
                        quiz_info['start_time'] = time.time()
                        quiz_state = 'ANSWERING';
                        pygame.key.start_text_input()
                        pygame.key.set_text_input_rect(pygame.Rect(150, 400, 500, 60))
                        break
            if quiz_state == 'ANSWERING':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if quiz_info['reroll_available'] and pygame.Rect(300, 550, 200, 50).collidepoint(event.pos):
                        quiz_info['reroll_available'] = False
                        quiz_data = gemini_quiz.generate_quiz(quiz_info['categories'][0])
                        quiz_info.update(quiz_data);
                        quiz_info['user_answer'] = '';
                        apply_piece_skills()
                if event.type == pygame.TEXTINPUT:
                    quiz_info['user_answer'] += event.text
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_correct = (''.join(filter(str.isalnum, quiz_info['user_answer'].lower())) == quiz_info[
                            'answer_clean'])
                        if is_correct and quiz_info['current_question_index'] < quiz_info['questions_to_solve'] - 1:
                            quiz_info['current_question_index'] += 1
                            quiz_data = gemini_quiz.generate_quiz(quiz_info['categories'][0])
                            quiz_info.update(quiz_data);
                            quiz_info['user_answer'] = ''
                            apply_piece_skills();
                            quiz_info['start_time'] = time.time()
                        else:
                            pygame.key.stop_text_input();
                            quiz_info['result'] = is_correct
                            quiz_state, quiz_info['result_time'] = 'RESULT', time.time()
                    elif event.key == pygame.K_BACKSPACE:
                        quiz_info['user_answer'] = quiz_info['user_answer'][:-1]
            continue

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            x, y = event.pos[0] // 100, event.pos[1] // 100;
            click_coords = (x, y)
            current_pieces, current_locs, opp_locs, _ = (white_pieces, white_locations, black_locations,
                                                         white_moved) if turn_step < 2 else (black_pieces,
                                                                                             black_locations,
                                                                                             white_locations,
                                                                                             black_moved)

            if click_coords in current_locs:
                selection = current_locs.index(click_coords);
                selected_piece = current_pieces[selection]
                if turn_step % 2 == 0: turn_step += 1
            elif selection != 100:
                original_coords = current_locs[selection]


                def end_turn():
                    global turn_step, selection, valid_moves, black_options, white_options, white_ep, black_ep
                    new_ep = check_ep(original_coords, click_coords, turn_step)
                    if turn_step < 2:
                        white_ep, black_ep = (100, 100), new_ep
                    else:
                        white_ep, black_ep = new_ep, (100, 100)
                    turn_step = 2 if turn_step < 2 else 0
                    selection, valid_moves = 100, [];
                    black_options, white_options = check_options(black_pieces, black_locations, 'black'), check_options(
                        white_pieces, white_locations, 'white')


                if click_coords in valid_moves:
                    if click_coords in opp_locs:
                        defender_index = opp_locs.index(click_coords)
                        quiz_state = 'VERSUS';
                        quiz_info['start_time'] = time.time()
                        quiz_info['categories'] = random.sample(QUIZ_CATEGORIES, 3);
                        quiz_info['current_question_index'] = 0
                        attack_context.update(
                            {'attacker_color': 'white' if turn_step < 2 else 'black', 'attacker_piece': selected_piece,
                             'defender_piece': (black_pieces if turn_step < 2 else white_pieces)[defender_index],
                             'attacker_index': selection, 'defender_index': defender_index,
                             'target_coords': click_coords, 'original_attacker_coords': original_coords,
                             'original_turn_step': turn_step})
                        selection, valid_moves = 100, []
                    else:
                        locs, moved, _, opp_pieces, opp_locs, opp_moved, captured = (white_locations, white_moved,
                                                                                     white_ep, black_pieces,
                                                                                     black_locations, black_moved,
                                                                                     captured_pieces_white) if turn_step < 2 else (
                            black_locations, black_moved, black_ep, white_pieces, white_locations, white_moved,
                            captured_pieces_black)
                        locs[selection] = click_coords;
                        moved[selection] = True
                        ep_target, victim_y_offset = (black_ep, -1) if turn_step < 2 else (white_ep, 1)
                        if click_coords == ep_target and ep_target != (100, 100):
                            v_coord = (ep_target[0], ep_target[1] + victim_y_offset)
                            if v_coord in opp_locs:
                                v_idx = opp_locs.index(v_coord)
                                captured.append(opp_pieces.pop(v_idx));
                                opp_locs.pop(v_idx);
                                opp_moved.pop(v_idx)
                        end_turn()
                elif selected_piece == 'king' and any(click_coords == move[0] for move in castling_moves):
                    move = next(m for m in castling_moves if click_coords == m[0])
                    start_row = 0 if turn_step < 2 else 7
                    king_idx, rook_start_x = current_locs.index((4, start_row)), 0 if click_coords[0] < 4 else 7
                    rook_idx = current_locs.index((rook_start_x, start_row))
                    current_locs[king_idx], current_locs[rook_idx] = move[0], move[1]
                    current_moved[king_idx], current_moved[rook_idx] = True, True
                    end_turn()

        if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_RETURN:
            reset_game()

    if quiz_state == 'RESULT' and time.time() - quiz_info['result_time'] > 2.5:
        resolve_attack();
        quiz_state = 'INACTIVE'
    if winner != '': game_over = True; draw_game_over()
    pygame.display.flip()
pygame.quit()
