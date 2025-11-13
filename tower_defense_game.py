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


def load_image(filename, placeholder_size, placeholder_color):  # Função que carrega cada imagem, se falha, cria um placeholder
    try:
        return pygame.image.load(IMAGES_DIR / filename).convert_alpha()  # convert alpha para manter transparência caso seja png
    except (
        pygame.error,
        FileNotFoundError,
    ):  # Captura erro da biblioteca nao achar o arquivo e FileNotFoundError também
        print(f"AVISO: Imagem '{filename}' não encontrada. Criando placeholder padrão.")  # Aviso no console
        return create_placeholder_surface(placeholder_size[0], placeholder_size[1], placeholder_color)  # chama a função que cria o placeholder


def load_sound(
    filename,
):  # Tenta carregar um som, se falhar, retorna um objeto vazio do tipo 'none'
    try:
        # CONVERTE O PATH PARA UMA STRING (erro de depreciated)
        return pygame.mixer.Sound(str(SOUNDS_DIR / filename))
    except pygame.error:
        print(f"AVISO: Som '{filename}' não encontrado.")
        return None


# Carregamento em si das midias
try:
    # fundo do jogo
    background_image = pygame.image.load(IMAGES_DIR / "map.png").convert()  # convert para lidar com o tamanho da imagem
except pygame.error as e:
    print(f"Erro CRÍTICO ao carregar 'map.png': {e}")
    print("O 'map.png' é essencial. Criando um fundo preto por padrão.")
    background_image = create_placeholder_surface(SCREEN_WIDTH, GAME_HEIGHT, BLACK)

# Sprites (Carregados dentro das classes, mas são definidos previamente)
soldier_sprite = load_image("soldier_sprite.png", (32, 32), BLUE)  # load_image retorna um objeto Surface que é carregado para cada classe
tank_sprite = load_image("tank.png", (40, 40), GREY)  #

arrow_tower_sprite = load_image("arrow_tower.png", (48, 48), GREEN)
cannon_tower_sprite = load_image("cannon_tower.png", (48, 48), RED)
arrow_projectile_sprite = load_image("arrow_projectile.png", (10, 10), WHITE)
cannon_projectile_sprite = load_image("cannon_projectile.png", (15, 15), ORANGE)

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

sfx_arrow_fire = load_sound("arrow_fire.wav")
sfx_cannon_fire = load_sound("cannon_fire.wav")
sfx_enemy_death = load_sound("enemy_death.wav")
sfx_life_lost = load_sound("life_lost.wav")
sfx_build = load_sound("build.wav")

background_music = load_sound("background_music.mp3")
if background_music:  # diminue o volume da musica de fundo quando ela é carregada, if necessario para evitar erro caso o som nao seja carregado(por nao existir ou etc)
    background_music.set_volume(0.3)


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


