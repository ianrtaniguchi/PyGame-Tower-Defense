# =============================================================================
# PROJETO PYGAME - TOWER DEFENSE
#
#  Nomes dos componentes do grupo:
# - Ian Riki Taniguchi
# - João Alves Gava
# - João Vitor Del Pupo
#
#  Dependências:
# - pygame (instalar com: pip install pygame[caso tenha pip instalado])
# - pip install typing-extensions (precisa para compatibilidade com algumas versões do python)
# - pip install setuptools
# - pip install Pyrebase4
# - pip install pygame
#
#   Orientações de execução:
# - Execute este arquivo (main.py) (após as dependências serem instaladas, garanta também que a pasta 'assets' com as imagens e sons esteja no mesmo diretório).
# - Tela de Menu:
# - Pressione [ESPAÇO] para iniciar o jogo.
# - Tela do Jogo:
# - Use o mouse para clicar nos ícones de torre na UI inferior.
# - Clique em um dos círculos verdes (slots) no mapa para construir.
# - Pressione [ESC] para cancelar o modo de construção.
# - Tela de ou Game Over ou Vitória:
# - Pressione [ESPAÇO] para reiniciar.
#
# =============================================================================

import pygame
import sys
import math
import random
from pathlib import Path
import os  # Importado para o PyInstaller

# =============================================================================
# 1. CONFIGURAÇÕES INICIAIS
# =============================================================================

# Inicializa o Pygame e o mixer de áudio
# (Removido, o hub cuida disso)

# Configuração do Pathlib (para garantir que funcione em qualquer pasta)
if getattr(sys, "frozen", False):
    # Se estiver rodando em um .exe (congelado pelo PyInstaller)
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Se estiver rodando como script .py normal
    try:
        BASE_DIR = Path(__file__).resolve().parent
    except NameError:
        BASE_DIR = Path(".").resolve()

ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"


# consts da screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720  # Deixa 100px na parte inferior para UI
UI_PANEL_HEIGHT = 100
GAME_HEIGHT = SCREEN_HEIGHT - UI_PANEL_HEIGHT
FPS = 60

# consts do jogo
INITIAL_LIVES = 20
INITIAL_MONEY = 300  # Aumentado para permitir construção inicial

# Cores como const para poder trabalhar dps com melhor simplicidade
# Caps lock const (convenção)
LIGHT_BLUE = (173, 216, 230)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (100, 100, 100)
ORANGE = (255, 165, 0)

# Configurações da janela (Removido, o hub cuida disso)
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Tower Defense")
# clock = pygame.time.Clock()

# --- Métodos auxiliares para carregar as mídias ---


# Fallback de assets. Se alguém esquecer de dar 'commit' em uma imagem,
# isso aqui cria um quadrado colorido e evita que o jogo CRASHE.
def create_placeholder_surface(width, height, color):  # Cria uma superfície de cor sólida como placeholder
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(color)
    return surface


def load_image(filename, placeholder_size, placeholder_color, colorkey=None, scale=None):
    try:
        path = IMAGES_DIR / filename
        if not path.exists():
            path = IMAGES_DIR / Path(filename).name

        img = pygame.image.load(str(path))

        if scale:
            img = pygame.transform.scale(img, scale)

        if colorkey is not None:
            img = img.convert()
            img.set_colorkey(colorkey)
        else:
            img = img.convert_alpha()

        return img
    except (pygame.error, FileNotFoundError):
        print(f"AVISO: Imagem '{filename}' não encontrada. Usando placeholder.")
        return create_placeholder_surface(placeholder_size[0], placeholder_size[1], placeholder_color)


def load_sound(filename, volume=0.20):  # Tenta carregar um som, se falhar, retorna um objeto vazio do tipo 'none'
    try:
        sound = pygame.mixer.Sound(str(SOUNDS_DIR / filename))
        sound.set_volume(volume)
        return sound

    except pygame.error:
        print(f"AVISO: Som '{filename}' não encontrado.")
        return None


# Carregamento em si das midias
try:
    print(f"Tentando carregar mapa de: {str(IMAGES_DIR / 'map.png')}")

    background_image = pygame.image.load(str(IMAGES_DIR / "map.png")).convert()
except pygame.error as e:
    print(f"Erro CRÍTICO ao carregar 'map.png': {e}")
    print("O 'map.png' é essencial. Criando um fundo preto por padrão.")
    background_image = create_placeholder_surface(SCREEN_WIDTH, GAME_HEIGHT, BLACK)

# --- Carregamento de Assets dos Inimigos ---

