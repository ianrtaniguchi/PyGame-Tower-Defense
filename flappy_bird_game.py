import pygame
import sys
import random


def main(screen, clock):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BIRD_COLOR = (255, 255, 0)  # Amarelo
    PIPE_COLOR = (0, 200, 0)  # Verde
    BG_COLOR = (135, 206, 235)  # Fundo Azul

    try:
        font_large = pygame.font.SysFont("Arial", 60)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)

    class Bird(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.Surface((40, 30))
            self.image.fill(BIRD_COLOR)
            self.rect = self.image.get_rect(center=(100, HEIGHT // 2))
            self.velocity = 0
            self.gravity = 0.5
            self.lift = -10

        def update(self):
            self.velocity += self.gravity
            self.rect.y += self.velocity

            if self.rect.top < 0:
                self.rect.top = 0
                self.velocity = 0

        def flap(self):
            self.velocity = self.lift

    class Pipe(pygame.sprite.Sprite):
        def __init__(self, x, y, height, is_top):
            super().__init__()
            self.image = pygame.Surface((80, height))
            self.image.fill(PIPE_COLOR)
            self.rect = self.image.get_rect()
            self.speed = 5

            if is_top:
                self.rect.bottomleft = (x, y)
            else:
                self.rect.topleft = (x, y)

        def update(self):
            self.rect.x -= self.speed
            if self.rect.right < 0:
                self.kill()

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def create_pipes(all_sprites, pipes):
        gap_y = random.randint(200, HEIGHT - 200)
        gap_height = 200

        top_pipe_height = gap_y - gap_height // 2
        bottom_pipe_height = HEIGHT - (gap_y + gap_height // 2)

        pipe_top = Pipe(WIDTH, 0, top_pipe_height, True)
        pipe_bottom = Pipe(WIDTH, gap_y + gap_height // 2, bottom_pipe_height, False)

        all_sprites.add(pipe_top)
        all_sprites.add(pipe_bottom)
        pipes.add(pipe_top)
        pipes.add(pipe_bottom)

    def game_loop():
        all_sprites = pygame.sprite.Group()
        pipes = pygame.sprite.Group()

        bird = Bird()
        all_sprites.add(bird)

        score = 0
        pipe_timer = 0
        pipe_delay = 1500

        running = True
        game_over = False
        game_started = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        if not game_started:
                            game_started = True
                            pipe_timer = pygame.time.get_ticks()
                        if not game_over:
                            bird.flap()
                        else:
                            game_loop()
                            return

            if not game_started:
                screen.fill(BG_COLOR)
                draw_text(
                    "Pressione [ESPAÇO] para começar",
                    font_small,
                    BLACK,
                    screen,
                    WIDTH / 2,
                    HEIGHT / 2,
                )
                pygame.display.flip()
                clock.tick(60)
                continue

            if game_over:
                screen.fill(BLACK)
                draw_text(
                    "GAME OVER", font_large, RED, screen, WIDTH / 2, HEIGHT / 2 - 40
                )
                draw_text(
                    f"Pontuação: {score}",
                    font_small,
                    WHITE,
                    screen,
                    WIDTH / 2,
                    HEIGHT / 2 + 20,
                )
                draw_text(
                    "Pressione [ESPAÇO] para reiniciar ou [ESC] para sair",
                    font_small,
                    WHITE,
                    screen,
                    WIDTH / 2,
                    HEIGHT / 2 + 60,
                )
                pygame.display.flip()
                clock.tick(60)
                continue

            all_sprites.update()

            now = pygame.time.get_ticks()
            if now - pipe_timer > pipe_delay:
                create_pipes(all_sprites, pipes)
                pipe_timer = now

            for pipe in pipes:
                if (
                    not pipe.rect.colliderect(bird.rect)
                    and pipe.rect.right < bird.rect.left
                    and pipe.rect.right > bird.rect.left - 6
                ):
                    if not hasattr(pipe, "scored"):
                        score += 0.5
                        pipe.scored = True

            if (
                pygame.sprite.spritecollide(bird, pipes, False)
                or bird.rect.bottom > HEIGHT
            ):
                game_over = True

            screen.fill(BG_COLOR)
            all_sprites.draw(screen)
            draw_text(
                f"Pontuação: {int(score)}", font_large, WHITE, screen, WIDTH // 2, 50
            )

            pygame.display.flip()
            clock.tick(60)

    game_loop()
