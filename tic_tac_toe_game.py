# JOGO FUNCIONAL PRONTO
# Código feito pelos alunos: Ian Riki Taniguchi, João Alves Gava e João Vitor Del Pupo
import pygame
import sys
import math


def main(
    screen,
    clock,
    cheats_enabled,
):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    BG_COLOR = (40, 42, 54)
    LINE_COLOR = (98, 114, 164)
    X_COLOR = (255, 85, 85)
    O_COLOR = (139, 233, 253)
    TEXT_COLOR = (248, 248, 242)
    CARD_BG = (68, 71, 90)

    CHEAT_COLOR = (80, 250, 123)

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
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)

    def create_board():
        return [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

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

                if board[row][col] == 1:  # X
                    start_desc = (center_x - SQUARE_SIZE // 2 + FIGURE_PADDING, center_y - SQUARE_SIZE // 2 + FIGURE_PADDING)
                    end_desc = (center_x + SQUARE_SIZE // 2 - FIGURE_PADDING, center_y + SQUARE_SIZE // 2 - FIGURE_PADDING)
                    pygame.draw.line(screen, X_COLOR, start_desc, end_desc, FIGURE_WIDTH)

                    start_asc = (center_x - SQUARE_SIZE // 2 + FIGURE_PADDING, center_y + SQUARE_SIZE // 2 - FIGURE_PADDING)
                    end_asc = (center_x + SQUARE_SIZE // 2 - FIGURE_PADDING, center_y - SQUARE_SIZE // 2 + FIGURE_PADDING)
                    pygame.draw.line(screen, X_COLOR, start_asc, end_asc, FIGURE_WIDTH)

                elif board[row][col] == 2:  # O
                    radius = SQUARE_SIZE // 2 - FIGURE_PADDING
                    pygame.draw.circle(screen, O_COLOR, (center_x, center_y), radius, FIGURE_WIDTH)

    def mark_square(board, row, col, player):
        # Permite P1 (X) sobrescrever P2 (O) se os cheats estiverem ligados
        if board[row][col] == 0 or (cheats_enabled and player == 1 and board[row][col] == 2):
            board[row][col] = player
            return True
        return False

    def check_win(board, player):
        for col in range(BOARD_COLS):
            if board[0][col] == player and board[1][col] == player and board[2][col] == player:
                draw_winning_line((OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2, OFFSET_Y), (OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2, OFFSET_Y + HEIGHT), player)
                return True
        for row in range(BOARD_ROWS):
            if board[row][0] == player and board[row][1] == player and board[row][2] == player:
                draw_winning_line((OFFSET_X, OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2), (OFFSET_X + WIDTH, OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2), player)
                return True
        if board[0][0] == player and board[1][1] == player and board[2][2] == player:
            draw_winning_line((OFFSET_X, OFFSET_Y), (OFFSET_X + 3 * SQUARE_SIZE, OFFSET_Y + 3 * SQUARE_SIZE), player)
            return True
        if board[0][2] == player and board[1][1] == player and board[2][0] == player:
            draw_winning_line((OFFSET_X + 3 * SQUARE_SIZE, OFFSET_Y), (OFFSET_X, OFFSET_Y + 3 * SQUARE_SIZE), player)
            return True
        return False

    def draw_winning_line(start, end, player):
        color = X_COLOR if player == 1 else O_COLOR
        pass

    def is_board_full(board):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    return False
        return True

    def draw_game_over(message, winner_color=TEXT_COLOR):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        card_width, card_height = 600, 250
        card_rect = pygame.Rect((WIDTH - card_width) // 2, (HEIGHT - card_height) // 2, card_width, card_height)

        shadow_rect = card_rect.copy()
        shadow_rect.move_ip(5, 5)
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=20)

        pygame.draw.rect(screen, CARD_BG, card_rect, border_radius=20)
        pygame.draw.rect(screen, winner_color, card_rect, 4, border_radius=20)

        text_surf = font_large.render(message, True, winner_color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(text_surf, text_rect)

        text_surf_small = font_small.render("Pressione [ESPAÇO] para reiniciar", True, TEXT_COLOR)
        text_rect_small = text_surf_small.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(text_surf_small, text_rect_small)

    def game_loop():
        board = create_board()
        player = 1
        game_over = False
        winner_message = ""
        winner_color = TEXT_COLOR
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE and game_over:
                        board = create_board()
                        player = 1
                        game_over = False
                        winner_message = ""

                if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX = event.pos[0]
                    mouseY = event.pos[1]

                    if mouseX > OFFSET_X and mouseX < (OFFSET_X + BOARD_COLS * SQUARE_SIZE) and mouseY > OFFSET_Y and mouseY < (OFFSET_Y + BOARD_ROWS * SQUARE_SIZE):

                        clicked_col = (mouseX - OFFSET_X) // SQUARE_SIZE
                        clicked_row = (mouseY - OFFSET_Y) // SQUARE_SIZE

                        if mark_square(board, clicked_row, clicked_col, player):
                            if check_win(board, player):
                                game_over = True
                                winner_message = f"Jogador {player} Venceu!"
                                winner_color = X_COLOR if player == 1 else O_COLOR
                            elif is_board_full(board):
                                game_over = True
                                winner_message = "Empate!"
                                winner_color = TEXT_COLOR
                            else:
                                player = 2 if player == 1 else 1

            screen.fill(BG_COLOR)
            draw_lines()
            draw_figures(board)

            # UI Cheats
            if cheats_enabled:
                text_surf = font_small.render("CHEATS ATIVADOS", True, CHEAT_COLOR)
                # Fundo semi-transparente para o texto do cheat ficar legível
                bg_rect = text_surf.get_rect(topleft=(OFFSET_X, 10))
                bg_rect.inflate_ip(10, 10)
                pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=5)
                screen.blit(text_surf, (OFFSET_X, 10))

            if game_over:
                draw_game_over(winner_message, winner_color)

            pygame.display.flip()
            clock.tick(60)

    game_loop()
