# JOGO FUNCIONAL PRONTO
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

    def get_tile_rect(r, c):
        x = OFFSET_X + (c * (TILE_SIZE + GAP_SIZE)) + GAP_SIZE
        y = OFFSET_Y + (r * (TILE_SIZE + GAP_SIZE)) + GAP_SIZE
        return pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw_single_tile(val, rect):
        bg_color, text_color = TILE_COLORS.get(val, TILE_COLORS["default"])
        pygame.draw.rect(screen, bg_color, rect, border_radius=5)
        if val != 0:
            draw_text(str(val), font_large, text_color, screen, rect.centerx, rect.centery)

    def draw_bg_and_score(score):
        screen.fill(BG_COLOR)
        grid_rect = pygame.Rect(OFFSET_X, OFFSET_Y, GRID_WIDTH, GRID_WIDTH)
        pygame.draw.rect(screen, GRID_BG, grid_rect, border_radius=5)
        draw_text(f"Pontuação: {score}", font_medium, WHITE, screen, WIDTH // 2, 50)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = get_tile_rect(r, c)
                pygame.draw.rect(screen, TILE_COLORS[0][0], rect, border_radius=5)

    def draw_board(grid, score):
        draw_bg_and_score(score)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                val = grid[r][c]
                if val != 0:
                    draw_single_tile(val, get_tile_rect(r, c))

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

    def animate_move(animations, score):
        TOTAL_FRAMES = 5

        for frame in range(1, TOTAL_FRAMES + 1):
            progress = frame / TOTAL_FRAMES

            draw_bg_and_score(score)

            for anim in animations:
                val = anim["val"]
                start_rect = get_tile_rect(*anim["from"])
                end_rect = get_tile_rect(*anim["to"])

                # Interpolação linear simples
                curr_x = start_rect.x + (end_rect.x - start_rect.x) * progress
                curr_y = start_rect.y + (end_rect.y - start_rect.y) * progress

                curr_rect = pygame.Rect(curr_x, curr_y, TILE_SIZE, TILE_SIZE)
                draw_single_tile(val, curr_rect)

            pygame.display.flip()
            clock.tick(60)

    def merge_with_indices(line):
        # Recebe uma lista de tuplas (valor, indice_original)

        non_zeros = [x for x in line if x[0] != 0]
        new_line = []
        moves = []  # Lista de dicts de movimento: {'val', 'from', 'to'}
        gain = 0

        i = 0
        while i < len(non_zeros):
            val, original_idx = non_zeros[i]

            if i < len(non_zeros) - 1 and non_zeros[i + 1][0] == val:
                next_val, next_original_idx = non_zeros[i + 1]
                merged_val = val * 2
                gain += merged_val

                target_idx = len(new_line)
                new_line.append(merged_val)

                moves.append({"val": val, "from": original_idx, "to": target_idx})  # movimento peça 1
                moves.append({"val": next_val, "from": next_original_idx, "to": target_idx})
                i += 2
            else:
                target_idx = len(new_line)
                new_line.append(val)
                moves.append({"val": val, "from": original_idx, "to": target_idx})
                i += 1

        while len(new_line) < GRID_SIZE:
            new_line.append(0)

        return new_line, moves, gain

    def calculate_move(grid, direction):
        new_grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        score_gain = 0
        animations = []
        moved = False

        if direction == "up":
            for c in range(GRID_SIZE):
                line = [(grid[r][c], r) for r in range(GRID_SIZE)]
                merged_line, moves, gain = merge_with_indices(line)
                score_gain += gain

                for r in range(GRID_SIZE):
                    new_grid[r][c] = merged_line[r]

                for m in moves:
                    if m["from"] != m["to"]:
                        moved = True
                    animations.append({"val": m["val"], "from": (m["from"], c), "to": (m["to"], c)})  # (row, col)

        elif direction == "down":
            for c in range(GRID_SIZE):
                line = [(grid[r][c], r) for r in range(GRID_SIZE - 1, -1, -1)]
                merged_line, moves, gain = merge_with_indices(line)
                score_gain += gain

                for r in range(GRID_SIZE):
                    new_grid[GRID_SIZE - 1 - r][c] = merged_line[r]

                for m in moves:
                    if m["from"] != (3 - m["to"]):
                        moved = True  # Comparação ajustada para reverso
                    animations.append({"val": m["val"], "from": (m["from"], c), "to": (3 - m["to"], c)})

        elif direction == "left":
            for r in range(GRID_SIZE):
                line = [(grid[r][c], c) for c in range(GRID_SIZE)]
                merged_line, moves, gain = merge_with_indices(line)
                score_gain += gain

                new_grid[r] = merged_line

                for m in moves:
                    if m["from"] != m["to"]:
                        moved = True
                    animations.append({"val": m["val"], "from": (r, m["from"]), "to": (r, m["to"])})

        elif direction == "right":
            for r in range(GRID_SIZE):
                line = [(grid[r][c], c) for c in range(GRID_SIZE - 1, -1, -1)]
                merged_line, moves, gain = merge_with_indices(line)
                score_gain += gain

                new_grid[r] = merged_line[::-1]  # Inverte de volta para salvar

                for m in moves:
                    # m['to'] 0 é a coluna da direita (3)
                    start_c = m["from"]
                    end_c = 3 - m["to"]
                    if start_c != end_c:
                        moved = True
                    animations.append({"val": m["val"], "from": (r, start_c), "to": (r, end_c)})

        return new_grid, score_gain, moved, animations

    def check_game_over(grid):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == 0:
                    return False
                if c < GRID_SIZE - 1 and grid[r][c] == grid[r][c + 1]:
                    return False
                if r < GRID_SIZE - 1 and grid[r][c] == grid[r + 1][c]:
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

            direction = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if not game_over and not direction:
                        if event.key == pygame.K_UP:
                            direction = "up"
                        elif event.key == pygame.K_DOWN:
                            direction = "down"
                        elif event.key == pygame.K_LEFT:
                            direction = "left"
                        elif event.key == pygame.K_RIGHT:
                            direction = "right"

            if direction:
                new_grid, gain, moved, animations = calculate_move(grid, direction)

                if moved:
                    animate_move(animations, score)
                    grid = new_grid
                    score += gain
                    add_new_tile(grid)
                    if check_game_over(grid):
                        game_over = True

            clock.tick(60)

        return score

    score = game_loop()
    return score
