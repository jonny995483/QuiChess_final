# --- START OF FILE main_with_quiz.py (최종 완성본) ---

import pygame
import random
import time
from constants import *
import gemini_quiz

# Gemini API 설정
gemini_quiz.setup_gemini()


def draw_text_center(text, font_obj, color, surface, rect):
    text_surface = font_obj.render(text, True, color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)


def draw_quiz_ui():
    overlay = pygame.Surface((800, 800), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))

    if quiz_state == 'CATEGORY_SELECTION':
        draw_text_center('퀴즈 분야를 선택하세요!', big_font, 'white', screen, pygame.Rect(0, 100, 800, 100))
        for i, category in enumerate(quiz_info['categories']):
            btn_rect = pygame.Rect(250, 250 + i * 100, 300, 80)
            pygame.draw.rect(screen, 'dark cyan', btn_rect);
            pygame.draw.rect(screen, 'white', btn_rect, 3)
            draw_text_center(category, medium_font, 'white', screen, btn_rect)

    elif quiz_state == 'ANSWERING':
        q_rect = pygame.Rect(50, 150, 700, 200)
        words, lines, current_line = quiz_info['question'].split(' '), [], ""
        for word in words:
            if font.size(current_line + " " + word)[0] < q_rect.width - 20:
                current_line += " " + word
            else:
                lines.append(current_line.strip()); current_line = word
        lines.append(current_line.strip())
        for i, line in enumerate(lines):
            draw_text_center(line, font, 'white', screen,
                             pygame.Rect(q_rect.x, q_rect.y + 50 + i * font.get_linesize(), q_rect.width,
                                         font.get_linesize()))

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
        locs[context['attacker_index']] = context['target_coords']
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
    screen.blit(medium_font.render('FORFEIT', True, 'black'), (810, 830))
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
        if 0 <= target[0] <= 7 and 0 <= target[1] <= 7 and target not in friends_list:
            moves_list.append(target)
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


# ===== Main Game Loop =====
white_options, black_options = [], []
black_options, white_options = check_options(black_pieces, black_locations, 'black'), check_options(white_pieces,
                                                                                                    white_locations,
                                                                                                    'white')
run = True
selected_piece = None

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
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)
        if selected_piece == 'king': draw_castling(castling_moves)
    if quiz_state != 'INACTIVE': draw_quiz_ui()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: run = False

        if quiz_state != 'INACTIVE':
            if quiz_state == 'CATEGORY_SELECTION' and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, category in enumerate(quiz_info['categories']):
                    btn_rect = pygame.Rect(250, 250 + i * 100, 300, 80)
                    if btn_rect.collidepoint(event.pos):
                        quiz_data = gemini_quiz.generate_quiz(category)
                        quiz_info.update(quiz_data)
                        quiz_info['user_answer'] = ''  # #### 오류 수정: 사용자 답변 기록 초기화 ####
                        quiz_state = 'ANSWERING'
                        pygame.key.start_text_input()
                        pygame.key.set_text_input_rect(pygame.Rect(150, 400, 500, 60))
                        break

            if quiz_state == 'ANSWERING':
                if event.type == pygame.TEXTINPUT:
                    quiz_info['user_answer'] += event.text
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.key.stop_text_input()
                        user_ans_clean = ''.join(filter(str.isalnum, quiz_info['user_answer'].lower()))
                        quiz_info['result'] = (user_ans_clean == quiz_info['answer_clean'])
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
                    selection, valid_moves = 100, []
                    black_options, white_options = check_options(black_pieces, black_locations, 'black'), check_options(
                        white_pieces, white_locations, 'white')


                if click_coords in valid_moves:
                    if click_coords in opp_locs:
                        quiz_state, quiz_info['categories'] = 'CATEGORY_SELECTION', random.sample(QUIZ_CATEGORIES, 3)
                        attack_context.update(
                            {'attacker_color': 'white' if turn_step < 2 else 'black', 'attacker_index': selection,
                             'defender_index': opp_locs.index(click_coords), 'target_coords': click_coords,
                             'original_attacker_coords': original_coords, 'original_turn_step': turn_step})
                        selection, valid_moves = 100, []
                    else:
                        pieces, locs, moved, _, opp_pieces, opp_locs, opp_moved, captured = (white_pieces,
                                                                                             white_locations,
                                                                                             white_moved, white_ep,
                                                                                             black_pieces,
                                                                                             black_locations,
                                                                                             black_moved,
                                                                                             captured_pieces_white) if turn_step < 2 else (
                            black_pieces, black_locations, black_moved, black_ep, white_pieces, white_locations,
                            white_moved, captured_pieces_black)
                        locs[selection] = click_coords;
                        moved[selection] = True
                        ep_target, victim_y_offset = (black_ep, -1) if turn_step < 2 else (white_ep, 1)
                        if click_coords == ep_target:
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
                    king_idx = current_locs.index((4, start_row))
                    rook_start_x = 0 if click_coords[0] < 4 else 7
                    rook_idx = current_locs.index((rook_start_x, start_row))
                    current_locs[king_idx], current_locs[rook_idx] = move[0], move[1]
                    current_moved[king_idx], current_moved[rook_idx] = True, True
                    end_turn()

        if event.type == pygame.KEYDOWN and game_over and event.key == pygame.K_RETURN:
            white_pieces, white_locations, white_moved = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop',
                                                          'knight', 'rook'] + ['pawn'] * 8, [(i, 0) for i in
                                                                                             range(8)] + [(i, 1) for i
                                                                                                          in
                                                                                                          range(8)], [
                                                             False] * 16
            black_pieces, black_locations, black_moved = ['rook', 'knight', 'bishop', 'king', 'queen', 'bishop',
                                                          'knight', 'rook'] + ['pawn'] * 8, [(i, 7) for i in
                                                                                             range(8)] + [(i, 6) for i
                                                                                                          in
                                                                                                          range(8)], [
                                                             False] * 16
            captured_pieces_white, captured_pieces_black, turn_step, selection, valid_moves, winner, game_over = [], [], 0, 100, [], '', False
            white_ep, black_ep, white_options, black_options = (100, 100), (100, 100), [], []
            black_options, white_options = check_options(black_pieces, black_locations, 'black'), check_options(
                white_pieces, white_locations, 'white')

    if quiz_state == 'RESULT' and time.time() - quiz_info['result_time'] > 2.5:
        resolve_attack()
        quiz_state = 'INACTIVE'
    if winner != '':
        game_over = True
        draw_game_over()
    pygame.display.flip()
pygame.quit()