class Enemy(pygame.sprite.Sprite):  # classe para os inimigos
    def __init__(self, enemy_type, path):
        super().__init__()  # inicializa a classe super sprite do pygame

        self.path = path
        self.waypoint_index = 0  # comeca no waypoint 0
        self.pos = pygame.math.Vector2(self.path[self.waypoint_index])  # .math cria um vetor pra calcular os movimentos

        # Atributos dos inimigos baseados no tipo
        if enemy_type == "soldier":
            self.image = soldier_sprite
            self.speed = 2
            self.max_health = 100
            self.reward = 10
        elif enemy_type == "tank":
            self.image = tank_sprite
            self.speed = 1
            self.max_health = 300
            self.reward = 25

        self.health = self.max_health  # seta a vida maxima
        self.rect = self.image.get_rect(center=self.pos)  # seta o rect para colisao e desenho, centralizado tambem

    def update(self):

        # Sobrescreve o update() padrão do pygame.sprite.Sprite
        # Esta função é chamada automaticamente pelo enemy_group.update() no loop principal.
        # Lógica de movimento do inimigo em direção ao próximo waypoint
        target_waypoint = self.path[self.waypoint_index]
        target_vector = pygame.math.Vector2(target_waypoint)

        try:
            direction = (target_vector - self.pos).normalize()
        except ValueError:  # Ocorre se a posição e o alvo forem os mesmos
            direction = pygame.math.Vector2(0, 0)  # Chegou

        self.pos += direction * self.speed
        self.rect.center = self.pos

        if (target_vector - self.pos).length_squared() < self.speed**2:
            self.waypoint_index += 1
            # 5. Checar se terminou o caminho
            if self.waypoint_index >= len(self.path):  # se o inimigo chegou ao final do caminho (fora da tela)
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"tipo": "enemy_leaked"}))
                self.kill()  # remove o inimigo

    def take_damage(self, amount):  # Aplica dano ao inimigo e retorna a recompensa(dinheiro) se morrer.
        self.health -= amount
        if self.health <= 0:
            self.kill()  # Remove o sprite do jogo
            if sfx_enemy_death:  # toca o som de morte se ele existir (mesma verificação anterior)
                sfx_enemy_death.play()
            return self.reward  # retorna a recompensa ja definida na criação do inimigo
        return 0  # Retorna 0 de recompensa (reward) se o inimigo só tomou dano mas não morreu.

    def draw_health_bar(self, surface):  # Desenha a barra de vida acima do inimigo.
        if self.health < self.max_health:
            bar_width = self.rect.width * 0.8  # deixa menor q o inimigo
            bar_height = 5
            health_ratio = self.health / self.max_health  # define a proporcao

            bg_rect = pygame.Rect(
                self.rect.centerx - bar_width / 2,
                self.rect.top - 10,
                bar_width,
                bar_height,
            )  # barra total
            pygame.draw.rect(surface, RED, bg_rect)  # desenha a barra

            hp_rect = pygame.Rect(
                self.rect.centerx - bar_width / 2,
                self.rect.top - 10,
                bar_width * health_ratio,
                bar_height,
            )  # barra de vida atual
            pygame.draw.rect(surface, GREEN, hp_rect)  # desenha a barra


class Tower(pygame.sprite.Sprite):  # Classe para as torres de defesa.
    def __init__(self, tower_type, pos):
        super().__init__()

        self.pos = pygame.math.Vector2(pos)
        self.tower_type = tower_type
        self.data = TOWER_DATA[tower_type]  # Usa o TOWER_DATA global (que pode estar modificado)

        self.image = self.data["image"]
        self.range = self.data["range"]
        self.fire_rate = self.data["fire_rate"]
        self.damage = self.data["damage"]

        self.rect = self.image.get_rect(center=self.pos)
        self.last_shot_time = pygame.time.get_ticks()
        self.target = None

    def update(self, enemy_group, projectile_group):  # Encontra um alvo e atira.
        self.find_target(enemy_group)

        if self.target:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time >= self.fire_rate:
                self.shoot(projectile_group)
                self.last_shot_time = now

    def find_target(self, enemy_group):  # Encontra o inimigo mais próximo dentro do alcance usando loop
        if self.target and (not self.target.alive() or (self.target.pos - self.pos).length() > self.range):  # verifica se esta vivo e no range
            self.target = None  # retorna nulo se nao estiver mais valido

        if not self.target:  # se nao tiver alvo procura um novo
            closest_dist_sq = self.range**2  # usa o quadrado do alcance pq com raiz pode dar erro
            for enemy in enemy_group:  # para cada inimigo calcula a distancia em x e em y usando pitagoras
                dist_sq = (enemy.pos - self.pos).length_squared()
                if dist_sq <= closest_dist_sq:  # se a distancia estiver dentro do alcance
                    closest_dist_sq = dist_sq
                    self.target = enemy  # define o inimigo como alvo

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
        if not self.target or not self.target.alive():
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


