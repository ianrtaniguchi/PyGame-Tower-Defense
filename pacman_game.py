import pygame
import sys
import random


def main(screen, clock):
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
        "1222222000100000010002222221",
        "1111112110111111110112111111",
        "0000012110000000000112100000",
        "1111112110111111110112111111",
        "1222222222222112222222222221",
        "1211112111112112111112111121",
        "1222112222222222222221122221",
        "1112112112111111112112112111",
        "1222222112222112222112222221",
        "1111111111111111111111111111",
    ]  # 0: caminho, 1: parede

    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4))
            self.image.fill(YELLOW)
            pygame.draw.circle(
                self.image,
                BLACK,
                (self.image.get_width() // 2, self.image.get_height() // 2),
                CELL_SIZE // 2 - 2,
            )
            pygame.draw.circle(
                self.image,
                YELLOW,
                (self.image.get_width() // 2, self.image.get_height() // 2),
                CELL_SIZE // 2 - 3,
            )
            self.rect = self.image.get_rect(
                topleft=(
                    MAP_OFFSET_X + x * CELL_SIZE + 2,
                    MAP_OFFSET_Y + y * CELL_SIZE + 2,
                )
            )
            self.grid_x = x
            self.grid_y = y
            self.direction = (0, 0)
            self.next_direction = (0, 0)
            self.speed = 3

        def update(self, walls):
            new_rect = self.rect.copy()

            if self.rect.x % CELL_SIZE == 2 and self.rect.y % CELL_SIZE == 2:
                self.grid_x = (self.rect.x - MAP_OFFSET_X) // CELL_SIZE
                self.grid_y = (self.rect.y - MAP_OFFSET_Y) // CELL_SIZE

                next_x = self.grid_x + self.next_direction[0]
                next_y = self.grid_y + self.next_direction[1]

                if (
                    next_x >= 0
                    and next_x < GRID_WIDTH
                    and next_y >= 0
                    and next_y < GRID_HEIGHT
                    and MAP[next_y][next_x] != "1"
                ):
                    self.direction = self.next_direction

            new_rect.x += self.direction[0] * self.speed
            new_rect.y += self.direction[1] * self.speed

            if new_rect.x % CELL_SIZE == 2 and new_rect.y % CELL_SIZE == 2:
                next_x = self.grid_x + self.direction[0]
                next_y = self.grid_y + self.direction[1]

                if (
                    next_x < 0
                    or next_x >= GRID_WIDTH
                    or next_y < 0
                    or next_y >= GRID_HEIGHT
                    or MAP[next_y][next_x] == "1"
                ):
                    self.direction = (0, 0)

            self.rect = new_rect

        def set_direction(self, dx, dy):
            self.next_direction = (dx, dy)

    class Ghost(pygame.sprite.Sprite):
        def __init__(self, x, y, color):
            super().__init__()
            self.image = pygame.Surface((CELL_SIZE - 4, CELL_SIZE - 4))
            self.image.fill(color)
            self.rect = self.image.get_rect(
                topleft=(
                    MAP_OFFSET_X + x * CELL_SIZE + 2,
                    MAP_OFFSET_Y + y * CELL_SIZE + 2,
                )
            )
            self.grid_x = x
            self.grid_y = y
            self.direction = (0, 0)
            self.speed = 2
            self.last_move = 0

        def update(self, player_grid_pos):
            if pygame.time.get_ticks() - self.last_move < 200:
                self.rect.x += self.direction[0] * self.speed
                self.rect.y += self.direction[1] * self.speed
                return

            self.last_move = pygame.time.get_ticks()
            self.grid_x = (self.rect.x - MAP_OFFSET_X) // CELL_SIZE
            self.grid_y = (self.rect.y - MAP_OFFSET_Y) // CELL_SIZE

            possible_moves = []
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if (dx, dy) == (-self.direction[0], -self.direction[1]):
                    continue
                next_x = self.grid_x + dx
                next_y = self.grid_y + dy
                if (
                    next_x >= 0
                    and next_x < GRID_WIDTH
                    and next_y >= 0
                    and next_y < GRID_HEIGHT
                    and MAP[next_y][next_x] != "1"
                ):
                    possible_moves.append((dx, dy))

            if not possible_moves:
                self.direction = (-self.direction[0], -self.direction[1])
            else:
                best_move = possible_moves[0]
                min_dist = float("inf")

                for move in possible_moves:
                    dist = abs(self.grid_x + move[0] - player_grid_pos[0]) + abs(
                        self.grid_y + move[1] - player_grid_pos[1]
                    )
                    if dist < min_dist:
                        min_dist = dist
                        best_move = move

                self.direction = best_move

            self.rect.x = MAP_OFFSET_X + self.grid_x * CELL_SIZE + 2
            self.rect.y = MAP_OFFSET_Y + self.grid_y * CELL_SIZE + 2
            self.rect.x += self.direction[0] * self.speed
            self.rect.y += self.direction[1] * self.speed

    class Pellet(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pygame.Surface((CELL_SIZE // 4, CELL_SIZE // 4))
            self.image.fill(WHITE)
            pygame.draw.circle(
                self.image,
                BLACK,
                (self.image.get_width() // 2, self.image.get_height() // 2),
                CELL_SIZE // 8,
            )
            pygame.draw.circle(
                self.image,
                WHITE,
                (self.image.get_width() // 2, self.image.get_height() // 2),
                CELL_SIZE // 8 - 1,
            )
            self.rect = self.image.get_rect(
                center=(
                    MAP_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2,
                    MAP_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2,
                )
            )

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw_map(surface, walls):
        for y, row in enumerate(MAP):
            for x, char in enumerate(row):
                if char == "1":
                    wall_rect = pygame.Rect(
                        MAP_OFFSET_X + x * CELL_SIZE,
                        MAP_OFFSET_Y + y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(surface, BLUE, wall_rect)
                    walls.append(wall_rect)

    def game_loop():
        all_sprites = pygame.sprite.Group()
        ghosts = pygame.sprite.Group()
        pellets = pygame.sprite.Group()
        walls = []

        player = Player(1, 1)
        all_sprites.add(player)

        ghost_list = [
            Ghost(12, 8, RED),
            Ghost(13, 8, GREEN),
            Ghost(14, 8, PINK),
            Ghost(15, 8, ORANGE),
        ]
        for g in ghost_list:
            all_sprites.add(g)
            ghosts.add(g)

        total_pellets = 0
        for y, row in enumerate(MAP):
            for x, char in enumerate(row):
                if char == "2":
                    p = Pellet(x, y)
                    all_sprites.add(p)
                    pellets.add(p)
                    total_pellets += 1

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
                            game_loop()
                            return
                    if event.key == pygame.K_UP:
                        player.set_direction(0, -1)
                    if event.key == pygame.K_DOWN:
                        player.set_direction(0, 1)
                    if event.key == pygame.K_LEFT:
                        player.set_direction(-1, 0)
                    if event.key == pygame.K_RIGHT:
                        player.set_direction(1, 0)

            if game_over or game_won:
                screen.fill(BLACK)
                message = "VOCÊ VENCEU!" if game_won else "GAME OVER"
                color = YELLOW if game_won else RED
                draw_text(
                    message, font_large, color, screen, WIDTH / 2, HEIGHT / 2 - 40
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

            player.update(walls)
            for ghost in ghosts:
                ghost.update((player.grid_x, player.grid_y))

            eaten_pellets = pygame.sprite.spritecollide(player, pellets, True)
            if eaten_pellets:
                score += len(eaten_pellets) * 10

            if pygame.sprite.spritecollide(player, ghosts, False):
                game_over = True

            if len(pellets) == 0:
                game_won = True

            screen.fill(BLACK)

            temp_walls = []
            draw_map(screen, temp_walls)

            pellets.draw(screen)
            all_sprites.draw(screen)

            draw_text(
                f"Pontuação: {score}", font_small, WHITE, screen, 10, 10, center=False
            )

            pygame.display.flip()
            clock.tick(60)

    game_loop()
