# JOGO FUNCIONAL
# Código feito pelos alunos: Ian Riki Taniguchi, João Alves Gava e João Vitor Del Pupo
import pygame
import sys
import math


def main(screen, clock):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    LINE_COLOR = (150, 150, 150)
    X_COLOR = (230, 70, 70)
    O_COLOR = (70, 70, 230)

    BOARD_ROWS = 3
    BOARD_COLS = 3
    SQUARE_SIZE = HEIGHT // BOARD_ROWS
    OFFSET_X = (WIDTH - (SQUARE_SIZE * BOARD_COLS)) // 2

    try:
        font_large = pygame.font.SysFont("Arial", 60)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)

    def create_board():
        return [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

    def draw_lines():
        for i in range(1, BOARD_COLS):
            pygame.draw.line(
                screen,
                LINE_COLOR,
                (OFFSET_X + i * SQUARE_SIZE, 0),
                (OFFSET_X + i * SQUARE_SIZE, HEIGHT),
                6,
            )
        for i in range(1, BOARD_ROWS):
            pygame.draw.line(
                screen,
                LINE_COLOR,
                (OFFSET_X, i * SQUARE_SIZE),
                (OFFSET_X + BOARD_COLS * SQUARE_SIZE, i * SQUARE_SIZE),
                6,
            )

    def draw_figures(board):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                center_x = OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
                center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2

                if board[row][col] == 1:
                    pygame.draw.line(
                        screen,
                        X_COLOR,
                        (center_x - 60, center_y - 60),
                        (center_x + 60, center_y + 60),
                        15,
                    )
                    pygame.draw.line(
                        screen,
                        X_COLOR,
                        (center_x + 60, center_y - 60),
                        (center_x - 60, center_y + 60),
                        15,
                    )
                elif board[row][col] == 2:
                    pygame.draw.circle(screen, O_COLOR, (center_x, center_y), 60, 15)

    def mark_square(board, row, col, player):
        if board[row][col] == 0:
            board[row][col] = player
            return True
        return False

    def check_win(board, player):
        for col in range(BOARD_COLS):
            if board[0][col] == player and board[1][col] == player and board[2][col] == player:
                return True
        for row in range(BOARD_ROWS):
            if board[row][0] == player and board[row][1] == player and board[row][2] == player:
                return True
        if board[0][0] == player and board[1][1] == player and board[2][2] == player:
            return True
        if board[0][2] == player and board[1][1] == player and board[2][0] == player:
            return True
        return False

    def is_board_full(board):
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if board[row][col] == 0:
                    return False
        return True

    def draw_game_over(message):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        text_surf = font_large.render(message, True, WHITE)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(text_surf, text_rect)

        text_surf_small = font_small.render("Pressione [ESPAÇO] para reiniciar ou [ESC] para sair", True, WHITE)
        text_rect_small = text_surf_small.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        screen.blit(text_surf_small, text_rect_small)

    def game_loop():
        board = create_board()
        player = 1
        game_over = False
        winner_message = ""
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

                    if mouseX > OFFSET_X and mouseX < (WIDTH - OFFSET_X):
                        clicked_col = (mouseX - OFFSET_X) // SQUARE_SIZE
                        clicked_row = mouseY // SQUARE_SIZE

                        if mark_square(board, clicked_row, clicked_col, player):
                            if check_win(board, player):
                                game_over = True
                                winner_message = f"Jogador {player} venceu!"
                            elif is_board_full(board):
                                game_over = True
                                winner_message = "Empate!"
                            else:
                                player = 2 if player == 1 else 1

            screen.fill(BLACK)
            draw_lines()
            draw_figures(board)

            if game_over:
                draw_game_over(winner_message)

            pygame.display.flip()
            clock.tick(60)

    game_loop()
