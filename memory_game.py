# JOGO FUNCIONAL PRONTO
# Implementação do Jogo da Memória para o Hub de Jogos
import pygame
import sys
import random
import math
import os


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    # Cores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (100, 100, 100)
    BLUE = (0, 0, 200)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    try:
        font_large = pygame.font.SysFont("Arial", 60)
        font_medium = pygame.font.SysFont("Arial", 32)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)

    GRID_ROWS = 4
    GRID_COLS = 5
    CARD_SIZE = 150
    CARD_GAP = 10

    GRID_WIDTH = (CARD_SIZE + CARD_GAP) * GRID_COLS
    GRID_HEIGHT = (CARD_SIZE + CARD_GAP) * GRID_ROWS
    OFFSET_X = (WIDTH - GRID_WIDTH) // 2 + CARD_GAP // 2
    OFFSET_Y = (HEIGHT - GRID_HEIGHT) // 2 + CARD_GAP // 2

    TOTAL_PAIRS = (GRID_ROWS * GRID_COLS) // 2

    base_img_path = os.path.join("assets", "images", "memoria")
    loaded_images = {}
    for i in range(1, TOTAL_PAIRS + 1):
        image_found = False
        for ext in [".png", ".jpg", ".jpeg"]:
            image_filename = f"memoria_{i}{ext}"
            full_path = os.path.join(base_img_path, image_filename)

            if os.path.exists(full_path):
                try:
                    img = pygame.image.load(full_path)  # Carrega do caminho correto
                    img = pygame.transform.scale(img, (CARD_SIZE, CARD_SIZE))
                    loaded_images[i] = img
                    image_found = True
                    break
                except Exception as e:
                    print(f"Erro ao carregar {full_path}: {e}")

        if not image_found:
            loaded_images[i] = None
            print(f"AVISO: Foto 'memoria_{i}' não encontrada em {base_img_path}. Usando número.")

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def create_board():
        numbers = list(range(1, TOTAL_PAIRS + 1)) * 2
        random.shuffle(numbers)

        board = []
        for r in range(GRID_ROWS):
            row = []
            for c in range(GRID_COLS):
                card_val = numbers.pop()
                card = {"value": card_val, "state": "hidden", "rect": pygame.Rect(OFFSET_X + c * (CARD_SIZE + CARD_GAP), OFFSET_Y + r * (CARD_SIZE + CARD_GAP), CARD_SIZE, CARD_SIZE)}  # hidden, revealed, matched
                row.append(card)
            board.append(row)
        return board

    def get_clicked_card(mouse_pos, board):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if board[r][c]["rect"].collidepoint(mouse_pos):
                    return (r, c)
        return None

    def draw_card_content(surface, card):
        rect = card["rect"]
        photo = loaded_images.get(card["value"])

        if photo:
            surface.blit(photo, rect.topleft)
            pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
        else:
            pygame.draw.rect(surface, WHITE, rect, border_radius=8)
            draw_text(str(card["value"]), font_large, BLACK, surface, rect.centerx, rect.centery)

    def draw_board(board):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                card = board[r][c]
                rect = card["rect"]

                if card["state"] == "hidden":
                    pygame.draw.rect(screen, BLUE, rect, border_radius=8)
                    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)

                elif card["state"] == "revealed":
                    draw_card_content(screen, card)

                elif card["state"] == "matched":
                    draw_card_content(screen, card)
                    s = pygame.Surface((CARD_SIZE, CARD_SIZE))
                    s.set_alpha(100)
                    s.fill(GREEN)
                    screen.blit(s, rect.topleft)
                    pygame.draw.rect(screen, GREEN, rect, 3, border_radius=8)

    def game_loop():
        board = create_board()
        revealed_cards = []
        matches_found = 0
        game_over = False

        preview_duration = 8000  # 8 segundos em milissegundos
        preview_start = pygame.time.get_ticks()

        in_preview = True
        while in_preview:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - preview_start

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 0

            if elapsed >= preview_duration:
                in_preview = False

            screen.fill(BLACK)

            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    draw_card_content(screen, board[r][c])

            time_left = math.ceil((preview_duration - elapsed) / 1000)
            draw_text(f"MEMORIZE! Início em: {time_left}", font_medium, GREEN, screen, WIDTH // 2, 30)

            pygame.display.flip()
            clock.tick(60)
        start_time = pygame.time.get_ticks()

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if cheats_enabled and event.key == pygame.K_c:
                        screen.fill(BLACK)
                        for r in range(GRID_ROWS):
                            for c in range(GRID_COLS):
                                draw_card_content(screen, board[r][c])
                        pygame.display.flip()
                        pygame.time.wait(1000)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
                    if len(revealed_cards) < 2:
                        pos = get_clicked_card(event.pos, board)
                        if pos:
                            r, c = pos
                            if board[r][c]["state"] == "hidden":
                                board[r][c]["state"] = "revealed"
                                revealed_cards.append((r, c))

            if len(revealed_cards) == 2:
                screen.fill(BLACK)
                draw_board(board)
                time_elapsed = (pygame.time.get_ticks() - start_time) // 1000
                draw_text(f"Tempo: {time_elapsed}s", font_medium, WHITE, screen, WIDTH - 100, 30)
                pygame.display.flip()

                pygame.time.wait(800)

                r1, c1 = revealed_cards[0]
                r2, c2 = revealed_cards[1]

                card1 = board[r1][c1]
                card2 = board[r2][c2]

                if card1["value"] == card2["value"]:
                    card1["state"] = "matched"
                    card2["state"] = "matched"
                    matches_found += 1
                else:
                    card1["state"] = "hidden"
                    card2["state"] = "hidden"

                revealed_cards = []
            if matches_found == TOTAL_PAIRS and not game_over:
                game_over = True
                end_time = pygame.time.get_ticks()
                time_taken_ms = end_time - start_time
                score = max(0, 100000 - (time_taken_ms // 10))

            screen.fill(BLACK)
            draw_board(board)
            if not game_over:
                time_elapsed = (pygame.time.get_ticks() - start_time) // 1000
                draw_text(f"Tempo: {time_elapsed}s", font_medium, WHITE, screen, WIDTH - 100, 30)

            if game_over:
                panel_rect = pygame.Rect(0, 0, 400, 300)
                panel_rect.center = (WIDTH // 2, HEIGHT // 2)
                pygame.draw.rect(screen, (50, 50, 50), panel_rect, border_radius=20)
                pygame.draw.rect(screen, WHITE, panel_rect, 2, border_radius=20)

                draw_text("PARABÉNS!", font_large, GREEN, screen, WIDTH // 2, HEIGHT // 2 - 50)
                draw_text(f"Pontuação: {score}", font_medium, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 10)
                draw_text("Pressione [ESC] para sair", font_small, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 60)

            pygame.display.flip()
            clock.tick(60)

        if game_over:
            return score
        return 0

    score = game_loop()
    return score