# 1. Eye Monster (Tanque) -> Arquivos .jpg
eye_walk_imgs = []
for i in range(1, 9):
    # Correção: Extensão mudada para .png
    img = load_image(f"Eye-Monster/walk/monster-{i}.png", (40, 40), BLUE, scale=(50, 50))
    eye_walk_imgs.append(img)

eye_death_imgs = []
for i in range(1, 5):
    # Correção: Extensão mudada para .png
    img = load_image(f"Eye-Monster/death/death-{i}.png", (40, 40), RED, scale=(50, 50))
    eye_death_imgs.append(img)

# 2. Skeleton (Soldier) -> Arquivos .png
# IMPORTANTE: Crie uma pasta chamada "Skeleton" dentro de assets/images e coloque os arquivos lá
skelly_walk_imgs = []
for i in range(1, 4):
    # Correção: pasta 'skeleton/side/'
    img = load_image(f"skeleton/side/base.skelly.side ({i}).png", (32, 32), GREY, scale=(40, 40))
    skelly_walk_imgs.append(img)

skelly_death_imgs = []
for i in range(1, 9):
    # Correção: pasta 'skeleton/death/'
    img = load_image(f"skeleton/death/base.skelly.death ({i}).png", (32, 32), RED, scale=(40, 40))
    skelly_death_imgs.append(img)


# Correção: Apontando para o arquivo correto da torre 1
arrow_tower_sprite = load_image("tipo 1 de torre/tower - 1.png", (48, 48), GREEN)

# Correção: Apontando para o arquivo correto da torre 2 (Canhão)
cannon_tower_sprite = load_image("tipo 2 torre/New Piskel (1).png", (48, 48), RED)
arrow_projectile_sprite = load_image("arrow_projectile.png", (10, 10), WHITE)
cannon_projectile_sprite = load_image("cannon_projectile.png", (15, 15), ORANGE)

# Carregamento dos Sons
sfx_arrow_fire = load_sound("tower_defense_fx/Other/Shot.wav")
sfx_cannon_fire = load_sound("tower_defense_fx/Other/Gunshot_1_A.wav")
sfx_enemy_death = load_sound("enemy_death.wav")
sfx_life_lost = load_sound("life_lost.wav")
sfx_build = load_sound("build.wav")
sfx_explosion = load_sound("tower_defense_fx/Other/Explosion.wav")  # Novo som de explosão

# Fontes
try:  # boa pratica
    font_large = pygame.font.SysFont("Arial", 48)
    font_medium = pygame.font.SysFont("Arial", 24)
    font_small = pygame.font.SysFont("Arial", 18)
except:  # esse except garante que caso o sistema não tenha a fonte Arial, ele use a fonte padrão já baixada com o pygame
    font_large = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

# Sons # load_sound retorna um objeto do tipo Sound que é carregado para cada classe, a classe Sound é definida na própria biblioteca pygame

ost_normal = load_sound("tower_defense_fx/OST/Main OST cut.wav")
ost_cheats = load_sound("tower_defense_fx/OST/Ligeiro-OST_1_.wav")


# --- Definições do Jogo ---

# Definição do Caminho (Waypoints)
WAYPOINTS = [  # esses waypoints definem o caminho que os inimigos vão seguir, são coordenadas x,y que podem ser mudadas, mas dependem do mapa para fazer sentido visual
    (-100, 150),
    (300, 150),
    (300, 400),
    (1000, 400),
    (1000, 200),
    (1380, 200),  # Ponto final (fora da tela)
]

# Locais de construção das torres, necessário alterar conforme o mapa (Del Pupo)
TOWER_SLOTS = [
    (200, 250),
    (400, 250),
    (200, 350),
    (500, 500),
    (700, 500),
    (900, 500),
    (900, 300),
]

TORRE_SLOT_RECTS = [pygame.Rect(pos[0] - 24, pos[1] - 24, 48, 48) for pos in TOWER_SLOTS]  # cria os rects para cada slot, que detecta a colisão do mouse os pos sao para centralizar o rect, 24 metade dos 48 pixels, deve ser alterado se mudar o tamanho das torres
occupied_slots = []  # slots que já tem torre

WAVE_DEFINITIONS = [  # define quantos soldier_sprites e tanks cada onda possui
    {"soldier": 5, "tank": 0},  # Onda 1
    {"soldier": 10, "tank": 0},  # Onda 2
    {"soldier": 15, "tank": 2},  # Onda 3
    {"soldier": 10, "tank": 5},  # Onda 4
    {"soldier": 0, "tank": 10},  # Onda 5
    {"soldier": 20, "tank": 10},  # Onda 6
]

