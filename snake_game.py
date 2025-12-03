# JOGO FUNCIONAL PRONTO
import pygame
import random
import sys


def main(screen, clock, cheats_enabled):
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    BLOCK_SIZE = 20
    GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
    GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

    BG_COLOR_1 = (170, 215, 81)
    BG_COLOR_2 = (162, 209, 73)
    SNAKE_COLOR = (70, 115, 232)
    SNAKE_HEAD_COLOR = (50, 90, 200)
    APPLE_COLOR = (231, 71, 29)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    try:
        font_large = pygame.font.SysFont("Arial", 50, bold=True)
        font_small = pygame.font.SysFont("Arial", 24, bold=True)
    except:
        font_large = pygame.font.Font(None, 60)
        font_small = pygame.font.Font(None, 32)

    def draw_text(text, font, color, surface, x, y, center=True):
        shadow = font.render(text, True, (0, 0, 0))
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        offset = 2
        if center:
            text_rect.center = (x, y)
            surface.blit(shadow, (text_rect.x + offset, text_rect.y + offset))
            surface.blit(text_obj, text_rect)
        else:
            text_rect.topleft = (x, y)
            surface.blit(shadow, (x + offset, y + offset))
            surface.blit(text_obj, (x, y))

    def draw_grid():
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                color = BG_COLOR_1 if (row + col) % 2 == 0 else BG_COLOR_2
                rect = pygame.Rect(col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
                pygame.draw.rect(screen, color, rect)

    def draw_apple(x, y):
        center_x = x * BLOCK_SIZE + BLOCK_SIZE // 2
        center_y = y * BLOCK_SIZE + BLOCK_SIZE // 2
        radius = BLOCK_SIZE // 2 - 2

        pygame.draw.circle(screen, APPLE_COLOR, (center_x, center_y), radius)
        pygame.draw.circle(screen, (255, 150, 150), (center_x - 3, center_y - 3), 3)
        pygame.draw.rect(screen, (100, 50, 0), (center_x - 1, center_y - radius - 2, 2, 4))

    def draw_snake(snake_body, direction):
        for i, pos in enumerate(snake_body):
            x = pos[0] * BLOCK_SIZE
            y = pos[1] * BLOCK_SIZE
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)

            if i == 0:  # Cabeça
                pygame.draw.rect(screen, SNAKE_HEAD_COLOR, rect, border_radius=5)

                # Olhos
                eye_radius = 2
                # Posição dos olhos baseada na direção
                eye_offset_x = 5
                eye_offset_y = 5

                pygame.draw.circle(screen, WHITE, (x + eye_offset_x, y + eye_offset_y), 4)
                pygame.draw.circle(screen, BLACK, (x + eye_offset_x, y + eye_offset_y), eye_radius)

                if direction[0] != 0:
                    pygame.draw.circle(screen, WHITE, (x + eye_offset_x, y + BLOCK_SIZE - eye_offset_y), 4)
                    pygame.draw.circle(screen, BLACK, (x + eye_offset_x, y + BLOCK_SIZE - eye_offset_y), eye_radius)
                else:
                    pygame.draw.circle(screen, WHITE, (x + BLOCK_SIZE - eye_offset_x, y + eye_offset_y), 4)
                    pygame.draw.circle(screen, BLACK, (x + BLOCK_SIZE - eye_offset_x, y + eye_offset_y), eye_radius)

            else:
                inner_rect = rect.inflate(-2, -2)
                pygame.draw.rect(screen, SNAKE_COLOR, inner_rect, border_radius=3)

    def game_loop():
        snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        snake_dir = (1, 0)
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        score = 0
        game_over = False
        running = True

        game_speed = 15 if cheats_enabled else 10

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if not game_over:
                        if event.key == pygame.K_UP and snake_dir != (0, 1):
                            snake_dir = (0, -1)
                        elif event.key == pygame.K_DOWN and snake_dir != (0, -1):
                            snake_dir = (0, 1)
                        elif event.key == pygame.K_LEFT and snake_dir != (1, 0):
                            snake_dir = (-1, 0)
                        elif event.key == pygame.K_RIGHT and snake_dir != (-1, 0):
                            snake_dir = (1, 0)
                    else:
                        if event.key == pygame.K_SPACE:
                            return game_loop()

            if not game_over:
                head_x, head_y = snake[0]
                new_head = (head_x + snake_dir[0], head_y + snake_dir[1])

                if not cheats_enabled:
                    if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or new_head in snake:
                        game_over = True

                if cheats_enabled:
                    new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
                    if new_head in snake:
                        snake = snake[: snake.index(new_head)]

                if not game_over:
                    snake.insert(0, new_head)

                    if new_head == food:
                        score += 1
                        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                        while food in snake:
                            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                    else:
                        snake.pop()

            draw_grid()

            draw_apple(food[0], food[1])
            draw_snake(snake, snake_dir)

            score_bg = pygame.Surface((160, 40), pygame.SRCALPHA)
            score_bg.fill((0, 0, 0, 100))
            screen.blit(score_bg, (10, 10))
            draw_text(f"Maçãs: {score}", font_small, WHITE, screen, 90, 30, center=True)

            if cheats_enabled:
                draw_text("GOD MODE", font_small, (255, 215, 0), screen, SCREEN_WIDTH - 80, 30, center=True)

            if game_over:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))

                draw_text("FIM DE JOGO", font_large, (255, 50, 50), screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40)
                draw_text(f"Score Final: {score}", font_small, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20)
                draw_text("[ESPAÇO] Reiniciar   [ESC] Sair", font_small, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60)

            pygame.display.flip()
            clock.tick(game_speed)

    game_loop()
