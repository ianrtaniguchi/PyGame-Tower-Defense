# JOGO FUNCIONAL PRONTO
import pygame
import sys
import random


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    BG_COLOR = (10, 10, 20)
    PLAYER_COLOR = (0, 255, 255)
    PLAYER_CORE = (200, 255, 255)
    OBSTACLE_COLOR = (255, 0, 80)
    OBSTACLE_GLOW = (100, 0, 30)
    STAR_COLOR = (200, 200, 255)
    TEXT_COLOR = (255, 255, 255)

    try:
        font_large = pygame.font.SysFont("Arial", 60, bold=True)
        font_small = pygame.font.SysFont("Arial", 24)
        font_score = pygame.font.SysFont("Arial", 30, bold=True)
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)
        font_score = pygame.font.Font(None, 36)

    def draw_text(text, font, color, surface, x, y, center=True):
        shadow_obj = font.render(text, True, (0, 0, 0))
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()

        offset = 2
        if center:
            text_rect.center = (x, y)
            surface.blit(shadow_obj, (text_rect.x + offset, text_rect.y + offset))
            surface.blit(text_obj, text_rect)
        else:
            text_rect.topleft = (x, y)
            surface.blit(shadow_obj, (x + offset, y + offset))
            surface.blit(text_obj, (x, y))

    class Particle:
        def __init__(self, x, y):
            self.x = x + random.randint(-5, 5)
            self.y = y + random.randint(10, 20)
            self.size = random.randint(2, 5)
            self.life = 20
            self.color = (0, random.randint(100, 255), 255)

        def update(self):
            self.y += 2
            self.life -= 1
            self.size -= 0.1

        def draw(self, surface):
            if self.life > 0 and self.size > 0:
                s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, 150), (self.size, self.size), self.size)
                surface.blit(s, (self.x - self.size, self.y - self.size))

    class Star:
        def __init__(self):
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)
            self.speed = random.randint(1, 3)
            self.size = random.randint(1, 2)
            self.color = (random.randint(150, 255), random.randint(150, 255), 255)

        def update(self):
            self.y += self.speed * 2
            if self.y > HEIGHT:
                self.y = 0
                self.x = random.randint(0, WIDTH)

        def draw(self, surface):
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.rect = pygame.Rect(0, 0, 30, 30)
            self.rect.center = (WIDTH // 2, HEIGHT - 80)
            self.speed = 8
            self.particles = []

        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += self.speed

            self.particles.append(Particle(self.rect.centerx, self.rect.bottom))
            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)

        def draw(self, surface):
            for p in self.particles:
                p.draw(surface)

            cx, cy = self.rect.centerx, self.rect.centery
            points = [(cx, cy - 20), (cx - 15, cy + 15), (cx, cy + 5), (cx + 15, cy + 15)]  # Bico  # Asa Esquerda  # Centro baixo (cavidade)  # Asa Direita
            pygame.draw.polygon(surface, PLAYER_COLOR, points)
            pygame.draw.polygon(surface, PLAYER_CORE, points, 2)  # Contorno interno

    class Obstacle(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.width = random.randint(40, 120)
            self.height = 25
            self.rect = pygame.Rect(random.randint(0, WIDTH - self.width), -30, self.width, self.height)
            self.speed = random.randint(5, 12)

        def update(self):
            self.rect.y += self.speed
            if self.rect.top > HEIGHT:
                self.kill()

        def draw(self, surface):
            shadow_rect = self.rect.inflate(6, 6)
            s = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(s, (*OBSTACLE_COLOR, 100), s.get_rect(), border_radius=5)
            surface.blit(s, shadow_rect.topleft)
            pygame.draw.rect(surface, OBSTACLE_GLOW, self.rect, border_radius=4)
            pygame.draw.rect(surface, OBSTACLE_COLOR, self.rect, 2, border_radius=4)  # Borda
            pygame.draw.line(surface, OBSTACLE_COLOR, (self.rect.left + 5, self.rect.centery), (self.rect.right - 5, self.rect.centery), 1)

    def game_loop():
        player = Player()
        obstacles = []
        stars = [Star() for _ in range(50)]
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

            if not game_over:
                player.update()

                now = pygame.time.get_ticks()
                if now - spawn_timer > spawn_delay:
                    obstacles.append(Obstacle())
                    spawn_timer = now

                score = (now - start_time) // 100
                if spawn_delay > 100:
                    spawn_delay = max(150, 500 - (score // 5))

                player_rect_col = player.rect.inflate(-10, -10)

                for obs in obstacles[:]:
                    obs.update()
                    if obs.rect.top > HEIGHT:
                        obstacles.remove(obs)
                    elif not cheats_enabled and player_rect_col.colliderect(obs.rect):
                        game_over = True

                for star in stars:
                    star.update()

            screen.fill(BG_COLOR)

            for star in stars:
                star.draw(screen)

            player.draw(screen)

            for obs in obstacles:
                obs.draw(screen)

            if game_over:
                # Tela escurecida
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))

                draw_text("GAME OVER", font_large, OBSTACLE_COLOR, screen, WIDTH / 2, HEIGHT / 2 - 50)
                draw_text(f"Pontuação Final: {score}", font_small, TEXT_COLOR, screen, WIDTH / 2, HEIGHT / 2 + 10)
                draw_text("Pressione [ESC] para sair", font_small, (150, 150, 150), screen, WIDTH / 2, HEIGHT / 2 + 50)
            else:
                # Placar
                score_bg = pygame.Rect(10, 10, 200, 40)
                pygame.draw.rect(screen, (0, 0, 0), score_bg, border_radius=10)
                pygame.draw.rect(screen, PLAYER_COLOR, score_bg, 2, border_radius=10)
                draw_text(f"SCORE: {score}", font_score, TEXT_COLOR, screen, 110, 30, center=True)

                if cheats_enabled:
                    draw_text("IMORTAL", font_small, (0, 255, 0), screen, WIDTH - 80, 30)

            pygame.display.flip()
            clock.tick(60)

        return score

    return game_loop()