# Definição das Torres
TOWER_DATA = {
    # define os atributos de cada tipo de torre e bota no dicionario TOWER_DATA a chave é o tipo da torre e o valor é o dicionario com os atributos(poderia ser usado objeto mas dicionario é simples eficiente e 100% funcional nesse caso)
    # Deixamos em um dict global para facilitar o balanceamento e a adição de novas torres
    # sem precisar mexer nas classes.
    "arrow": {
        "image": arrow_tower_sprite,
        "cost": 50,
        "range": 150,
        "fire_rate": 1000,  # ms
        "damage": 25,
    },
    "cannon": {
        "image": cannon_tower_sprite,
        "cost": 120,
        "range": 120,
        "fire_rate": 2000,  # ms
        "damage": 50,
        "splash_radius": 50,  # Raio do dano em área
    },
}

# =============================================================================
# 2. CLASSES DO JOGO
# =============================================================================


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, path):
        super().__init__()
        self.path = path
        self.waypoint_index = 0
        self.pos = pygame.math.Vector2(self.path[0])
        self.enemy_type = enemy_type

        self.flip = False
        self.state = "walking"
        self.frame_index = 0
        self.animation_speed = 0.15

        # --- CORREÇÃO: TUDO ISSO AGORA ESTÁ DENTRO DO __INIT__ (COM TAB) ---
        if enemy_type == "soldier":
            # Soldier usa o ESQUELETO
            self.sprites_walk = skelly_walk_imgs if skelly_walk_imgs else [create_placeholder_surface(32, 32, GREY)]
            self.sprites_death = skelly_death_imgs if skelly_death_imgs else [create_placeholder_surface(32, 32, RED)]
            self.speed = 3
            self.max_health = 80
            self.reward = 15
            self.animation_speed = 0.15
            self.image = self.sprites_walk[0]  # Define imagem inicial

        elif enemy_type == "tank":
            # Tank usa o EYE MONSTER
            self.sprites_walk = eye_walk_imgs if eye_walk_imgs else [create_placeholder_surface(40, 40, BLUE)]
            self.sprites_death = eye_death_imgs if eye_death_imgs else [create_placeholder_surface(40, 40, RED)]
            self.speed = 1.5
            self.max_health = 300
            self.reward = 30
            self.animation_speed = 0.2
            self.image = self.sprites_walk[0]  # Define imagem inicial

        else:
            # Fallback de segurança (Evita o crash se o tipo for desconhecido)
            self.sprites_walk = [create_placeholder_surface(32, 32, WHITE)]
            self.sprites_death = [create_placeholder_surface(32, 32, WHITE)]
            self.speed = 1
            self.max_health = 10
            self.reward = 1
            self.image = self.sprites_walk[0]  # Define imagem inicial
        # -------------------------------------------------------------------

        # Cria o retângulo (Hitbox) baseado na imagem definida acima
        self.rect = self.image.get_rect(center=self.pos)
        self.health = self.max_health

    def update(self):
        if self.state == "dying":
            self.animate_death()
        else:
            self.move()
            self.animate_walk()

    def move(self):
        target_vector = pygame.math.Vector2(self.path[self.waypoint_index])
        try:
            diff = target_vector - self.pos
            direction = diff.normalize()

            # Verifica direção para virar o sprite (flip)
            if direction.x < 0:
                self.flip = True  # Vira para esquerda
            elif direction.x > 0:
                self.flip = False  # Normal (direita)

        except ValueError:
            direction = pygame.math.Vector2(0, 0)

        self.pos += direction * self.speed
        self.rect.center = self.pos

        if (target_vector - self.pos).length_squared() < (self.speed * 1.5) ** 2:
            self.waypoint_index += 1
            if self.waypoint_index >= len(self.path):
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"tipo": "enemy_leaked"}))
                self.kill()

    def animate_walk(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.sprites_walk):
            self.frame_index = 0

        current_img = self.sprites_walk[int(self.frame_index)]

        if self.flip:
            current_img = pygame.transform.flip(current_img, True, False)

        self.image = current_img
        self.rect = self.image.get_rect(center=self.pos)

    def animate_death(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.sprites_death):
            self.kill()
        else:
            current_img = self.sprites_death[int(self.frame_index)]
            if self.flip:
                current_img = pygame.transform.flip(current_img, True, False)
            self.image = current_img
            self.rect = self.image.get_rect(center=self.pos)

    def take_damage(self, amount):
        if self.state == "dying":
            return 0
        self.health -= amount
        if self.health <= 0:
            self.state = "dying"
            self.frame_index = 0
            if sfx_enemy_death:
                sfx_enemy_death.play()
            return self.reward
        return 0

    def draw_health_bar(self, surface):
        if self.health < self.max_health and self.state != "dying":
            bar_w = 40
            bar_h = 5
            ratio = self.health / self.max_health
            bx = self.rect.centerx - bar_w / 2
            by = self.rect.top - 10
            pygame.draw.rect(surface, RED, (bx, by, bar_w, bar_h))
            pygame.draw.rect(surface, GREEN, (bx, by, bar_w * ratio, bar_h))


