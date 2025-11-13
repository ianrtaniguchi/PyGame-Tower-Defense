# JOGO FUNCIONAL
# Código feito pelos alunos: Ian Riki Taniguchi, João Alves Gava e João Vitor Del Pupo
import pygame
import random
import sys


def main(screen, clock, cheats_enabled):
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    BLOCK_SIZE = 20
    GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
    GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    try:
        font_large = pygame.font.SysFont("Arial", 40)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 54)
        font_small = pygame.font.Font(None, 32)

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def game_loop():
        snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        snake_dir = (1, 0)
        food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        score = 0
        game_over = False
        running = True

        game_speed = 15 if cheats_enabled else 10

        while running:
            if game_over:
                screen.fill(BLACK)
                draw_text("GAME OVER", font_large, RED, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50)
                draw_text(f"Pontuação: {score}", font_small, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10)
                draw_text("Pressione [ESPAÇO] para reiniciar ou [ESC] para sair", font_small, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            game_loop()
                            return
                        if event.key == pygame.K_ESCAPE:
                            running = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP and snake_dir != (0, 1):
                            snake_dir = (0, -1)
                        elif event.key == pygame.K_DOWN and snake_dir != (0, -1):
                            snake_dir = (0, 1)
                        elif event.key == pygame.K_LEFT and snake_dir != (1, 0):
                            snake_dir = (-1, 0)
                        elif event.key == pygame.K_RIGHT and snake_dir != (-1, 0):
                            snake_dir = (1, 0)
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                head_x, head_y = snake[0]
                new_head = (head_x + snake_dir[0], head_y + snake_dir[1])

                if not cheats_enabled and (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or new_head in snake):
                    game_over = True
                    continue

                if cheats_enabled:
                    if new_head[0] < 0:
                        new_head = (GRID_WIDTH - 1, new_head[1])
                    if new_head[0] >= GRID_WIDTH:
                        new_head = (0, new_head[1])
                    if new_head[1] < 0:
                        new_head = (new_head[0], GRID_HEIGHT - 1)
                    if new_head[1] >= GRID_HEIGHT:
                        new_head = (new_head[0], 0)

                    if new_head in snake:
                        snake = snake[: snake.index(new_head)]

                snake.insert(0, new_head)

                if new_head == food:
                    score += 1
                    food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                else:
                    snake.pop()

                screen.fill(BLACK)

                for seg in snake:
                    pygame.draw.rect(screen, GREEN, (seg[0] * BLOCK_SIZE, seg[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, RED, (food[0] * BLOCK_SIZE, food[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

                draw_text(f"Pontuação: {score}", font_small, WHITE, screen, 10, 10, center=False)

                if cheats_enabled:
                    draw_text("CHEATS ATIVADOS", font_small, GREEN, screen, SCREEN_WIDTH - 100, 10, center=False)

                pygame.display.flip()
                clock.tick(game_speed)  # Usa a velocidade do cheat

    game_loop()
