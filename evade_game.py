import pygame
import sys
import random


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    PLAYER_COLOR = (0, 150, 255)

    try:
        font_large = pygame.font.SysFont("Arial", 60)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.Surface((40, 40))
            self.image.fill(PLAYER_COLOR)
            self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            self.speed = 8

        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += self.speed

    class Obstacle(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.width = random.randint(20, 100)
            self.image = pygame.Surface((self.width, 20))
            self.image.fill(RED)
            self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), -20))
            self.speed = random.randint(4, 10)

        def update(self):
            self.rect.y += self.speed
            if self.rect.top > HEIGHT:
                self.kill()

    def game_loop():
        player = Player()
        all_sprites = pygame.sprite.Group()
        obstacles = pygame.sprite.Group()
        all_sprites.add(player)

        start_time = pygame.time.get_ticks()
        score = 0
        game_over = False

        spawn_timer = 0
        spawn_delay = 500

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            if game_over:
                screen.fill(BLACK)
                draw_text("GAME OVER", font_large, RED, screen, WIDTH / 2, HEIGHT / 2 - 40)
                draw_text(f"Pontuação: {score}", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 20)
                draw_text("Pressione [ESC] para sair", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 60)

            else:
                all_sprites.update()

                now = pygame.time.get_ticks()
                if now - spawn_timer > spawn_delay:
                    obstacle = Obstacle()
                    all_sprites.add(obstacle)
                    obstacles.add(obstacle)
                    spawn_timer = now

                score = (now - start_time) // 100
                if spawn_delay > 100:
                    spawn_delay = max(100, 500 - (score // 10))

                if not cheats_enabled:
                    if pygame.sprite.spritecollide(player, obstacles, False):
                        game_over = True

                screen.fill(BLACK)
                all_sprites.draw(screen)
                draw_text(f"Pontuação: {score}", font_small, WHITE, screen, 10, 10, center=False)
                if cheats_enabled:
                    draw_text("CHEATS: Imortal", font_small, GREEN, screen, WIDTH - 150, 10)

            pygame.display.flip()
            clock.tick(60)

        return score

    return game_loop()