class Tower(pygame.sprite.Sprite):  # Classe para as torres de defesa.
    def __init__(self, tower_type, pos):
        super().__init__()
        self.data = TOWER_DATA[tower_type].copy()  # Copy é importante para não alterar o original
        self.damage_level = 1
        self.speed_level = 1

        self.pos = pygame.math.Vector2(pos)
        self.tower_type = tower_type

        self.image = self.data["image"]
        self.range = self.data["range"]
        self.fire_rate = self.data["fire_rate"]
        self.damage = self.data["damage"]

        self.rect = self.image.get_rect(center=self.pos)
        self.last_shot_time = pygame.time.get_ticks()
        self.target = None

    def get_upgrade_cost(self, upgrade_type):
        base_cost = self.data["cost"]
        if upgrade_type == "damage":
            return int(base_cost * 0.6 * self.damage_level)
        elif upgrade_type == "speed":
            return int(base_cost * 0.6 * self.speed_level)
        return 0

    def upgrade_damage(self):
        self.damage = int(self.damage * 1.3)  # Aumenta 30%
        self.damage_level += 1
        if sfx_build:
            sfx_build.play()

    def upgrade_speed(self):
        self.fire_rate = int(self.fire_rate * 0.85)  # Reduz tempo em 15% (atira mais rápido)
        self.speed_level += 1
        if sfx_build:
            sfx_build.play()

    def update(self, enemy_group, projectile_group):  # Encontra um alvo e atira.
        self.find_target(enemy_group)

        if self.target:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= self.fire_rate:
                self.shoot(projectile_group)
                self.last_shot_time = now

    def find_target(self, enemy_group):
        if self.target and (not self.target.alive() or self.target.state == "dying" or (self.target.pos - self.pos).length() > self.range):
            self.target = None

        if not self.target:
            closest_dist_sq = self.range**2
            # Filtra apenas inimigos que NÃO estão morrendo
            valid_enemies = [e for e in enemy_group if e.state != "dying"]
            for enemy in valid_enemies:
                dist_sq = (enemy.pos - self.pos).length_squared()
                if dist_sq <= closest_dist_sq:
                    closest_dist_sq = dist_sq
                    self.target = enemy

    def shoot(self, projectile_group):  #  Cria um novo projétil  do tipo da torre
        if self.tower_type == "arrow":
            projectile = Projectile("arrow", self.pos, self.target, self.damage)
            projectile_group.add(projectile)
            if sfx_arrow_fire:
                sfx_arrow_fire.play()

        elif self.tower_type == "cannon":
            projectile = Projectile("cannon", self.pos, self.target, self.damage, self.data["splash_radius"])
            projectile_group.add(projectile)
            if sfx_cannon_fire:
                sfx_cannon_fire.play()

    def draw_range(self, surface):  #  Desenha o círculo de alcance da torre pra cada torre
        range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, (255, 255, 255, 50), (self.range, self.range), self.range)
        surface.blit(range_surface, (self.pos.x - self.range, self.pos.y - self.range))


