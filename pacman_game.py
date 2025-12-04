# Pacman PRONTO
# Codigo feito por Ian Riki Taniguchi
import pygame
import sys
import random
import os


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    BLUE = (0, 0, 200)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    PINK = (255, 182, 193)
    ORANGE = (255, 165, 0)

    try:
        font_large = pygame.font.SysFont("Arial", 60)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 32)

    CELL_SIZE = 30
    GRID_WIDTH = 28
    GRID_HEIGHT = 20
    MAP_OFFSET_X = (WIDTH - (GRID_WIDTH * CELL_SIZE)) // 2
    MAP_OFFSET_Y = (HEIGHT - (GRID_HEIGHT * CELL_SIZE)) // 2

    MAP = [
        "1111111111111111111111111111",
        "1222222222222112222222222221",
        "1211112111112112111112111121",
        "1211112111112112111112111121",
        "1222222222222222222222222221",
        "1211112112111111112112111121",
        "1222222112222112222112222221",
        "1111112111110110111112111111",
        "0000012110000000000112100000",
        "1111112110111111110112111111",
        "2222222000100000010002222222",
        "1111112110111111110112111111",
        "0000012110000000000112100000",
        "1111112110111111110112111111",
        "1222222222222112222222222221",
        "1211112111112112111112111121",
        "1222112222222222222222112221",
        "1112112112111111112112112111",
        "1222222112222112222112222221",
        "1111111111111111111111111111",
    ]

    def load_img(path, size):
        full_path = os.path.join("assets", "images", path)
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path).convert_alpha()
                # print("carregou")
                return pygame.transform.scale(img, size)
            except Exception as e:
                print(f"Erro ao carregar imagem {path}: {e}")  # facilitar achar erro
        return None

    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            size = (CELL_SIZE - 4, CELL_SIZE - 4)
            self.sprite_img = load_img("Pacman/pacman-1.png.png", size)

            if self.sprite_img:
                self.image = self.sprite_img
                self.original_image = self.sprite_img
            else:
                self.image = pygame.Surface(size)  # desenho quadrado
                self.image.fill(YELLOW)
                pygame.draw.circle(self.image, BLACK, (size[0] // 2, size[1] // 2), CELL_SIZE // 2 - 2)
                pygame.draw.circle(self.image, YELLOW, (size[0] // 2, size[1] // 2), CELL_SIZE // 2 - 3)
                self.original_image = None
            self.angle = 0
            self.rect = self.image.get_rect(topleft=(MAP_OFFSET_X + x * CELL_SIZE + 2, MAP_OFFSET_Y + y * CELL_SIZE + 2))
            self.grid_x = x
            self.grid_y = y
            self.direction = (0, 0)
            self.next_direction = (0, 0)
            self.speed = 3

        def update(self):
            if (self.rect.x - MAP_OFFSET_X) % CELL_SIZE == 2 and (self.rect.y - MAP_OFFSET_Y) % CELL_SIZE == 2:
                self.grid_x = (self.rect.x - MAP_OFFSET_X) // CELL_SIZE
                self.grid_y = (self.rect.y - MAP_OFFSET_Y) // CELL_SIZE

                if self.next_direction != (0, 0):
                    nx = self.grid_x + self.next_direction[0]
                    ny = self.grid_y + self.next_direction[1]
                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        if MAP[ny][nx] != "1":
                            self.direction = self.next_direction
                    elif nx < 0 or nx >= GRID_WIDTH:
                        self.direction = self.next_direction

                nx = self.grid_x + self.direction[0]
                ny = self.grid_y + self.direction[1]

                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    if MAP[ny][nx] == "1":
                        self.direction = (0, 0)

            self.rect.x += self.direction[0] * self.speed
            self.rect.y += self.direction[1] * self.speed

            if self.rect.right <= MAP_OFFSET_X:
                self.rect.x = MAP_OFFSET_X + ((GRID_WIDTH - 1) * CELL_SIZE) + 2
            elif self.rect.left >= MAP_OFFSET_X + (GRID_WIDTH * CELL_SIZE):
                self.rect.x = MAP_OFFSET_X + 2

            if self.original_image and self.direction != (0, 0):
                if self.direction == (1, 0):
                    rot = 0
                elif self.direction == (-1, 0):
                    rot = 180
                elif self.direction == (0, -1):
                    rot = 90
                elif self.direction == (0, 1):
                    rot = 270
                else:
                    rot = 0
                self.image = pygame.transform.rotate(self.original_image, rot)

        def set_direction(self, dx, dy):
            self.next_direction = (dx, dy)

    class Ghost(pygame.sprite.Sprite):

        def __init__(self, x, y, color, img_file):
            super().__init__()
            size = (CELL_SIZE - 4, CELL_SIZE - 4)
            self.sprite = load_img(f"Pacman/fantasmas/{img_file}", size)
            if self.sprite:
                self.image = self.sprite
            else:
                self.image = pygame.Surface(size)
                self.image.fill(color)
            self.rect = self.image.get_rect(topleft=(MAP_OFFSET_X + x * CELL_SIZE + 2, MAP_OFFSET_Y + y * CELL_SIZE + 2))
            self.grid_x = x
            self.grid_y = y
            self.direction = (0, 0)
            self.speed = 2

        def update(self, player_grid_pos):
            self.rect.x += self.direction[0] * self.speed
            self.rect.y += self.direction[1] * self.speed

            if (self.rect.x - MAP_OFFSET_X) % CELL_SIZE == 2 and (self.rect.y - MAP_OFFSET_Y) % CELL_SIZE == 2:
                self.grid_x = (self.rect.x - MAP_OFFSET_X) // CELL_SIZE
                self.grid_y = (self.rect.y - MAP_OFFSET_Y) // CELL_SIZE

                possible_moves = []
                for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                    if (dx, dy) == (-self.direction[0], -self.direction[1]) and self.direction != (0, 0):
                        continue

                    nx, ny = self.grid_x + dx, self.grid_y + dy

                    if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                        if MAP[ny][nx] != "1":
                            possible_moves.append((dx, dy))
                    elif nx < 0 or nx >= GRID_WIDTH:
                        possible_moves.append((dx, dy))

                if not possible_moves:
                    possible_moves.append((-self.direction[0], -self.direction[1]))

                if possible_moves:
                    best_move = min(possible_moves, key=lambda m: abs((self.grid_x + m[0]) - player_grid_pos[0]) + abs((self.grid_y + m[1]) - player_grid_pos[1]))  # algoritmo de busca gulosa usando distância de Manhattan

                    if random.random() < 0.1:
                        self.direction = random.choice(possible_moves)
                    else:
                        self.direction = best_move
                else:
                    self.direction = (0, 0)

            if self.rect.right <= MAP_OFFSET_X:
                self.rect.x = MAP_OFFSET_X + ((GRID_WIDTH - 1) * CELL_SIZE) + 2
            elif self.rect.left >= MAP_OFFSET_X + (GRID_WIDTH * CELL_SIZE):
                self.rect.x = MAP_OFFSET_X + 2

    class Pellet(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((CELL_SIZE // 4, CELL_SIZE // 4))
            self.image.fill(WHITE)
            self.rect = self.image.get_rect(center=(MAP_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2, MAP_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2))

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw_map(surface):
        for y, row in enumerate(MAP):
            for x, char in enumerate(row):
                if char == "1":
                    wall_rect = pygame.Rect(MAP_OFFSET_X + x * CELL_SIZE, MAP_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, BLUE, wall_rect)

    def game_loop():
        all_sprites = pygame.sprite.Group()
        ghosts = pygame.sprite.Group()
        pellets = pygame.sprite.Group()

        player = Player(1, 1)
        all_sprites.add(player)

        ghost_specs = [
            (12, 8, RED, "fantasma pacman-1.png.png"),
            (13, 8, GREEN, "fantasma pacman-3.png.png"),
            (14, 8, PINK, "fantasma pacman-2.png.png"),
            (15, 8, ORANGE, "fantasma pacman-4.png.png"),
        ]

        for gx, gy, col, img_name in ghost_specs:
            g = Ghost(gx, gy, col, img_name)
            all_sprites.add(g)  # adiciona no vetor de sprites
            ghosts.add(g)

        for y, row in enumerate(MAP):
            for x, char in enumerate(row):
                if char == "2":
                    p = Pellet(x, y)
                    pellets.add(p)

        score = 0
        running = True
        game_over = False
        game_won = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if game_over or game_won:
                        if event.key == pygame.K_SPACE:
                            return game_loop()

                    if not game_over and not game_won:
                        if event.key == pygame.K_UP:
                            player.set_direction(0, -1)
                        elif event.key == pygame.K_DOWN:
                            player.set_direction(0, 1)
                        elif event.key == pygame.K_LEFT:
                            player.set_direction(-1, 0)
                        elif event.key == pygame.K_RIGHT:
                            player.set_direction(1, 0)

            if not game_over and not game_won:
                player.update()
                for ghost in ghosts:
                    ghost.update((player.grid_x, player.grid_y))

                eaten_pellets = pygame.sprite.spritecollide(player, pellets, True)
                if eaten_pellets:
                    score += len(eaten_pellets) * 10

                if not cheats_enabled:
                    if pygame.sprite.spritecollide(player, ghosts, False):
                        game_over = True

                if len(pellets) == 0:
                    game_won = True

            screen.fill(BLACK)
            draw_map(screen)
            pellets.draw(screen)
            all_sprites.draw(screen)

            draw_text(f"Pontuação: {score}", font_small, WHITE, screen, 20, 10, center=False)
            if cheats_enabled:
                draw_text("CHEATS ATIVADOS", font_small, GREEN, screen, WIDTH - 150, 10, center=True)

            if game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                draw_text("GAME OVER", font_large, RED, screen, WIDTH / 2, HEIGHT / 2 - 40)
                draw_text("Pressione [ESPAÇO] para reiniciar", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 30)
                draw_text("ou [ESC] para sair", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 60)

            if game_won:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                draw_text("VOCÊ VENCEU!", font_large, GREEN, screen, WIDTH / 2, HEIGHT / 2 - 40)
                draw_text(f"Score Final: {score}", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 20)
                draw_text("Pressione [ESPAÇO] para reiniciar", font_small, WHITE, screen, WIDTH / 2, HEIGHT / 2 + 60)

            pygame.display.flip()
            clock.tick(60)

        return score

    return game_loop()
