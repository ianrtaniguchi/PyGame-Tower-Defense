# JOGO FUNCIONAL PRONTO
import pygame
import sys
import random
import os


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    SKY_BLUE = (113, 197, 207)
    GROUND_COLOR = (222, 216, 149)
    GRASS_COLOR = (115, 191, 46)

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    BIRD_BODY = (255, 210, 0)
    BIRD_BEAK = (230, 80, 0)
    BIRD_WING = (240, 240, 230)

    PIPE_MAIN = (115, 190, 46)
    PIPE_HIGHLIGHT = (165, 230, 80)
    PIPE_SHADOW = (85, 120, 30)
    PIPE_BORDER = (45, 60, 20)

    try:
        font_large = pygame.font.SysFont("Arial", 60, bold=True)
        font_medium = pygame.font.SysFont("Arial", 40, bold=True)
        font_small = pygame.font.SysFont("Arial", 24, bold=True)
    except:
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 50)
        font_small = pygame.font.Font(None, 32)

    def create_bird_surface():
        surf = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, BIRD_BODY, (0, 0, 40, 30))
        pygame.draw.ellipse(surf, BLACK, (0, 0, 40, 30), 2)
        pygame.draw.circle(surf, WHITE, (28, 10), 8)
        pygame.draw.circle(surf, BLACK, (28, 10), 8, 1)
        pygame.draw.circle(surf, BLACK, (30, 10), 3)
        pygame.draw.ellipse(surf, BIRD_WING, (5, 16, 22, 10))
        pygame.draw.ellipse(surf, BLACK, (5, 16, 22, 10), 1)
        points = [(30, 18), (40, 22), (32, 26)]
        pygame.draw.polygon(surf, BIRD_BEAK, points)
        pygame.draw.polygon(surf, BLACK, points, 1)
        return surf

    def create_pipe_surface(width, height, is_top):
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        cap_height = 26
        body_y = 0 if is_top else cap_height
        body_h = height - cap_height
        cap_y = height - cap_height if is_top else 0

        body_rect = pygame.Rect(4, body_y, width - 8, body_h)
        pygame.draw.rect(surf, PIPE_MAIN, body_rect)
        pygame.draw.rect(surf, PIPE_HIGHLIGHT, (4, body_y, 10, body_h))
        pygame.draw.rect(surf, PIPE_SHADOW, (width - 14, body_y, 6, body_h))
        pygame.draw.rect(surf, PIPE_BORDER, body_rect, 2)

        cap_rect = pygame.Rect(0, cap_y, width, cap_height)
        pygame.draw.rect(surf, PIPE_MAIN, cap_rect)
        pygame.draw.rect(surf, PIPE_HIGHLIGHT, (0, cap_y, 14, cap_height))
        pygame.draw.rect(surf, PIPE_BORDER, cap_rect, 2)

        return surf

    def load_image_asset(filename, size=None):
        possible_paths = [os.path.join("assets", "images", filename), filename]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    if size:
                        img = pygame.transform.scale(img, size)
                    return img
                except Exception as e:
                    print(f"Erro ao carregar {filename}: {e}")
        return None

    bird_path = os.path.join("flappy bird", "flappy-1.png.png")
    loaded_bird = load_image_asset(bird_path, (40, 30))
    BIRD_IMG_ORIGINAL = loaded_bird if loaded_bird else create_bird_surface()

    pipe_path = os.path.join("flappy bird", "cano-1.png.png")

    class Bird(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = BIRD_IMG_ORIGINAL.copy()
            self.rect = self.image.get_rect(center=(100, HEIGHT // 2))
            self.velocity = 0
            self.gravity = 0.5
            self.lift = -9
            self.angle = 0

        def update(self):
            self.velocity += self.gravity
            self.rect.y += self.velocity

            target_angle = max(-90, min(20, -self.velocity * 3))
            self.angle += (target_angle - self.angle) * 0.1

            self.image = pygame.transform.rotate(BIRD_IMG_ORIGINAL, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

            if self.rect.top < 0:
                self.rect.top = 0
                self.velocity = 0

        def flap(self):
            self.velocity = self.lift

    class Pipe(pygame.sprite.Sprite):
        def __init__(self, x, y, height, is_top):
            super().__init__()

            if PIPE_IMG_BASE:
                scaled_pipe = pygame.transform.scale(PIPE_IMG_BASE, (80, height))
                if is_top:
                    self.image = pygame.transform.flip(scaled_pipe, False, True)
                else:
                    self.image = scaled_pipe
            else:
                self.image = create_pipe_surface(80, height, is_top)

            self.rect = self.image.get_rect()
            self.speed = 4

            if is_top:
                self.rect.bottomleft = (x, y)
            else:
                self.rect.topleft = (x, y)

        def update(self):
            self.rect.x -= self.speed
            if self.rect.right < 0:
                self.kill()

    def draw_text(text, font, color, surface, x, y, center=True):
        shadow = font.render(text, True, BLACK)
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

    def create_pipes(all_sprites, pipes):
        min_pipe_h = 50
        gap_height = 160

        available_height = HEIGHT - gap_height - (min_pipe_h * 2) - 50

        if available_height > 0:
            top_height = random.randint(min_pipe_h, min_pipe_h + available_height)
            bottom_height = HEIGHT - gap_height - top_height - 50

            pipe_top = Pipe(WIDTH, top_height, top_height, True)
            pipe_bottom = Pipe(WIDTH, top_height + gap_height, bottom_height, False)

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
        pipe_delay = 1800

        running = True
        game_over = False
        game_started = False

        ground_scroll = 0

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
                            bird.flap()
                        elif not game_over:
                            bird.flap()
                        else:
                            game_loop()
                            return

            screen.fill(SKY_BLUE)

            ground_h = 50
            ground_y = HEIGHT - ground_h
            if not game_over:
                ground_scroll = (ground_scroll - 4) % 40

            pygame.draw.rect(screen, GRASS_COLOR, (0, ground_y, WIDTH, 10))
            pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y + 10, WIDTH, ground_h - 10))

            for i in range(0, WIDTH + 40, 40):
                pygame.draw.line(screen, (200, 190, 130), (i + ground_scroll, ground_y + 10), (i + ground_scroll - 20, HEIGHT), 2)

            pygame.draw.line(screen, (80, 160, 20), (0, ground_y), (WIDTH, ground_y), 2)

            if not game_started:
                offset = int(pygame.time.get_ticks() * 0.005) % 10
                screen.blit(BIRD_IMG_ORIGINAL, (WIDTH // 2 - 20, HEIGHT // 2 - 15 + offset))

                draw_text("FLAPPY BIRD", font_large, WHITE, screen, WIDTH / 2, HEIGHT / 2 - 80)
                draw_text("Pressione [ESPAÇO] para voar", font_small, BLACK, screen, WIDTH / 2, HEIGHT / 2 + 50)
                draw_text("[ESC] para voltar", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 90)

                pygame.display.flip()
                clock.tick(60)
                continue

            if not game_over:
                all_sprites.update()

                now = pygame.time.get_ticks()
                if now - pipe_timer > pipe_delay:
                    create_pipes(all_sprites, pipes)
                    pipe_timer = now

                for pipe in pipes:
                    if getattr(pipe, "rect").top < HEIGHT // 2:
                        if pipe.rect.right < bird.rect.left and not hasattr(pipe, "scored"):
                            score += 1
                            pipe.scored = True

                if bird.rect.bottom >= ground_y:
                    bird.rect.bottom = ground_y
                    bird.velocity = 0

                    if not cheats_enabled:
                        game_over = True

                if not cheats_enabled:
                    if pygame.sprite.spritecollide(bird, pipes, False, pygame.sprite.collide_mask):
                        game_over = True

            pipes.draw(screen)
            screen.blit(bird.image, bird.rect)

            draw_text(str(int(score)), font_large, WHITE, screen, WIDTH // 2, 80)

            if cheats_enabled:
                draw_text("GOD MODE", font_small, (0, 255, 0), screen, WIDTH - 80, 30, center=True)

            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 128))
                screen.blit(overlay, (0, 0))

                box_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 200)
                pygame.draw.rect(screen, (220, 220, 200), box_rect, border_radius=15)
                pygame.draw.rect(screen, (80, 80, 80), box_rect, 4, border_radius=15)

                draw_text("GAME OVER", font_medium, (230, 80, 0), screen, WIDTH / 2, HEIGHT / 2 - 60)
                draw_text(f"Score: {int(score)}", font_small, BLACK, screen, WIDTH / 2, HEIGHT / 2)

                draw_text("[ESPAÇO] Jogar Novamente", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 130)
                draw_text("[ESC] Sair", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 160)

            pygame.display.flip()
            clock.tick(60)

    game_loop()