def main(screen, clock, cheats_enabled):  # Função principal do jogo
    running = True
    game_state = "START_MENU"  # Pula o LOGIN, o hub já fez isso

    # Variáveis do Jogo
    lives = INITIAL_LIVES
    money = INITIAL_MONEY
    wave = 0
    total_waves = len(WAVE_DEFINITIONS)

    # --- LÓGICA DE CHEAT ---
    if cheats_enabled:
        money = 99999
        lives = 99
        # Modifica permanentemente (para esta sessão) os stats da torre
        TOWER_DATA["arrow"]["fire_rate"] = 100
        TOWER_DATA["cannon"]["fire_rate"] = 500
        TOWER_DATA["arrow"]["damage"] = 100
        TOWER_DATA["cannon"]["damage"] = 200
    else:
        # Garante que os valores voltem ao normal se o cheat for desativado no hub
        TOWER_DATA["arrow"]["fire_rate"] = 1000
        TOWER_DATA["cannon"]["fire_rate"] = 2000
        TOWER_DATA["arrow"]["damage"] = 25
        TOWER_DATA["cannon"]["damage"] = 50
    # --- FIM DA LÓGICA DE CHEAT ---

    # Grupos dos sprites
    enemy_group = pygame.sprite.Group()
    tower_group = pygame.sprite.Group()
    projectile_group = pygame.sprite.Group()

    # Variáveis de controle
    selected_tower_type = None  # zera a torre selecionada
    occupied_slots.clear()  # Limpa todos os slots ocupados no reinício

    # UI
    buttons = {
        "arrow": Button(
            300,
            GAME_HEIGHT + 10,
            80,
            80,
            TOWER_DATA["arrow"]["image"],
            TOWER_DATA["arrow"]["cost"],
        ),
        "cannon": Button(
            400,
            GAME_HEIGHT + 10,
            80,
            80,
            TOWER_DATA["cannon"]["image"],
            TOWER_DATA["cannon"]["cost"],
        ),
    }

    # Controle de waves
    wave_in_progress = False
    wave_spawn_list = []
    last_spawn_time = 0
    spawn_delay = 1000  # 1 segundo entre inimigos

    # Callback para projéteis adicionarem dinheiro
    def add_money(amount):
        nonlocal money
        money += amount

    if background_music:
        background_music.play(loops=-1)

    while running:
        # --- 6.1. Controle de FPS ---
        clock.tick(FPS)

        mouse_pos = pygame.mouse.get_pos()

        # --- 6.2. Processamento dos eventos ---
        events = pygame.event.get()  # Pega todos os eventos do jogo usando o modulo importado do pygame
        for event in events:  # para cada evento na lista de eventos
            if event.type == pygame.QUIT:  # se for o evento de fechar a janela
                running = False
                if background_music:
                    background_music.stop()  # Para a música ao sair

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selected_tower_type = None  # Cancela construção
                    running = False  # Sai para o menu do hub
                    if background_music:
                        background_music.stop()

            # --- Eventos por Estado ---

            if game_state == "START_MENU":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:  # se apertar espaço
                    game_state = "PLAYING"  # muda o estado para jogando
                    wave = 0  # Reseta a onda para 0 para forçar o início da onda 1

            elif game_state == "PLAYING":  # se estiver jogando
                if event.type == pygame.USEREVENT and event.tipo == "enemy_leaked":
                    # --- LÓGICA DE CHEAT ---
                    if not cheats_enabled:  # Só perde vida se o cheat estiver desligado
                        lives -= 1
                        if sfx_life_lost:
                            sfx_life_lost.play()
                        if lives <= 0:
                            game_state = "GAME_OVER"
                            if background_music:
                                background_music.stop()
                    # --- FIM DA LÓGICA DE CHEAT ---

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    clicked_button = False
                    for tower_type, button in buttons.items():
                        if button.is_clicked(mouse_pos):
                            if money >= button.cost:
                                selected_tower_type = tower_type
                                print(f"Modo de construção: {tower_type}")
                            else:
                                print("Dinheiro insuficiente.")
                            clicked_button = True
                            break

                    # 2. Se não clicou na UI e está construindo, clicou em um slot?
                    if not clicked_button and selected_tower_type:
                        for i, rect in enumerate(TORRE_SLOT_RECTS):
                            if i not in occupied_slots and rect.collidepoint(mouse_pos):
                                # Construir a torre
                                cost = TOWER_DATA[selected_tower_type]["cost"]
                                if money >= cost:
                                    money -= cost
                                    new_tower = Tower(selected_tower_type, rect.center)
                                    tower_group.add(new_tower)
                                    occupied_slots.append(i)
                                    if sfx_build:
                                        sfx_build.play()
                                    print(f"Torre {selected_tower_type} construída no slot {i}")
                                    selected_tower_type = None  # Sai do modo de construção
                                else:
                                    print("Dinheiro insuficiente.")
                                break

            elif game_state == "GAME_OVER" or game_state == "WIN":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Reinicia o jogo
                        game_state = "START_MENU"
                        lives = INITIAL_LIVES
                        money = INITIAL_MONEY

                        # --- LÓGICA DE CHEAT ---
                        if cheats_enabled:
                            money = 99999
                            lives = 99
                        # --- FIM DA LÓGICA DE CHEAT ---

                        wave = 0
                        enemy_group.empty()
                        tower_group.empty()
                        projectile_group.empty()
                        occupied_slots.clear()
                        wave_in_progress = False
                        wave_spawn_list = []
                        if background_music:
                            background_music.play(loops=-1)
                    elif event.key == pygame.K_ESCAPE:
                        running = False  # Sai para o menu do hub
                        if background_music:
                            background_music.stop()

        if game_state == "PLAYING":
            for button in buttons.values():
                button.check_hover(mouse_pos)

            # Atualiza Sprites
            enemy_group.update()
            tower_group.update(enemy_group, projectile_group)
            projectile_group.update(enemy_group, add_money)  # Passa inimigos e callback

            # Lógica das ondas
            if not wave_in_progress and not enemy_group:  # garante que só comece nova wave se a anterior acabou
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
                    # ganho o jogo
                    game_state = "WIN"
                    if background_music:
                        background_music.stop()  # para a musica de fundo (funciona pois 	ela é carregada como objeto Sound)

            if wave_in_progress:
                now = pygame.time.get_ticks()  # pega o tempo atual
                if wave_spawn_list and now - last_spawn_time >= spawn_delay:  # se tiver waves para acontecer e tempo desde o ultimo spawn for maior q o delay , spawna um inimigo
                    enemy_type_to_spawn = wave_spawn_list.pop(0)  # tira 1 inimigo
                    new_enemy = Enemy(enemy_type_to_spawn, WAYPOINTS)  # "cria"o inimigo
                    enemy_group.add(new_enemy)  # adiciona ao grupo de inimigos
                    last_spawn_time = now  # reseta o delay

                if not wave_spawn_list:
                    wave_in_progress = False  # garante q nao gere 2 waves juntas

        screen.fill(BLACK)

        if game_state == "START_MENU":  # landing page
            screen.blit(background_image, (0, 0))  # desenha fundo em 0,0
            draw_text(
                "TOWER DEFENSE",
                font_large,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                center=True,
            )  # nome do jogo
            draw_text(
                "Pressione [ESPAÇO] para começar",
                font_medium,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 20,
                center=True,
            )  # clicar para começar
            draw_text(
                "Pressione [ESC] para voltar ao Hub",
                font_small,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 60,
                center=True,
            )

        elif game_state == "PLAYING":  # após clicar espaco
            screen.blit(background_image, (0, 0))  # desenha fundo em 0,0
            draw_tower_slots(screen, selected_tower_type)  # desenha onde pode construir, chama a funcao q recebe as coordenadas como parametro

            enemy_group.draw(screen)  # desenha os inimigos a cada clock
            tower_group.draw(screen)  # desenha as torres a cada clock
            projectile_group.draw(screen)  # desenha os projeteis a cada clock

            for enemy in enemy_group:
                enemy.draw_health_bar(screen)

            if mouse_pos:  # Garante que mouse_pos não é None
                draw_tower_preview(screen, mouse_pos, selected_tower_type)  # desenha preview de construção onde o mouse está

            draw_ui(screen, lives, money, wave, total_waves, buttons)  # desenha a tela e a parte inferior

            if cheats_enabled:
                draw_text("CHEATS ATIVADOS", font_small, GREEN, screen, SCREEN_WIDTH - 100, 20, center=True)

        elif game_state == "GAME_OVER":  # estado derrota
            screen.blit(background_image, (0, 0))  # desenha fundo em 0,0
            draw_text(
                "GAME OVER",
                font_large,
                RED,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                center=True,
            )  #
            draw_text(
                f"Você sobreviveu {wave-1} ondas",
                font_medium,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 20,
                center=True,
            )
            draw_text(
                "Pressione [ESPAÇO] para reiniciar",
                font_medium,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 60,
                center=True,
            )

        elif game_state == "WIN":  # estado vitoria
            screen.blit(background_image, (0, 0))  # desenha fundo em 0,0
            draw_text(
                "VITÓRIA!",
                font_large,
                GREEN,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 - 50,
                center=True,
            )
            draw_text(
                "Você defendeu todas as ondas!",
                font_medium,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 20,
                center=True,
            )
            draw_text(
                "Pressione [ESPAÇO] para reiniciar",
                font_medium,
                WHITE,
                screen,
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2 + 60,
                center=True,
            )

        pygame.display.flip()  # Update da tela