class Projectile(pygame.sprite.Sprite):  # Classe dos projéteis disparados pelas torres.
    def __init__(self, projectile_type, pos, target, damage, splash_radius=0):
        super().__init__()

        self.projectile_type = projectile_type  # tipo do projetil
        self.pos = pygame.math.Vector2(pos)  # posicao usando vetor do pygame
        self.target = target
        self.damage = damage

        if self.projectile_type == "arrow":  # flecha e canhao tem comportamentos diferentes
            self.image = arrow_projectile_sprite
            self.speed = 10

        elif self.projectile_type == "cannon":
            self.image = cannon_projectile_sprite
            self.speed = 6
            self.splash_radius = splash_radius
            # Canhão mira na POSIÇÃO, não no alvo vector serve pra isso.
            self.target_pos = pygame.math.Vector2(target.pos)

        self.rect = self.image.get_rect(center=self.pos)

    def update(self, enemy_group, money_callback):  # da update para mover o projetil e checar colisões.
        if self.projectile_type == "arrow":
            self.move_arrow(money_callback)  # chama o metodo de mover flecha e chama o callback de dinheiro
        elif self.projectile_type == "cannon":
            self.move_cannon(enemy_group, money_callback)  # chama o método de mover canhão

    def move_arrow(self, money_callback):  #  Lógica da flecha teleguiada
        if not self.target or not self.target.alive() or self.target.state == "dying":
            self.kill()
            return
        try:
            direction = (self.target.pos - self.pos).normalize()
        except ValueError:
            direction = pygame.math.Vector2(0, 0)

        self.pos += direction * self.speed
        self.rect.center = self.pos

        # Checar colisão
        if pygame.sprite.collide_circle(self, self.target):
            reward = self.target.take_damage(self.damage)
            money_callback(reward)  # Adiciona dinheiro
            self.kill()

    def move_cannon(self, enemy_group, money_callback):  # Lógica do projétil de canhão (movimento em linha reta dano em área)
        try:
            direction = (self.target_pos - self.pos).normalize()
        except ValueError:
            direction = pygame.math.Vector2(0, 0)

        self.pos += direction * self.speed
        self.rect.center = self.pos

        # Checar se chegou ao destino
        if (self.target_pos - self.pos).length_squared() < self.speed**2:
            self.explode(enemy_group, money_callback)
            self.kill()

    def explode(self, enemy_group, money_callback):  # aplica o dano em área
        if sfx_explosion:
            sfx_explosion.play()
        for enemy in enemy_group:
            dist_sq = (enemy.pos - self.pos).length_squared()
            if dist_sq <= self.splash_radius**2:
                reward = enemy.take_damage(self.damage)
                money_callback(reward)


class Button:  # Classe para os botões de construção na UI.
    def __init__(self, x, y, width, height, image, cost):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.transform.scale(image, (width - 10, height - 10))  # Reduz para caber
        self.cost = cost
        self.is_hovered = False

    def draw(self, surface, money):
        # Cor de fundo baseada no estado
        if self.is_hovered and money >= self.cost:
            bg_color = GREEN
        elif self.is_hovered:
            bg_color = RED  # Hover, mas sem dinheiro
        elif money < self.cost:
            bg_color = GREY  # Sem dinheiro
        else:
            bg_color = BLACK  # Normal

        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # Borda

        # Centraliza a imagem
        img_rect = self.image.get_rect(center=self.rect.center)
        surface.blit(self.image, img_rect)

        # Desenha o custo
        draw_text(
            f"${self.cost}",
            font_small,
            WHITE,
            surface,
            self.rect.centerx,
            self.rect.bottom - 10,
            center=True,
        )

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


# =============================================================================
# 3. FUNÇÕES AUXILIARES
# =============================================================================


