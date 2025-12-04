import pygame
import sys
import math
import random

# --- Funções Utilitárias ---


def format_number(n):
    """Formata números grandes (Ex: 1.5M, 3.2B)"""
    n = int(n)
    if n < 1000:
        return str(n)
    units = ["", "k", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc"]
    magnitude = 0
    while abs(n) >= 1000:
        n /= 1000.0
        magnitude += 1
    if magnitude > 0:
        return f"{n:.2f}".rstrip("0").rstrip(".") + units[magnitude]
    return str(int(n))


def calculate_bulk_cost(base_cost, current_count, amount):
    """Calcula custo cumulativo para compras em massa"""
    price_of_next = base_cost * (1.15**current_count)
    if amount == 1:
        return math.ceil(price_of_next)
    ratio = 1.15
    total_cost = price_of_next * ((ratio**amount) - 1) / (ratio - 1)
    return math.ceil(total_cost)


def draw_gradient_rect(surface, color_top, color_bottom, rect):
    """Desenha um gradiente vertical"""
    fill_rect = pygame.Rect(rect)
    color_rect = pygame.Surface((2, 2))
    pygame.draw.line(color_rect, color_top, (0, 0), (1, 0))
    pygame.draw.line(color_rect, color_bottom, (0, 1), (1, 1))
    color_rect = pygame.transform.smoothscale(color_rect, (fill_rect.width, fill_rect.height))
    surface.blit(color_rect, fill_rect)


# --- Classes Visuais ---


class Particle:
    """Migalhas que caem ao clicar no cookie"""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.3
        self.size = random.randint(4, 8)
        self.color = color
        self.life = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 8
        self.size -= 0.1

    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, max(0, int(self.life))), (int(self.size), int(self.size)), int(self.size))
            surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class FloatingText:
    """Texto que sobe e desaparece (+1, +100, Frenzy!)"""

    def __init__(self, text, pos, font, color=(255, 255, 255)):
        self.text = text
        self.pos = list(pos)
        self.color = color
        self.font = font
        self.life = 255
        self.y_offset = 0

    def update(self):
        self.y_offset -= 1.5  # Sobe
        self.life -= 3  # Desaparece

    def draw(self, surface):
        if self.life > 0:
            # Renderiza com Alpha
            text_surf = self.font.render(self.text, True, self.color)
            alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, max(0, int(self.life))))

            # Blit especial para alpha em texto
            text_surf.set_alpha(max(0, int(self.life)))
            surface.blit(text_surf, (self.pos[0] - text_surf.get_width() // 2, self.pos[1] + self.y_offset))


class AchievementToast:
    """Notificação deslizante de conquista"""

    def __init__(self, name, desc, font_title, font_desc, width):
        self.name = name
        self.desc = desc
        self.rect = pygame.Rect(width // 2 - 150, -80, 300, 70)
        self.target_y = 20
        self.timer = 180  # quadros (3 segundos a 60fps)
        self.state = "entering"
        self.font_title = font_title
        self.font_desc = font_desc

    def update(self):
        if self.state == "entering":
            self.rect.y += 4
            if self.rect.y >= self.target_y:
                self.rect.y = self.target_y
                self.state = "stay"
        elif self.state == "stay":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "leaving"
        elif self.state == "leaving":
            self.rect.y -= 4

    def draw(self, surface):
        # Fundo e Borda
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (40, 40, 50, 240), s.get_rect(), border_radius=10)
        pygame.draw.rect(s, (255, 215, 0), s.get_rect(), 2, border_radius=10)
        surface.blit(s, self.rect.topleft)

        # Texto
        title_surf = self.font_title.render("CONQUISTA!", True, (255, 215, 0))
        name_surf = self.font_desc.render(self.name, True, (255, 255, 255))

        surface.blit(title_surf, (self.rect.centerx - title_surf.get_width() // 2, self.rect.top + 10))
        surface.blit(name_surf, (self.rect.centerx - name_surf.get_width() // 2, self.rect.bottom - 25))

        return self.state == "leaving" and self.rect.bottom < 0


class GoldenCookie:
    def __init__(self, width, height, font):
        self.rect = pygame.Rect(0, 0, 80, 80)
        self.WIDTH = width
        self.HEIGHT = height
        self.font = font
        self.reset()
        self.pulse_val = 0

    def reset(self):
        x = random.randint(self.WIDTH // 10, self.WIDTH // 2 - 100)
        y = random.randint(50, self.HEIGHT - 100)
        self.rect.center = (x, y)
        self.active = False
        self.life = 60 * random.randint(10, 20)
        self.spawn_timer = 60 * random.randint(30, 90)  # Entre 30s e 90s
        self.bonus_value = 0
        self.type = "cookies"

    def activate(self, current_cookies, current_cps):
        if random.random() < 0.7:
            # Bônus de cookies: 15% do banco ou 10 mins de CpS
            self.bonus_value = max(current_cps * 600, current_cookies * 0.15)
            # Cap mínimo
            if self.bonus_value < 100:
                self.bonus_value = 100
            self.type = "cookies"
        else:
            self.type = "frenzy"
        self.active = True

    def update(self, current_cookies, current_cps):
        self.pulse_val += 0.1
        if self.active:
            self.life -= 1
            if self.life <= 0:
                self.reset()
        else:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self.activate(current_cookies, current_cps)

    def draw(self, surface):
        if self.active:
            scale = 1.0 + 0.1 * math.sin(self.pulse_val)
            radius = int(35 * scale)

            # Glow
            glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 215, 0, 50), (radius * 2, radius * 2), radius + 10)
            surface.blit(glow, (self.rect.centerx - radius * 2, self.rect.centery - radius * 2))

            # Corpo Dourado
            pygame.draw.circle(surface, (218, 165, 32), self.rect.center, radius)
            pygame.draw.circle(surface, (255, 223, 0), self.rect.center, radius - 4)

            # Texto "!"
            txt = self.font.render("!", True, (139, 69, 19))
            surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2))

    def check_click(self, pos):
        return self.active and self.rect.collidepoint(pos)


# --- Função Principal ---


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    FPS = 60

    # Paleta de Cores Mais Rica
    COLOR_BG_DARK = (20, 10, 10)
    COLOR_BG_LIGHT = (45, 25, 20)

    COOKIE_BASE = (205, 133, 63)
    COOKIE_SHADOW = (139, 69, 19)
    COOKIE_LIGHT = (222, 184, 135)
    CHIP_DARK = (60, 30, 10)
    CHIP_LIGHT = (100, 50, 20)

    UI_PANEL_BG = (30, 30, 35, 230)  # Com Alpha
    BTN_GREEN = (80, 180, 100)
    BTN_RED = (180, 80, 80)
    BTN_HOVER_ADD = 30

    GOLD = (255, 215, 0)
    CYAN = (50, 200, 255)
    WHITE = (240, 240, 245)
    GREY = (150, 150, 160)

    # Fontes
    try:
        font_giant = pygame.font.SysFont("Arial", 50, bold=True)
        font_large = pygame.font.SysFont("Arial", 36, bold=True)
        font_medium = pygame.font.SysFont("Arial", 26, bold=True)
        font_small = pygame.font.SysFont("Arial", 18)
        font_tiny = pygame.font.SysFont("Arial", 14, bold=True)
    except:
        font_giant = pygame.font.Font(None, 60)
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 34)
        font_small = pygame.font.Font(None, 24)
        font_tiny = pygame.font.Font(None, 18)

    # Dados do Jogo
    BUILDINGS_DATA = {
        "cursor": {"name": "Cursor", "desc": "Autoclique.", "icon": "👆", "base_cost": 15, "base_cps": 0.1, "count": 0},
        "grandma": {"name": "Vovó", "desc": "Receita caseira.", "icon": "👵", "base_cost": 100, "base_cps": 1.0, "count": 0},
        "farm": {"name": "Fazenda", "desc": "Plantação de massa.", "icon": "🚜", "base_cost": 1100, "base_cps": 8.0, "count": 0},
        "mine": {"name": "Mina", "desc": "Extração de pepitas.", "icon": "⛏️", "base_cost": 12000, "base_cps": 47.0, "count": 0},
        "factory": {"name": "Fábrica", "desc": "Produção em massa.", "icon": "🏭", "base_cost": 130000, "base_cps": 260.0, "count": 0},
        "bank": {"name": "Banco", "desc": "Juros de cookies.", "icon": "🏦", "base_cost": 1400000, "base_cps": 1400.0, "count": 0},
    }

    TECH_UPGRADES = [
        {"id": "u_click_1", "name": "Mouse de Plástico", "desc": "Cliques +1% CpS atual.", "cost": 500, "target": "click", "multiplier": 0.01, "bought": False},
        {"id": "u_cursor_1", "name": "Dedo Reforçado", "desc": "Cursores 2x eficientes.", "cost": 500, "target": "cursor", "multiplier": 2, "bought": False},
        {"id": "u_grandma_1", "name": "Rolo de Massa", "desc": "Vovós 2x eficientes.", "cost": 1000, "target": "grandma", "multiplier": 2, "bought": False},
        {"id": "u_farm_1", "name": "Adubo Doce", "desc": "Fazendas 2x eficientes.", "cost": 11000, "target": "farm", "multiplier": 2, "bought": False},
        {"id": "u_global_1", "name": "Mão Divina", "desc": "+5% CpS Global.", "cost": 1000000, "target": "global", "multiplier": 1.05, "bought": False},
    ]

    ACHIEVEMENTS = [
        {"id": "a_start", "name": "O Começo", "desc": "Asse 1 biscoito.", "condition": lambda c, b: c >= 1, "unlocked": False},
        {"id": "a_1k", "name": "Padeiro Amador", "desc": "1.000 biscoitos no banco.", "condition": lambda c, b: c >= 1000, "unlocked": False},
        {"id": "a_clicker", "name": "Exército de Dedos", "desc": "Tenha 20 Cursores.", "condition": lambda c, b: b["cursor"]["count"] >= 20, "unlocked": False},
        {"id": "a_rich", "name": "Milionário", "desc": "1 Milhão de biscoitos.", "condition": lambda c, b: c >= 1000000, "unlocked": False},
    ]

    # Estado Inicial
    cookies = 50000.0 if cheats_enabled else 0.0
    base_click_value = 1.0
    buildings = {k: v.copy() for k, v in BUILDINGS_DATA.items()}
    techs = [t.copy() for t in TECH_UPGRADES]
    achievements = [a.copy() for a in ACHIEVEMENTS]

    buy_amount = 1
    current_tab = "buildings"

    # Layout UI
    PANEL_WIDTH = 380
    PANEL_X = WIDTH - PANEL_WIDTH

    # Cookie Centro
    cookie_pos = (PANEL_X // 2, HEIGHT // 2)
    cookie_radius = 130
    cookie_scale = 1.0

    # Fundo rotativo (Sunburst)
    sunburst_surf = pygame.Surface((WIDTH * 2, WIDTH * 2), pygame.SRCALPHA)
    for i in range(0, 360, 20):
        points = [(WIDTH, WIDTH), (WIDTH + WIDTH * math.cos(math.radians(i)), WIDTH + WIDTH * math.sin(math.radians(i))), (WIDTH + WIDTH * math.cos(math.radians(i + 10)), WIDTH + WIDTH * math.sin(math.radians(i + 10)))]
        pygame.draw.polygon(sunburst_surf, (255, 255, 255, 15), points)
    sunburst_angle = 0

    # Objetos Dinâmicos
    floating_texts = []
    particles = []
    toasts = []
    golden_cookie = GoldenCookie(WIDTH, HEIGHT, font_medium)

    frenzy_multiplier = 1.0
    frenzy_timer = 0

    last_time = pygame.time.get_ticks()

    def draw_ui_panel(surface, mouse_pos):
        # Fundo do Painel com Blur/Transparência simulada
        overlay = pygame.Surface((PANEL_WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(UI_PANEL_BG)
        surface.blit(overlay, (PANEL_X, 0))

        # Linha divisória
        pygame.draw.line(surface, (255, 255, 255, 50), (PANEL_X, 0), (PANEL_X, HEIGHT), 2)

        # Tabs
        btn_w = PANEL_WIDTH // 2 - 10
        rect_b = pygame.Rect(PANEL_X + 5, 10, btn_w, 45)
        rect_u = pygame.Rect(PANEL_X + 5 + btn_w + 10, 10, btn_w, 45)

        col_b = (80, 80, 90) if current_tab != "buildings" else (60, 100, 160)
        col_u = (80, 80, 90) if current_tab != "upgrades" else (60, 100, 160)

        pygame.draw.rect(surface, col_b, rect_b, border_radius=8)
        pygame.draw.rect(surface, col_u, rect_u, border_radius=8)

        draw_text("LOJA", font_medium, WHITE, surface, rect_b.centerx, rect_b.centery)
        draw_text("UPGRADES", font_medium, WHITE, surface, rect_u.centerx, rect_u.centery)

        # Conteúdo
        y_start = 70

        # Botão Multiplicador (só na loja)
        if current_tab == "buildings":
            rect_mult = pygame.Rect(PANEL_X + 10, y_start, PANEL_WIDTH - 20, 30)
            col_mult = (50, 50, 60)
            if rect_mult.collidepoint(mouse_pos):
                col_mult = (70, 70, 80)
            pygame.draw.rect(surface, col_mult, rect_mult, border_radius=5)
            draw_text(f"Comprar: {buy_amount}x", font_small, WHITE, surface, rect_mult.centerx, rect_mult.centery)
            y_start += 40

        scroll_y = y_start
        BTN_H = 70
        GAP = 8

        if current_tab == "buildings":
            for key, b in buildings.items():
                cost = calculate_bulk_cost(b["base_cost"], b["count"], buy_amount)
                can_buy = cookies >= cost
                rect = pygame.Rect(PANEL_X + 10, scroll_y, PANEL_WIDTH - 20, BTN_H)

                # Cor do botão
                base_col = BTN_GREEN if can_buy else BTN_RED
                if rect.collidepoint(mouse_pos) and can_buy:
                    base_col = (min(255, base_col[0] + 30), min(255, base_col[1] + 30), min(255, base_col[2] + 30))

                # Sombra do botão
                shadow_rect = rect.move(0, 3)
                pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=10)
                pygame.draw.rect(surface, base_col, rect, border_radius=10)

                # Detalhes
                # Ícone (Placeholder ou Emoji se fonte suportar, usando texto aqui)
                icon_surf = font_medium.render(b["icon"], True, WHITE)
                surface.blit(icon_surf, (rect.x + 15, rect.centery - icon_surf.get_height() // 2))

                # Nome e Custo
                name_col = WHITE
                cost_col = (200, 255, 200) if can_buy else (255, 200, 200)

                name_surf = font_medium.render(b["name"], True, name_col)
                surface.blit(name_surf, (rect.x + 60, rect.y + 10))

                cost_surf = font_small.render(f"Custo: {format_number(cost)}", True, cost_col)
                surface.blit(cost_surf, (rect.x + 60, rect.bottom - 25))

                # Quantidade
                count_surf = font_large.render(str(b["count"]), True, (255, 255, 255, 100))
                count_surf.set_alpha(150)
                surface.blit(count_surf, (rect.right - count_surf.get_width() - 20, rect.centery - count_surf.get_height() // 2))

                scroll_y += BTN_H + GAP

        elif current_tab == "upgrades":
            count = 0
            for t in techs:
                if t["bought"]:
                    continue
                count += 1
                can_buy = cookies >= t["cost"]
                rect = pygame.Rect(PANEL_X + 10, scroll_y, PANEL_WIDTH - 20, BTN_H)

                base_col = (60, 100, 160) if can_buy else (80, 80, 80)
                if rect.collidepoint(mouse_pos) and can_buy:
                    base_col = (80, 120, 180)

                pygame.draw.rect(surface, base_col, rect, border_radius=10)
                if not can_buy:
                    pygame.draw.rect(surface, (0, 0, 0, 100), rect, border_radius=10)

                draw_text(t["name"], font_medium, WHITE, surface, rect.x + 15, rect.y + 10, center=False)
                draw_text(t["desc"], font_tiny, GREY, surface, rect.x + 15, rect.bottom - 42, center=False)

                price_col = GOLD if can_buy else (255, 100, 100)
                draw_text(format_number(t["cost"]), font_small, price_col, surface, rect.right - 15, rect.centery, center=False, align_right=True)

                scroll_y += BTN_H + GAP

            if count == 0:
                draw_text("Todos os upgrades comprados!", font_small, GREY, surface, PANEL_X + PANEL_WIDTH // 2, 150)

    def draw_text(text, font, color, surface, x, y, center=True, align_right=False):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        elif align_right:
            text_rect.right = x
            text_rect.centery = y
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw_fancy_cookie(surface, x, y, radius, scale):
        # Sombra
        r = int(radius * scale)
        pygame.draw.circle(surface, (0, 0, 0, 80), (x + 5, y + 10), r)

        # Borda
        pygame.draw.circle(surface, COOKIE_SHADOW, (x, y), r)
        # Base
        pygame.draw.circle(surface, COOKIE_BASE, (x, y), int(r * 0.95))

        # Highlight (Bisel)
        pygame.draw.circle(surface, COOKIE_LIGHT, (x - r // 4, y - r // 4), int(r * 0.85))
        pygame.draw.circle(surface, COOKIE_BASE, (x - r // 5, y - r // 5), int(r * 0.85))  # Máscara para o highlight

        # Gotas de Chocolate (Posições fixas para não tremer)
        random.seed(42)  # Seed fixa para desenho consistente
        for _ in range(7):
            cx = x + int(random.uniform(-0.6, 0.6) * r)
            cy = y + int(random.uniform(-0.6, 0.6) * r)
            cr = int(r * 0.15)
            pygame.draw.circle(surface, CHIP_DARK, (cx, cy), cr)
            pygame.draw.circle(surface, CHIP_LIGHT, (cx - 2, cy - 2), int(cr * 0.5))
        random.seed()  # Reseta seed

    # Loop Principal
    running = True
    while running:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        dt = (now - last_time) / 1000.0
        last_time = now
        mouse_pos = pygame.mouse.get_pos()

        # --- Lógica ---

        # Cálculo de CpS (Cookies per Second)
        cps = 0.0
        global_mult = 1.0

        # Multiplicadores de upgrade
        for t in techs:
            if t["bought"]:
                if t["target"] == "global":
                    global_mult *= t["multiplier"]
                elif t["target"] == "click":
                    base_click_value += cps * t["multiplier"]

        for key, b in buildings.items():
            b_mult = 1.0
            for t in techs:
                if t["bought"] and t["target"] == key:
                    b_mult *= t["multiplier"]
            cps += (b["base_cps"] * b["count"]) * b_mult

        final_cps = cps * global_mult * frenzy_multiplier
        cookies += final_cps * dt

        # Checar Conquistas
        for a in achievements:
            if not a["unlocked"] and a["condition"](cookies, buildings):
                a["unlocked"] = True
                toasts.append(AchievementToast(a["name"], a["desc"], font_tiny, font_small, WIDTH))

        # Atualizar Efeitos
        if frenzy_timer > 0:
            frenzy_timer -= dt
            if frenzy_timer <= 0:
                frenzy_multiplier = 1.0
                floating_texts.append(FloatingText("Frenzy Acabou!", cookie_pos, font_medium, (255, 100, 100)))

        if cookie_scale > 1.0:
            cookie_scale -= 2.0 * dt
            if cookie_scale < 1.0:
                cookie_scale = 1.0

        # Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Clique no Cookie
                dist = math.hypot(mouse_pos[0] - cookie_pos[0], mouse_pos[1] - cookie_pos[1])
                if dist <= cookie_radius * cookie_scale:
                    click_gain = base_click_value * frenzy_multiplier
                    cookies += click_gain
                    cookie_scale = 1.1  # Pulo visual
                    floating_texts.append(FloatingText(f"+{format_number(click_gain)}", mouse_pos, font_medium))

                    # Spawnar partículas
                    for _ in range(random.randint(3, 6)):
                        particles.append(Particle(mouse_pos[0], mouse_pos[1], random.choice([COOKIE_BASE, CHIP_DARK])))

                # Clique no Golden Cookie
                if golden_cookie.check_click(mouse_pos):
                    if golden_cookie.type == "cookies":
                        cookies += golden_cookie.bonus_value
                        floating_texts.append(FloatingText(f"+{format_number(golden_cookie.bonus_value)}!!", mouse_pos, font_large, GOLD))
                    else:
                        frenzy_multiplier = 7.0
                        frenzy_timer = 20.0  # 20 segundos
                        floating_texts.append(FloatingText("FRENZY x7!!", mouse_pos, font_large, CYAN))
                    golden_cookie.reset()

                # Clique na UI
                if mouse_pos[0] > PANEL_X:
                    # Tabs
                    btn_w = PANEL_WIDTH // 2 - 10
                    rect_b = pygame.Rect(PANEL_X + 5, 10, btn_w, 45)
                    rect_u = pygame.Rect(PANEL_X + 5 + btn_w + 10, 10, btn_w, 45)
                    if rect_b.collidepoint(mouse_pos):
                        current_tab = "buildings"
                    if rect_u.collidepoint(mouse_pos):
                        current_tab = "upgrades"

                    # Multiplicador
                    if current_tab == "buildings":
                        rect_mult = pygame.Rect(PANEL_X + 10, 70, PANEL_WIDTH - 20, 30)
                        if rect_mult.collidepoint(mouse_pos):
                            buy_amount = 10 if buy_amount == 1 else (100 if buy_amount == 10 else 1)

                    # Botões de Compra
                    y_start = 70 + (40 if current_tab == "buildings" else 0)
                    scroll_y = y_start
                    BTN_H, GAP = 70, 8

                    if current_tab == "buildings":
                        for key, b in buildings.items():
                            rect = pygame.Rect(PANEL_X + 10, scroll_y, PANEL_WIDTH - 20, BTN_H)
                            if rect.collidepoint(mouse_pos):
                                cost = calculate_bulk_cost(b["base_cost"], b["count"], buy_amount)
                                if cookies >= cost:
                                    cookies -= cost
                                    b["count"] += buy_amount
                                    # Particle effect na UI?
                            scroll_y += BTN_H + GAP
                    elif current_tab == "upgrades":
                        for t in techs:
                            if t["bought"]:
                                continue
                            rect = pygame.Rect(PANEL_X + 10, scroll_y, PANEL_WIDTH - 20, BTN_H)
                            if rect.collidepoint(mouse_pos):
                                if cookies >= t["cost"]:
                                    cookies -= t["cost"]
                                    t["bought"] = True
                            scroll_y += BTN_H + GAP

        # Atualizações de Objetos
        particles = [p for p in particles if p.life > 0]
        for p in particles:
            p.update()

        floating_texts = [t for t in floating_texts if t.life > 0]
        for t in floating_texts:
            t.update()

        if len(toasts) > 0:
            if toasts[0].update():  # Retorna True se acabou
                toasts.pop(0)

        golden_cookie.update(cookies, final_cps)

        # --- Desenho ---
        draw_gradient_rect(screen, COLOR_BG_DARK, COLOR_BG_LIGHT, (0, 0, WIDTH, HEIGHT))

        # Sunburst Rotativo
        sunburst_angle = (sunburst_angle + 0.2) % 360
        rot_sunburst = pygame.transform.rotate(sunburst_surf, sunburst_angle)
        rect_sb = rot_sunburst.get_rect(center=cookie_pos)
        screen.blit(rot_sunburst, rect_sb)

        # Partículas atrás do cookie
        for p in particles:
            p.draw(screen)

        # Cookie Principal
        draw_fancy_cookie(screen, cookie_pos[0], cookie_pos[1], cookie_radius, cookie_scale)

        # Golden Cookie
        golden_cookie.draw(screen)

        # HUD Esquerda (Cookies e CpS)
        draw_text(f"{format_number(cookies)} Cookies", font_giant, WHITE, screen, cookie_pos[0], 50)

        cps_col = CYAN if frenzy_multiplier > 1 else (200, 200, 200)
        draw_text(f"por segundo: {format_number(final_cps)}", font_medium, cps_col, screen, cookie_pos[0], 100)

        # Painel Direito
        draw_ui_panel(screen, mouse_pos)

        # Overlays
        for t in floating_texts:
            t.draw(screen)
        if len(toasts) > 0:
            toasts[0].draw(screen)

        pygame.display.flip()

    return int(cookies)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Cookie Clicker Ultimate")
    clock = pygame.time.Clock()
    main(screen, clock, cheats_enabled=False)
