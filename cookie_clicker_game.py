import pygame
import sys
import math
import random


def format_number(n):
    n = int(n)
    if n < 1000:
        return str(n)
    units = ["", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc"]
    magnitude = 0
    while abs(n) >= 1000:
        n /= 1000.0
        magnitude += 1
    if magnitude > 0:
        return f"{n:.2f}".rstrip("0").rstrip(".") + units[magnitude]
    return str(int(n))


def calculate_bulk_cost(base_cost, current_count, amount):
    price_of_next = base_cost * (1.15**current_count)
    if amount == 1:
        return math.ceil(price_of_next)
    ratio = 1.15
    total_cost = price_of_next * ((ratio**amount) - 1) / (ratio - 1)
    return math.ceil(total_cost)


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()
    FPS = 60

    WHITE = (240, 240, 240)
    BLACK = (10, 10, 10)
    BROWN = (139, 69, 19)
    LIGHT_BROWN = (205, 133, 63)

    UI_BG = (45, 45, 55)
    UI_COOKIE_BG = (30, 30, 40)

    BTN_BUYABLE = (46, 139, 87)
    BTN_TOO_EXPENSIVE = (165, 42, 42)
    BTN_HOVER_MOD = 30
    BTN_BORDER = (20, 20, 20)

    TAB_ACTIVE = (70, 130, 180)
    TAB_INACTIVE = (60, 60, 70)

    GOLD = (255, 215, 0)
    CYAN = (0, 255, 255)
    RED_TEXT = (255, 80, 80)
    YELLOW_TEXT = (255, 255, 100)

    try:
        font_large = pygame.font.SysFont("Arial", 60, bold=True)
        font_count = pygame.font.SysFont("Arial", 44, bold=True)
        font_medium = pygame.font.SysFont("Arial", 24, bold=True)
        font_small = pygame.font.SysFont("Arial", 18)
        font_tiny = pygame.font.SysFont("Arial", 14)
    except:
        font_large = pygame.font.Font(None, 74)
        font_count = pygame.font.Font(None, 55)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)
        font_tiny = pygame.font.Font(None, 18)

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

    class FloatingText:
        def __init__(self, text, pos, color=YELLOW_TEXT):
            self.text = text
            self.pos = list(pos)
            self.color = color
            self.font = font_small
            self.life = FPS * 1.5

        def update(self):
            self.pos[1] -= 1
            self.life -= 1

        def draw(self, surface):
            if self.life > 0:
                draw_text(self.text, self.font, self.color, surface, self.pos[0], self.pos[1], center=True)

    class AchievementToast:
        def __init__(self, name, desc):
            self.name = name
            self.desc = desc
            self.rect = pygame.Rect(WIDTH // 2 - 150, -80, 300, 70)
            self.target_y = 20
            self.timer = FPS * 4
            self.state = "entering"

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
            pygame.draw.rect(surface, UI_BG, self.rect, border_radius=10)
            pygame.draw.rect(surface, GOLD, self.rect, 2, border_radius=10)
            draw_text("CONQUISTA!", font_tiny, GOLD, surface, self.rect.centerx, self.rect.top + 15)
            draw_text(self.name, font_small, WHITE, surface, self.rect.centerx, self.rect.bottom - 25)
            return self.state == "leaving" and self.rect.bottom < 0

    class GoldenCookie:
        def __init__(self):
            self.rect = pygame.Rect(0, 0, 60, 60)
            self.reset()

        def reset(self):
            x = random.randint(WIDTH // 10, WIDTH // 2 - 50)
            y = random.randint(50, HEIGHT - 50)
            self.rect.center = (x, y)
            self.active = False
            self.life = FPS * random.randint(10, 20)
            self.spawn_timer = FPS * random.randint(30, 60)
            self.bonus_value = 0

        def activate(self, current_cookies, current_cps):
            if random.random() < 0.7:
                self.bonus_value = max(current_cps * 600, current_cookies * 0.15, 100)
                self.type = "cookies"
            else:
                self.type = "frenzy"
            self.active = True

        def update(self, current_cookies, current_cps):
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
                pygame.draw.circle(surface, GOLD, self.rect.center, 30)
                draw_text("!", font_medium, BROWN, surface, self.rect.centerx, self.rect.centery)

        def check_click(self, pos):
            return self.active and self.rect.collidepoint(pos)

    BUILDINGS_DATA = {
        "cursor": {"name": "Cursor", "desc": "Clica por você.", "icon": "[C]", "base_cost": 15, "base_cps": 0.1, "count": 0},
        "grandma": {"name": "Vovó", "desc": "Assa biscoitos.", "icon": "[V]", "base_cost": 100, "base_cps": 1.0, "count": 0},
        "farm": {"name": "Fazenda", "desc": "Colheita de cookies.", "icon": "[F]", "base_cost": 1100, "base_cps": 8.0, "count": 0},
        "mine": {"name": "Mina", "desc": "Minera massa.", "icon": "[M]", "base_cost": 12000, "base_cps": 47.0, "count": 0},
        "factory": {"name": "Fábrica", "desc": "Produção em massa.", "icon": "[IND]", "base_cost": 130000, "base_cps": 260.0, "count": 0},
    }

    TECH_UPGRADES_DATA = [
        {"id": "u_cursor_1", "name": "Dedo Reforçado", "desc": "Cursores 2x mais eficientes.", "cost": 500, "target": "cursor", "multiplier": 2, "bought": False},
        {"id": "u_grandma_1", "name": "Rolo de Massa", "desc": "Vovós 2x mais eficientes.", "cost": 1000, "target": "grandma", "multiplier": 2, "bought": False},
        {"id": "u_farm_1", "name": "Adubo Doce", "desc": "Fazendas produzem 2x mais.", "cost": 11000, "target": "farm", "multiplier": 2, "bought": False},
        {"id": "u_global_1", "name": "Mão Divina", "desc": "+5% de CPS global.", "cost": 1000000, "target": "global", "multiplier": 1.05, "bought": False},
    ]

    ACHIEVEMENTS_DATA = [
        {"id": "a_start", "name": "O Começo", "desc": "Asse 1 biscoito.", "condition": lambda c, b: c >= 1, "unlocked": False},
        {"id": "a_1k", "name": "Padeiro Amador", "desc": "Tenha 1.000 biscoitos.", "condition": lambda c, b: c >= 1000, "unlocked": False},
        {"id": "a_clicker", "name": "Clicker Viciado", "desc": "Tenha 10 Cursores.", "condition": lambda c, b: b["cursor"]["count"] >= 10, "unlocked": False},
    ]

    def game_loop():
        cookies = 0.0
        click_value = 1.0
        buildings = {k: v.copy() for k, v in BUILDINGS_DATA.items()}
        techs = [t.copy() for t in TECH_UPGRADES_DATA]
        achievements = [a.copy() for a in ACHIEVEMENTS_DATA]

        buy_amount = 1
        current_tab = "buildings"

        if cheats_enabled:
            cookies = 50000.0

        UPGRADE_BAR_WIDTH = 340
        UPGRADE_BAR_X = WIDTH - UPGRADE_BAR_WIDTH
        cookie_center = (UPGRADE_BAR_X // 2, HEIGHT // 2)
        cookie_radius = 140
        cookie_scale = 1.0

        BTN_HEIGHT = 64
        BTN_MARGIN = 8

        floating_texts = []
        toasts = []
        golden_cookie = GoldenCookie()
        frenzy_multiplier = 1.0
        frenzy_timer = 0
        last_update = pygame.time.get_ticks()

        running = True
        while running:
            now = pygame.time.get_ticks()
            dt = (now - last_update) / 1000.0
            last_update = now
            mouse_pos = pygame.mouse.get_pos()

            cps = 0.0
            global_mult = 1.0
            for t in techs:
                if t["bought"] and t["target"] == "global":
                    global_mult *= t["multiplier"]
            for key, b_data in buildings.items():
                building_mult = 1.0
                for t in techs:
                    if t["bought"] and t["target"] == key:
                        building_mult *= t["multiplier"]
                cps += (b_data["base_cps"] * b_data["count"]) * building_mult
            final_cps = cps * global_mult * frenzy_multiplier
            cookies += final_cps * dt

            for a in achievements:
                if not a["unlocked"] and a["condition"](cookies, buildings):
                    a["unlocked"] = True
                    toasts.append(AchievementToast(a["name"], a["desc"]))

            if frenzy_timer > 0:
                frenzy_timer -= dt
                if frenzy_timer <= 0:
                    frenzy_multiplier = 1.0
                    floating_texts.append(FloatingText("Frenzy acabou", cookie_center, RED_TEXT))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if math.hypot(mouse_pos[0] - cookie_center[0], mouse_pos[1] - cookie_center[1]) <= cookie_radius:
                        cookies += click_value * frenzy_multiplier
                        cookie_scale = 1.05
                        floating_texts.append(FloatingText(f"+{format_number(click_value * frenzy_multiplier)}", mouse_pos))

                    if golden_cookie.check_click(mouse_pos):
                        if golden_cookie.type == "cookies":
                            cookies += golden_cookie.bonus_value
                            floating_texts.append(FloatingText(f"+{format_number(golden_cookie.bonus_value)}!", mouse_pos, GOLD))
                        else:
                            frenzy_multiplier = 7.0
                            frenzy_timer = 20.0
                            floating_texts.append(FloatingText("FRENZY x7!", mouse_pos, CYAN))
                        golden_cookie.reset()

                    if mouse_pos[0] > UPGRADE_BAR_X:
                        tab_y = 10
                        tab_w = UPGRADE_BAR_WIDTH // 2 - 10
                        btn_build = pygame.Rect(UPGRADE_BAR_X + 5, tab_y, tab_w, 40)
                        btn_tech = pygame.Rect(UPGRADE_BAR_X + 5 + tab_w + 5, tab_y, tab_w, 40)

                        if btn_build.collidepoint(mouse_pos):
                            current_tab = "buildings"
                        if btn_tech.collidepoint(mouse_pos):
                            current_tab = "upgrades"

                        if current_tab == "buildings":
                            btn_mult = pygame.Rect(UPGRADE_BAR_X + 10, 60, UPGRADE_BAR_WIDTH - 20, 30)
                            if btn_mult.collidepoint(mouse_pos):
                                buy_amount = 10 if buy_amount == 1 else (100 if buy_amount == 10 else 1)

                        start_y = 100 if current_tab == "buildings" else 60
                        if current_tab == "buildings":
                            for key, b in buildings.items():
                                rect = pygame.Rect(UPGRADE_BAR_X + 5, start_y, UPGRADE_BAR_WIDTH - 10, BTN_HEIGHT)
                                if rect.collidepoint(mouse_pos):
                                    cost = calculate_bulk_cost(b["base_cost"], b["count"], buy_amount)
                                    if cookies >= cost:
                                        cookies -= cost
                                        b["count"] += buy_amount
                                    break
                                start_y += BTN_HEIGHT + BTN_MARGIN
                        elif current_tab == "upgrades":
                            for t in techs:
                                if not t["bought"]:
                                    rect = pygame.Rect(UPGRADE_BAR_X + 5, start_y, UPGRADE_BAR_WIDTH - 10, BTN_HEIGHT)
                                    if rect.collidepoint(mouse_pos) and cookies >= t["cost"]:
                                        cookies -= t["cost"]
                                        t["bought"] = True
                                    break
                                    start_y += BTN_HEIGHT + BTN_MARGIN

            if cookie_scale > 1.0:
                cookie_scale -= 0.01 * 60 * dt
            floating_texts = [t for t in floating_texts if t.life > 0]
            for t in floating_texts:
                t.update()
            if len(toasts) > 0 and toasts[0].update():
                toasts.pop(0)
            golden_cookie.update(cookies, final_cps)

            screen.fill(BLACK)

            pygame.draw.rect(screen, UI_COOKIE_BG, (0, 0, UPGRADE_BAR_X, HEIGHT))
            if frenzy_multiplier > 1:
                pygame.draw.circle(screen, (50, 20, 20), cookie_center, 250, 2)

            rad = int(cookie_radius * cookie_scale)
            pygame.draw.circle(screen, BROWN, cookie_center, rad)
            chip_offsets = [(-40, -40), (40, 50), (30, -50), (-50, 20)]
            for ox, oy in chip_offsets:
                cx, cy = cookie_center[0] + int(ox * cookie_scale), cookie_center[1] + int(oy * cookie_scale)
                pygame.draw.circle(screen, LIGHT_BROWN, (cx, cy), int(20 * cookie_scale))
            golden_cookie.draw(screen)

            draw_text(f"{format_number(cookies)} Cookies", font_large, WHITE, screen, cookie_center[0], 80)
            cps_color = CYAN if frenzy_multiplier > 1 else WHITE
            draw_text(f"por segundo: {format_number(final_cps)}", font_medium, cps_color, screen, cookie_center[0], 130)

            pygame.draw.rect(screen, UI_BG, (UPGRADE_BAR_X, 0, UPGRADE_BAR_WIDTH, HEIGHT))

            tab_y, tab_w = 10, UPGRADE_BAR_WIDTH // 2 - 10
            btn_build = pygame.Rect(UPGRADE_BAR_X + 5, tab_y, tab_w, 40)
            btn_tech = pygame.Rect(UPGRADE_BAR_X + 5 + tab_w + 5, tab_y, tab_w, 40)

            col_b = TAB_ACTIVE if current_tab == "buildings" else TAB_INACTIVE
            col_t = TAB_ACTIVE if current_tab == "upgrades" else TAB_INACTIVE
            pygame.draw.rect(screen, col_b, btn_build, border_radius=8)
            pygame.draw.rect(screen, col_t, btn_tech, border_radius=8)
            draw_text("Estruturas", font_medium, WHITE, screen, btn_build.centerx, btn_build.centery)
            draw_text("Melhorias", font_medium, WHITE, screen, btn_tech.centerx, btn_tech.centery)

            if current_tab == "buildings":
                btn_mult = pygame.Rect(UPGRADE_BAR_X + 10, 60, UPGRADE_BAR_WIDTH - 20, 30)
                col_mult = TAB_INACTIVE
                if btn_mult.collidepoint(mouse_pos):
                    col_mult = (col_mult[0] + 20, col_mult[1] + 20, col_mult[2] + 20)
                pygame.draw.rect(screen, col_mult, btn_mult, border_radius=5)
                draw_text(f"Comprar: {buy_amount}x", font_small, WHITE, screen, btn_mult.centerx, btn_mult.centery)

                y_off = 100
                for key, b in buildings.items():
                    cost = calculate_bulk_cost(b["base_cost"], b["count"], buy_amount)
                    can_buy = cookies >= cost
                    rect = pygame.Rect(UPGRADE_BAR_X + 5, y_off, UPGRADE_BAR_WIDTH - 10, BTN_HEIGHT)

                    col = BTN_BUYABLE if can_buy else BTN_TOO_EXPENSIVE
                    if rect.collidepoint(mouse_pos):
                        col = (min(col[0] + BTN_HOVER_MOD, 255), min(col[1] + BTN_HOVER_MOD, 255), min(col[2] + BTN_HOVER_MOD, 255))

                    pygame.draw.rect(screen, col, rect, border_radius=8)
                    pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=8)

                    PADDING_X = 12
                    PADDING_Y = 8

                    draw_text(f"{b['icon']} {b['name']}", font_medium, WHITE, screen, rect.left + PADDING_X, rect.top + PADDING_Y + 10, center=False)

                    cost_col = YELLOW_TEXT if can_buy else RED_TEXT
                    draw_text(f"Custo: {format_number(cost)}", font_small, cost_col, screen, rect.left + PADDING_X, rect.bottom - PADDING_Y - 8, center=False)

                    draw_text(str(b["count"]), font_count, WHITE, screen, rect.right - PADDING_X - 5, rect.centery, center=False, align_right=True)

                    y_off += BTN_HEIGHT + BTN_MARGIN

            elif current_tab == "upgrades":
                y_off = 60
                count_visible = 0
                for t in techs:
                    if t["bought"]:
                        continue
                    count_visible += 1
                    rect = pygame.Rect(UPGRADE_BAR_X + 5, y_off, UPGRADE_BAR_WIDTH - 10, BTN_HEIGHT)
                    can_buy = cookies >= t["cost"]

                    col = BTN_BUYABLE if can_buy else TAB_INACTIVE
                    if rect.collidepoint(mouse_pos) and can_buy:
                        col = (min(col[0] + BTN_HOVER_MOD, 255), min(col[1] + BTN_HOVER_MOD, 255), min(col[2] + BTN_HOVER_MOD, 255))

                    pygame.draw.rect(screen, col, rect, border_radius=8)
                    pygame.draw.rect(screen, BTN_BORDER, rect, 2, border_radius=8)

                    PADDING_X = 12
                    draw_text(t["name"], font_medium, WHITE, screen, rect.left + PADDING_X, rect.top + 15, center=False)
                    draw_text(t["desc"], font_tiny, (200, 200, 200), screen, rect.left + PADDING_X, rect.bottom - 20, center=False)

                    cost_col = YELLOW_TEXT if can_buy else RED_TEXT
                    draw_text(format_number(t["cost"]), font_small, cost_col, screen, rect.right - PADDING_X, rect.centery, center=False, align_right=True)

                    y_off += BTN_HEIGHT + BTN_MARGIN

                if count_visible == 0:
                    draw_text("Tudo comprado!", font_medium, TAB_INACTIVE, screen, UPGRADE_BAR_X + UPGRADE_BAR_WIDTH // 2, 100)

            for t in floating_texts:
                t.draw(screen)
            if len(toasts) > 0:
                toasts[0].draw(screen)

            pygame.display.flip()
            clock.tick(FPS)

    game_loop()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    pygame.display.set_caption("Cookie Clicker Bonito")
    clock = pygame.time.Clock()
    main(screen, clock, cheats_enabled=False)
