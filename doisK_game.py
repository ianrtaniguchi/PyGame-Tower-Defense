# JOGO FUNCIONAL
# Implementação do 2048 para o Hub de Jogos
import pygame
import sys
import random


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BG_COLOR = (187, 173, 160)
    GRID_BG = (205, 193, 180)
    GREEN = (0, 255, 0)

    TILE_COLORS = {
        0: (GRID_BG, BLACK),
        2: ((238, 228, 218), (119, 110, 101)),
        4: ((237, 224, 200), (119, 110, 101)),
        8: ((242, 177, 121), (249, 246, 242)),
        16: ((245, 149, 99), (249, 246, 242)),
        32: ((246, 124, 95), (249, 246, 242)),
        64: ((246, 94, 59), (249, 246, 242)),
        128: ((237, 207, 114), (249, 246, 242)),
        256: ((237, 204, 97), (249, 246, 242)),
        512: ((237, 200, 80), (249, 246, 242)),
        1024: ((237, 197, 63), (249, 246, 242)),
        2048: ((237, 194, 46), (249, 246, 242)),
        "default": ((60, 58, 50), (249, 246, 242)),
    }

    try:
        font_large = pygame.font.SysFont("Arial", 55, bold=True)
        font_medium = pygame.font.SysFont("Arial", 32)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)

    GRID_SIZE = 4
    TILE_SIZE = 100
    GAP_SIZE = 15

    GRID_WIDTH = (TILE_SIZE * GRID_SIZE) + (GAP_SIZE * (GRID_SIZE + 1))
    OFFSET_X = (WIDTH - GRID_WIDTH) // 2
    OFFSET_Y = (HEIGHT - GRID_WIDTH) // 2

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def new_game():
        grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        if cheats_enabled:
            grid[0][0] = 128
            add_new_tile(grid)
        else:
            add_new_tile(grid)
            add_new_tile(grid)

        return grid, 0

    def add_new_tile(grid):
        empty_cells = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == 0:
                    empty_cells.append((r, c))

        if empty_cells:
            r, c = random.choice(empty_cells)
            grid[r][c] = 2 if random.random() < 0.9 else 4

    def draw_board(grid, score):
        screen.fill(BG_COLOR)

        grid_rect = pygame.Rect(OFFSET_X, OFFSET_Y, GRID_WIDTH, GRID_WIDTH)
        pygame.draw.rect(screen, GRID_BG, grid_rect, border_radius=5)

        draw_text(f"Pontuação: {score}", font_medium, WHITE, screen, WIDTH // 2, 50)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = grid[r][c]

                bg_color, text_color = TILE_COLORS.get(val, TILE_COLORS["default"])

                tile_rect = pygame.Rect(OFFSET_X + (c * (TILE_SIZE + GAP_SIZE)) + GAP_SIZE, OFFSET_Y + (r * (TILE_SIZE + GAP_SIZE)) + GAP_SIZE, TILE_SIZE, TILE_SIZE)

                pygame.draw.rect(screen, bg_color, tile_rect, border_radius=3)

                if val != 0:
                    draw_text(str(val), font_large, text_color, screen, tile_rect.centerx, tile_rect.centery)

    def move(grid, direction):
        moved = False
        score_gain = 0
        new_grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        if direction == "up":
            for c in range(GRID_SIZE):
                col = [grid[r][c] for r in range(GRID_SIZE)]
                new_col, gain = merge(col)
                score_gain += gain
                for r in range(GRID_SIZE):
                    new_grid[r][c] = new_col[r]
                if col != new_col:
                    moved = True

        elif direction == "down":
            for c in range(GRID_SIZE):
                col = [grid[r][c] for r in range(GRID_SIZE - 1, -1, -1)]
                new_col, gain = merge(col)
                score_gain += gain
                for r in range(GRID_SIZE):
                    new_grid[GRID_SIZE - 1 - r][c] = new_col[r]
                if col != [grid[r][c] for r in range(GRID_SIZE - 1, -1, -1)]:
                    moved = True

        elif direction == "left":
            for r in range(GRID_SIZE):
                row = grid[r]
                new_row, gain = merge(row)
                score_gain += gain
                new_grid[r] = new_row
                if row != new_row:
                    moved = True

        elif direction == "right":
            for r in range(GRID_SIZE):
                row = grid[r][::-1]
                new_row, gain = merge(row)
                score_gain += gain
                new_grid[r] = new_row[::-1]
                if row != grid[r][::-1]:
                    moved = True

        return new_grid, score_gain, moved

    def merge(line):
        new_line = [i for i in line if i != 0]

        gain = 0
        i = 0
        while i < len(new_line) - 1:
            if new_line[i] == new_line[i + 1]:
                new_line[i] *= 2
                gain += new_line[i]
                new_line.pop(i + 1)
            i += 1

        while len(new_line) < GRID_SIZE:
            new_line.append(0)

        return new_line, gain

    def check_game_over(grid):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == 0:
                    return False

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE - 1):
                if grid[r][c] == grid[r][c + 1]:
                    return False

        for c in range(GRID_SIZE):
            for r in range(GRID_SIZE - 1):
                if grid[r][c] == grid[r + 1][c]:
                    return False

        return True

    def game_loop():
        grid, score = new_game()
        running = True
        game_over = False

        while running:

            draw_board(grid, score)

            if game_over:
                draw_text("GAME OVER", font_large, (255, 0, 0), screen, WIDTH // 2, HEIGHT // 2 - 40)
                draw_text("Pressione [ESC] para sair", font_small, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 20)

            pygame.display.flip()

            moved_this_turn = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if not game_over:
                        if event.key == pygame.K_UP:
                            grid, gain, moved_this_turn = move(grid, "up")
                        elif event.key == pygame.K_DOWN:
                            grid, gain, moved_this_turn = move(grid, "down")
                        elif event.key == pygame.K_LEFT:
                            grid, gain, moved_this_turn = move(grid, "left")
                        elif event.key == pygame.K_RIGHT:
                            grid, gain, moved_this_turn = move(grid, "right")

                        if moved_this_turn:
                            score += gain
                            add_new_tile(grid)
                            if check_game_over(grid):
                                game_over = True

            clock.tick(60)

        return score

    score = game_loop()
    return score