def draw_text(text, font, color, surface, x, y, center=False, v_center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    elif v_center:
        # Alinha à esquerda em X, mas centraliza verticalmente em Y
        text_rect.left = x
        text_rect.centery = y
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def draw_ui(surface, lives, money, wave, total_waves, buttons):  # Desenha a UI  na parte inferior.
    panel_rect = pygame.Rect(0, GAME_HEIGHT, SCREEN_WIDTH, UI_PANEL_HEIGHT)
    pygame.draw.rect(surface, BLACK, panel_rect)
    pygame.draw.rect(surface, WHITE, panel_rect, 2)  # Borda

    # Stats
    draw_text(f"Vidas: {lives}", font_medium, WHITE, surface, 20, GAME_HEIGHT + 10)
    draw_text(f"Dinheiro: ${money}", font_medium, WHITE, surface, 20, GAME_HEIGHT + 50)
    draw_text(
        f"Onda: {wave} / {total_waves}",
        font_medium,
        WHITE,
        surface,
        SCREEN_WIDTH - 200,
        GAME_HEIGHT + 35,
    )

    # Botoes
    for key, button in buttons.items():
        button.draw(surface, money)


def draw_upgrade_menu(surface, tower, money):
    panel_rect = pygame.Rect(0, GAME_HEIGHT, SCREEN_WIDTH, UI_PANEL_HEIGHT)
    pygame.draw.rect(surface, (40, 40, 50), panel_rect)
    pygame.draw.rect(surface, WHITE, panel_rect, 2)

    # Informações da Torre
    info_text = f"Torre: {tower.tower_type.upper()} | Dano: {tower.damage} | Delay: {tower.fire_rate}ms"
    draw_text(info_text, font_medium, WHITE, surface, 20, GAME_HEIGHT + 10)

    # Custos
    cost_dmg = tower.get_upgrade_cost("damage")
    cost_spd = tower.get_upgrade_cost("speed")
    refund = int(tower.data["cost"] * 0.75)

    # Definição dos Botões (Rects)
    # Botão Dano
    btn_dmg = pygame.Rect(400, GAME_HEIGHT + 40, 200, 40)
    color_dmg = GREEN if money >= cost_dmg else GREY
    pygame.draw.rect(surface, color_dmg, btn_dmg)
    draw_text(f"UP Dano (-${cost_dmg})", font_small, BLACK, surface, btn_dmg.centerx, btn_dmg.centery, center=True)

    # Botão Velocidade
    btn_spd = pygame.Rect(620, GAME_HEIGHT + 40, 200, 40)
    color_spd = ORANGE if money >= cost_spd else GREY
    pygame.draw.rect(surface, color_spd, btn_spd)
    draw_text(f"UP Rapidez (-${cost_spd})", font_small, BLACK, surface, btn_spd.centerx, btn_spd.centery, center=True)

    # Botão Vender
    btn_sell = pygame.Rect(840, GAME_HEIGHT + 40, 200, 40)
    pygame.draw.rect(surface, RED, btn_sell)
    draw_text(f"Vender (+${refund})", font_small, WHITE, surface, btn_sell.centerx, btn_sell.centery, center=True)

    draw_text("Pressione ESC para cancelar seleção", font_small, WHITE, surface, SCREEN_WIDTH - 250, GAME_HEIGHT + 10)

    return btn_dmg, btn_spd, btn_sell


def draw_tower_slots(surface, selected_tower_type):  # pega as coordenadas dos slots que podem ser construidos e desenha eles
    for i, rect in enumerate(TORRE_SLOT_RECTS):
        # Só desenha slots vazios
        if i not in occupied_slots:
            # Se estiver construindo, mostra um círculo verde
            if selected_tower_type:
                pygame.draw.circle(surface, GREEN, rect.center, 24, 3)
            # Senão, um círculo cinza sutil
            else:
                pygame.draw.circle(surface, (50, 50, 50), rect.center, 24, 2)


def draw_tower_preview(surface, mouse_pos, tower_type):  # Desenha o preview da torre no mouse
    if not tower_type:
        return

    data = TOWER_DATA[tower_type]
    image = data["image"]
    range_val = data["range"]

    # Desenha o alcance
    range_surface = pygame.Surface((range_val * 2, range_val * 2), pygame.SRCALPHA)
    pygame.draw.circle(range_surface, (255, 255, 255, 50), (range_val, range_val), range_val)
    surface.blit(range_surface, (mouse_pos[0] - range_val, mouse_pos[1] - range_val))

    # Desenha a torre
    surface.blit(
        image,
        (mouse_pos[0] - image.get_width() // 2, mouse_pos[1] - image.get_height() // 2),
    )


# =============================================================================
# 4. LOOP PRINCIPAL (Máquina de Estados)
# =============================================================================


def run_transition(screen, clock):
    duration_flash = 100
    duration_fade = 1000

    flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    flash_surface.fill(WHITE)

    fade_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade_surface.fill(BLACK)

    if sfx_build:
        sfx_build.play()

    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < duration_flash:
        # Calcula alfa (transparência) decrescente
        elapsed = pygame.time.get_ticks() - start_time
        alpha = 255 - int((elapsed / duration_flash) * 255)
        flash_surface.set_alpha(alpha)

        screen.blit(flash_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    for alpha in range(0, 260, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.time.wait(200)


def main(screen, clock, cheats_enabled):  # Função principal do jogo
    running = True
    game_state = "START_MENU"

    # Variáveis do Jogo
    lives = INITIAL_LIVES
    money = INITIAL_MONEY
    wave = 0
    total_waves = len(WAVE_DEFINITIONS)

    # Variável para controlar a música atual
    current_music = None

    # --- LÓGICA DE CHEAT E SELEÇÃO DE MÚSICA ---
    if cheats_enabled:
        money = 99999
        lives = 99
        TOWER_DATA["arrow"]["fire_rate"] = 100
        TOWER_DATA["cannon"]["fire_rate"] = 500
        TOWER_DATA["arrow"]["damage"] = 100
        TOWER_DATA["cannon"]["damage"] = 200
        current_music = ost_cheats
    else:
        # Garante que os valores voltem ao normal
        TOWER_DATA["arrow"]["fire_rate"] = 1000
        TOWER_DATA["cannon"]["fire_rate"] = 2000
        TOWER_DATA["arrow"]["damage"] = 25
        TOWER_DATA["cannon"]["damage"] = 50
        current_music = ost_normal

    # Toca a música selecionada
    if current_music:
        current_music.set_volume(0.1)
        current_music.play(loops=-1)

    # Grupos dos sprites
    enemy_group = pygame.sprite.Group()
    tower_group = pygame.sprite.Group()
    projectile_group = pygame.sprite.Group()

    # Variáveis de controle
    selected_tower_type = None
    occupied_slots.clear()

    # UI
    buttons = {
        "arrow": Button(300, GAME_HEIGHT + 10, 80, 80, TOWER_DATA["arrow"]["image"], TOWER_DATA["arrow"]["cost"]),
        "cannon": Button(400, GAME_HEIGHT + 10, 80, 80, TOWER_DATA["cannon"]["image"], TOWER_DATA["cannon"]["cost"]),
    }

    # Controle de waves
    wave_in_progress = False
    wave_spawn_list = []
    last_spawn_time = 0
    spawn_delay = 1000

    def add_money(amount):
        nonlocal money
        money += amount

    # Variável nova para controlar a torre selecionada
    selected_tower_instance = None

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                if current_music:
                    current_music.stop()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Cancela tudo
                    selected_tower_type = None
                    selected_tower_instance = None
                    # Se pressionar ESC de novo, sai do jogo (opcional, mantendo lógica original)
                    if not selected_tower_instance and not selected_tower_type:
                        running = False
                        if current_music:
                            current_music.stop()

            if game_state == "START_MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    run_transition(screen, clock)
                    game_state = "PLAYING"
                    wave = 0

            elif game_state == "PLAYING":
                if event.type == pygame.USEREVENT and getattr(event, "tipo", "") == "enemy_leaked":
                    if not cheats_enabled:
                        lives -= 1
                        if sfx_life_lost:
                            sfx_life_lost.play()
                        if lives <= 0:
                            game_state = "GAME_OVER"
                            if current_music:
                                current_music.stop()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clicked_interface = False

                    # 1. Se uma torre JÁ estiver selecionada, checa cliques no menu de upgrade
                    if selected_tower_instance:
                        # Recalcula os rects dos botões (mesma lógica do draw) para checar colisão
                        # (Idealmente seria uma classe, mas faremos direto aqui pela simplicidade)
                        btn_dmg = pygame.Rect(400, GAME_HEIGHT + 40, 200, 40)
                        btn_spd = pygame.Rect(620, GAME_HEIGHT + 40, 200, 40)
                        btn_sell = pygame.Rect(840, GAME_HEIGHT + 40, 200, 40)

                        # Lógica UPGRADE DANO
                        if btn_dmg.collidepoint(mouse_pos):
                            cost = selected_tower_instance.get_upgrade_cost("damage")
                            if money >= cost:
                                money -= cost
                                selected_tower_instance.upgrade_damage()
                            clicked_interface = True

                        # Lógica UPGRADE VELOCIDADE
                        elif btn_spd.collidepoint(mouse_pos):
                            cost = selected_tower_instance.get_upgrade_cost("speed")
                            if money >= cost:
                                money -= cost
                                selected_tower_instance.upgrade_speed()
                            clicked_interface = True

                        # Lógica VENDER
                        elif btn_sell.collidepoint(mouse_pos):
                            refund = int(selected_tower_instance.data["cost"] * 0.75)
                            add_money(refund)
                            # Liberar slot
                            for i, rect in enumerate(TORRE_SLOT_RECTS):
                                if rect.center == selected_tower_instance.rect.center:
                                    if i in occupied_slots:
                                        occupied_slots.remove(i)
                                    break
                            selected_tower_instance.kill()
                            selected_tower_instance = None
                            if sfx_build:
                                sfx_build.play()
                            clicked_interface = True

                    # 2. Se não clicou na interface de upgrade, tenta selecionar torre ou botão de build
                    if not clicked_interface:
                        # Verifica clique nos botões de construção (se NENHUMA torre selecionada)
                        if not selected_tower_instance:
                            for tower_type, button in buttons.items():
                                if button.is_clicked(mouse_pos):
                                    if money >= button.cost:
                                        selected_tower_type = tower_type
                                        selected_tower_instance = None  # Garante que desseleciona torre
                                    clicked_interface = True
                                    break

                        # Verifica clique no Mapa
                        if not clicked_interface:
                            # Tenta SELECIONAR uma torre existente
                            clicked_on_tower = False
                            for tower in tower_group:
                                if tower.rect.collidepoint(mouse_pos):
                                    selected_tower_instance = tower
                                    selected_tower_type = None  # Para de construir
                                    clicked_on_tower = True
                                    break

                            # Se não clicou em torre, tenta CONSTRUIR (se tiver tipo selecionado)
                            if not clicked_on_tower:
                                selected_tower_instance = None  # Clicar no vazio desseleciona a torre atual
                                if selected_tower_type:
                                    for i, rect in enumerate(TORRE_SLOT_RECTS):
                                        if i not in occupied_slots and rect.collidepoint(mouse_pos):
                                            cost = TOWER_DATA[selected_tower_type]["cost"]
                                            if money >= cost:
                                                money -= cost
                                                new_tower = Tower(selected_tower_type, rect.center)
                                                tower_group.add(new_tower)
                                                occupied_slots.append(i)
                                                if sfx_build:
                                                    sfx_build.play()
                                                selected_tower_type = None
                                            break

            elif game_state in ["GAME_OVER", "WIN"]:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Reset do jogo
                        game_state = "START_MENU"
                        lives = INITIAL_LIVES
                        money = INITIAL_MONEY
                        if current_music:
                            current_music.stop()
                            current_music.play(loops=-1)
                        if cheats_enabled:
                            money = 99999
                            lives = 99
                        wave = 0
                        enemy_group.empty()
                        tower_group.empty()
                        projectile_group.empty()
                        occupied_slots.clear()
                        wave_in_progress = False
                        wave_spawn_list = []
                        selected_tower_instance = None  # Reset seleção

                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        if current_music:
                            current_music.stop()

        if game_state == "PLAYING":
            for button in buttons.values():
                button.check_hover(mouse_pos)

            enemy_group.update()
            tower_group.update(enemy_group, projectile_group)
            projectile_group.update(enemy_group, add_money)

            # Lógica de Waves
            if not wave_in_progress and not enemy_group:
                if wave < total_waves:
                    wave += 1
                    wave_in_progress = True
                    wave_spawn_list = []
                    current_wave_data = WAVE_DEFINITIONS[wave - 1]
                    for enemy_type, count in current_wave_data.items():
                        wave_spawn_list.extend([enemy_type] * count)
                    random.shuffle(wave_spawn_list)
                    last_spawn_time = pygame.time.get_ticks()
                else:
                    game_state = "WIN"
                    if current_music:
                        current_music.stop()

            if wave_in_progress:
                now = pygame.time.get_ticks()
                if wave_spawn_list and now - last_spawn_time >= spawn_delay:
                    enemy_type_to_spawn = wave_spawn_list.pop(0)
                    new_enemy = Enemy(enemy_type_to_spawn, WAYPOINTS)
                    enemy_group.add(new_enemy)
                    last_spawn_time = now
                if not wave_spawn_list:
                    wave_in_progress = False

        screen.fill(BLACK)

        if game_state == "START_MENU":
            screen.blit(background_image, (0, 0))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            draw_text("TOWER DEFENSE", font_large, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, center=True)
            draw_text("Pressione [ESPAÇO] para começar", font_medium, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, center=True)
            draw_text("Pressione [ESC] para voltar ao Hub", font_small, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, center=True)

        elif game_state == "PLAYING":
            screen.blit(background_image, (0, 0))
            draw_tower_slots(screen, selected_tower_type)

            # Se uma torre estiver selecionada, desenha o alcance dela
            if selected_tower_instance:
                selected_tower_instance.draw_range(screen)
                # Destaque visual na torre selecionada (borda amarela)
                pygame.draw.circle(screen, (255, 255, 0), selected_tower_instance.rect.center, 30, 2)

            enemy_group.draw(screen)
            tower_group.draw(screen)
            projectile_group.draw(screen)

            for enemy in enemy_group:
                enemy.draw_health_bar(screen)

            if mouse_pos and selected_tower_type:
                draw_tower_preview(screen, mouse_pos, selected_tower_type)

            # Lógica de qual UI desenhar
            if selected_tower_instance:
                draw_upgrade_menu(screen, selected_tower_instance, money)
            else:
                draw_ui(screen, lives, money, wave, total_waves, buttons)

            if cheats_enabled:
                draw_text("CHEATS ATIVADOS", font_small, GREEN, screen, SCREEN_WIDTH - 100, 20, center=True)

        elif game_state == "GAME_OVER":
            screen.blit(background_image, (0, 0))
            draw_text("GAME OVER", font_large, RED, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, center=True)
            draw_text(f"Você sobreviveu {wave-1} ondas", font_medium, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, center=True)
            draw_text("Pressione [ESPAÇO] para reiniciar", font_medium, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, center=True)

        elif game_state == "WIN":
            screen.blit(background_image, (0, 0))
            draw_text("VITÓRIA!", font_large, GREEN, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, center=True)
            draw_text("Você defendeu todas as ondas!", font_medium, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, center=True)
            draw_text("Pressione [ESPAÇO] para reiniciar", font_medium, WHITE, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60, center=True)

        pygame.display.flip()

    return 100000 if cheats_enabled else (wave - 1) * 100
