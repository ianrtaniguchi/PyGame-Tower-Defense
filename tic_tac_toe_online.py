# JOGO DA VELHA ONLINE PRONTO
import pygame
import sys


def main(screen, clock, cheats_enabled, db, game_id, player_role, user_token):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    BG_COLOR = (40, 42, 54)
    LINE_COLOR = (98, 114, 164)
    X_COLOR = (255, 85, 85)
    O_COLOR = (139, 233, 253)
    TEXT_COLOR = (248, 248, 242)
    CARD_BG = (68, 71, 90)

    BOARD_ROWS = 3
    BOARD_COLS = 3

    SQUARE_SIZE = min(WIDTH, HEIGHT) // BOARD_ROWS - 20
    OFFSET_X = (WIDTH - (SQUARE_SIZE * BOARD_COLS)) // 2
    OFFSET_Y = (HEIGHT - (SQUARE_SIZE * BOARD_ROWS)) // 2

    LINE_WIDTH = 10
    FIGURE_WIDTH = 15
    FIGURE_PADDING = SQUARE_SIZE // 4

    try:
        font_large = pygame.font.SysFont("Arial", 60, bold=True)
        font_small = pygame.font.SysFont("Arial", 24)
        font_status = pygame.font.SysFont("Arial", 30, bold=True)
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)
        font_status = pygame.font.Font(None, 40)

    def draw_lines():
        for i in range(1, BOARD_COLS):
            start = (OFFSET_X + i * SQUARE_SIZE, OFFSET_Y)
            end = (OFFSET_X + i * SQUARE_SIZE, OFFSET_Y + BOARD_ROWS * SQUARE_SIZE)
            pygame.draw.line(screen, LINE_COLOR, start, end, LINE_WIDTH)

        for i in range(1, BOARD_ROWS):
            start = (OFFSET_X, OFFSET_Y + i * SQUARE_SIZE)
            end = (OFFSET_X + BOARD_COLS * SQUARE_SIZE, OFFSET_Y + i * SQUARE_SIZE)
            pygame.draw.line(screen, LINE_COLOR, start, end, LINE_WIDTH)

    def draw_figures(board):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2

                if board[row][col] == 1:
                    start_desc = (center_x - SQUARE_SIZE // 2 + FIGURE_PADDING, center_y - SQUARE_SIZE // 2 + FIGURE_PADDING)
                    end_desc = (center_x + SQUARE_SIZE // 2 - FIGURE_PADDING, center_y + SQUARE_SIZE // 2 - FIGURE_PADDING)
                    pygame.draw.line(screen, X_COLOR, start_desc, end_desc, FIGURE_WIDTH)

                    start_asc = (center_x - SQUARE_SIZE // 2 + FIGURE_PADDING, center_y + SQUARE_SIZE // 2 - FIGURE_PADDING)
                    end_asc = (center_x + SQUARE_SIZE // 2 - FIGURE_PADDING, center_y - SQUARE_SIZE // 2 + FIGURE_PADDING)
                    pygame.draw.line(screen, X_COLOR, start_asc, end_asc, FIGURE_WIDTH)

                elif board[row][col] == 2:
                    radius = SQUARE_SIZE // 2 - FIGURE_PADDING
                    pygame.draw.circle(screen, O_COLOR, (center_x, center_y), radius, FIGURE_WIDTH)

    def draw_status(msg, color):
        text_surf = font_status.render(msg, True, color)
        rect = text_surf.get_rect(center=(WIDTH // 2, 40))
        pygame.draw.rect(screen, (0, 0, 0, 150), rect.inflate(20, 10), border_radius=10)
        screen.blit(text_surf, rect)

    def draw_game_over(message, winner_color=TEXT_COLOR):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        card_width, card_height = 600, 250
        card_rect = pygame.Rect((WIDTH - card_width) // 2, (HEIGHT - card_height) // 2, card_width, card_height)

        pygame.draw.rect(screen, CARD_BG, card_rect, border_radius=20)
        pygame.draw.rect(screen, winner_color, card_rect, 4, border_radius=20)

        text_surf = font_large.render(message, True, winner_color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(text_surf, text_rect)

        text_surf_small = font_small.render("Pressione [ESC] para sair", True, TEXT_COLOR)
        text_rect_small = text_surf_small.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(text_surf_small, text_rect_small)

    def check_server_updates():
        try:
            data = db.child("tictactoe").child(game_id).get(token=user_token).val()
            return data
        except:
            return None

    def update_server(board, next_turn, winner):
        data = {"board": board, "turn": next_turn, "winner": winner}
        db.child("tictactoe").child(game_id).update(data, token=user_token)

    def check_win_local(board, player):
        for i in range(3):
            if all([board[i][j] == player for j in range(3)]):
                return True
            if all([board[j][i] == player for j in range(3)]):
                return True
        if board[0][0] == board[1][1] == board[2][2] == player:
            return True
        if board[0][2] == board[1][1] == board[2][0] == player:
            return True
        return False

    def is_board_full(board):
        for r in board:
            if 0 in r:
                return False
        return True

    board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    running = True
    game_over = False
    winner_message = ""
    winner_color = TEXT_COLOR

    current_turn_server = 1
    last_update_time = 0
    update_interval = 500

    while running:
        current_time = pygame.time.get_ticks()

        if current_time - last_update_time > update_interval:
            server_data = check_server_updates()
            if server_data:
                if "board" in server_data:
                    s_board = server_data["board"]
                    if isinstance(s_board, list) and len(s_board) == 3:
                        board = s_board

                current_turn_server = server_data.get("turn", 1)
                server_winner = server_data.get("winner", 0)

                if server_winner != 0:
                    game_over = True
                    if server_winner == player_role:
                        winner_message = "VOCÊ VENCEU!"
                        winner_color = X_COLOR if player_role == 1 else O_COLOR
                    elif server_winner == 3:
                        winner_message = "EMPATE!"
                        winner_color = TEXT_COLOR
                    else:
                        winner_message = "VOCÊ PERDEU!"
                        winner_color = (100, 100, 100)

            last_update_time = current_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if current_turn_server == player_role:
                    mouseX, mouseY = event.pos

                    if (OFFSET_X < mouseX < OFFSET_X + BOARD_COLS * SQUARE_SIZE) and (OFFSET_Y < mouseY < OFFSET_Y + BOARD_ROWS * SQUARE_SIZE):

                        col = (mouseX - OFFSET_X) // SQUARE_SIZE
                        row = (mouseY - OFFSET_Y) // SQUARE_SIZE

                        if board[row][col] == 0:
                            board[row][col] = player_role

                            winner = 0
                            if check_win_local(board, player_role):
                                winner = player_role
                            elif is_board_full(board):
                                winner = 3

                            next_turn = 2 if player_role == 1 else 1

                            update_server(board, next_turn, winner)

                            current_turn_server = next_turn

        screen.fill(BG_COLOR)
        draw_lines()
        draw_figures(board)

        if not game_over:
            if current_turn_server == player_role:
                draw_status("SUA VEZ!", (80, 255, 80))
            else:
                draw_status("AGUARDANDO OPONENTE...", (255, 200, 80))
        else:
            draw_game_over(winner_message, winner_color)

        pygame.display.flip()
        clock.tick(60)
