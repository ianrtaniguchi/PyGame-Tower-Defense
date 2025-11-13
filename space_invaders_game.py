# JOGO FUNCIONAL
# Código feito pelos alunos: Ian Riki Taniguchi, João Alves Gava e João Vitor Del Pupo
import pygame
import sys
import random


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    try:
        font_small = pygame.font.SysFont("Arial", 24)
        font_large = pygame.font.SysFont("Arial", 60)
    except:
        font_small = pygame.font.Font(None, 32)
        font_large = pygame.font.Font(None, 74)

    class Player(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.image = pygame.Surface((50, 30))
            self.image.fill(GREEN)
            self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 20))
            self.speed = 8

        def update(self):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > 0:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
                self.rect.x += self.speed

        def shoot(self, all_sprites, projectiles):
            projectile = Projectile(self.rect.centerx, self.rect.top, -10, GREEN)
            all_sprites.add(projectile)
            projectiles.add(projectile)

    class Enemy(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((30, 20))
            self.image.fill(WHITE)
            self.rect = self.image.get_rect(topleft=(x, y))
            self.speed = 2

        def update(self):
            self.rect.x += self.speed

        def shoot(self, all_sprites, enemy_projectiles):
            projectile = Projectile(self.rect.centerx, self.rect.bottom, 10, RED)
            all_sprites.add(projectile)
            enemy_projectiles.add(projectile)

    class Projectile(pygame.sprite.Sprite):
        def __init__(self, x, y, speed, color):
            super().__init__()
            self.image = pygame.Surface((5, 10))
            self.image.fill(color)
            self.rect = self.image.get_rect(center=(x, y))
            self.speed = speed

        def update(self):
            self.rect.y += self.speed
            if self.rect.bottom < 0 or self.rect.top > HEIGHT:
                self.kill()

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def game_loop():
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        projectiles = pygame.sprite.Group()
        enemy_projectiles = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)

        score = 0
        lives = 999999999 if cheats_enabled else 3
        enemy_move_down = False
        enemy_shoot_timer = 0
        enemy_shoot_delay = 1000

        player_shoot_timer = 0
        player_shoot_delay = 500
        if cheats_enabled:
            player_shoot_delay = 1

        for row in range(5):
            for col in range(10):
                enemy = Enemy(100 + col * 50, 50 + row * 40)
                all_sprites.add(enemy)
                enemies.add(enemy)

        running = True
        game_over = False
        game_won = False

        while running:
            now = pygame.time.get_ticks()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if game_over or game_won:
                        if event.key == pygame.K_SPACE:
                            game_loop()
                            return
                    # Tiro removido daqui para ser baseado em tecla pressionada

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and not game_over:
                if now - player_shoot_timer > player_shoot_delay:
                    player.shoot(all_sprites, projectiles)
                    player_shoot_timer = now

            if game_over or game_won:
                screen.fill(BLACK)
                message = "VOCÊ VENCEU!" if game_won else "GAME OVER"
                color = GREEN if game_won else RED
                draw_text(message, font_large, color, screen, WIDTH / 2, HEIGHT / 2 - 40)
                draw_text(f"Pontuação: {score}", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 20)
                draw_text("Pressione [ESPAÇO] para reiniciar ou [ESC] para sair", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 60)
                pygame.display.flip()
                clock.tick(60)
                continue

            all_sprites.update()

            enemy_move_down = False
            for enemy in enemies:
                if enemy.rect.right > WIDTH or enemy.rect.left < 0:
                    enemy_move_down = True
                    break

            if enemy_move_down:
                for e in enemies:
                    e.rect.y += 10
                    e.speed *= -1

            if now - enemy_shoot_timer > enemy_shoot_delay and enemies:
                random.choice(enemies.sprites()).shoot(all_sprites, enemy_projectiles)
                enemy_shoot_timer = now

            hits = pygame.sprite.groupcollide(enemies, projectiles, True, True)
            for hit in hits:
                score += 10

            if not cheats_enabled:
                hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
                if hits:
                    lives -= 1
                    if lives <= 0:
                        game_over = True

                hits = pygame.sprite.spritecollide(player, enemies, False)
                if hits:
                    game_over = True

            if not enemies:
                game_won = True

            screen.fill(BLACK)
            all_sprites.draw(screen)

            draw_text(f"Pontuação: {score}", font_small, WHITE, screen, 10, 10, center=False)
            draw_text(f"Vidas: {lives}", font_small, WHITE, screen, WIDTH - 100, 10, center=False)

            pygame.display.flip()
            clock.tick(60)

    game_loop()
