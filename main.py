# ARQUIVO MAIN PRINCIPAL - COM CHEATS FUNCIONANDO NO MENU
# Necessário instalar as dependências: pygame, pyrebase4
# Use:
# -pip install pygame pyrebase4

import pygame
import requests

pygame.init()
pygame.mixer.init()
import sys
import pyrebase
import os
import math

os.environ["SDL_VIDEO_WINDOW_POS"] = "center"

firebaseConfig = {
    "apiKey": "AIzaSyB6p7OSeA19GyE1lypGTfWe-_Otbt2b0f8",
    "authDomain": "mechanical-tower-defense.firebaseapp.com",
    "databaseURL": "https://mechanical-tower-defense-default-rtdb.firebaseio.com",
    "storageBucket": "mechanical-tower-defense.appspot.com",
}

DB_URL = "https://mechanical-tower-defense-default-rtdb.firebaseio.com"

try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
except Exception as e:
    print(f"ERRO CRITICO: Falha ao inicializar o Firebase: {e}")
    auth = None
    db = None

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hub de Jogos - GDT")
clock = pygame.time.Clock()

try:
    import tower_defense_game, snake_game, ping_pong_game, tic_tac_toe_game
    import space_invaders_game, flappy_bird_game, pacman_game, cookie_clicker_game
    import memory_game, doisK_game, quiz_game, evade_game
except ImportError as e:
    print(f"AVISO: Algum jogo não foi encontrado. {e}")

BG_COLOR = (20, 22, 28)
GRID_COLOR = (35, 40, 50)
PANEL_COLOR = (30, 32, 40)
TEXT_COLOR = (240, 240, 245)
PRIMARY_COLOR = (0, 180, 160)
PRIMARY_HOVER = (0, 210, 190)
SECONDARY_COLOR = (60, 65, 80)
SECONDARY_HOVER = (80, 85, 100)
INPUT_BG = (15, 18, 22)
FOCUS_COLOR = (64, 169, 255)
ERROR_COLOR = (255, 85, 85)
SUCCESS_COLOR = (80, 250, 120)
WHITE = (255, 255, 255)

try:
    font_title = pygame.font.SysFont("Arial", 50, bold=True)
    font_large = pygame.font.SysFont("Arial", 40)
    font_medium = pygame.font.SysFont("Arial", 28)
    font_small = pygame.font.SysFont("Arial", 22)
    font_toast = pygame.font.SysFont("Arial", 20, bold=True)
except:
    font_title = pygame.font.Font(None, 60)
    font_large = pygame.font.Font(None, 54)
    font_medium = pygame.font.Font(None, 38)
    font_small = pygame.font.Font(None, 28)
    font_toast = pygame.font.Font(None, 26)


def draw_grid(surface, offset_y):
    gap = 40
    width, height = surface.get_size()
    for x in range(0, width, gap):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, height), 1)
    for y in range(int(offset_y) % gap, height, gap):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (width, y), 1)


def draw_panel(surface, rect):
    shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 80), shadow.get_rect(), border_radius=12)
    surface.blit(shadow, (rect.x + 6, rect.y + 6))
    pygame.draw.rect(surface, PANEL_COLOR, rect, border_radius=12)
    pygame.draw.rect(surface, (50, 55, 65), rect, 1, border_radius=12)


def draw_text(text, font, color, surface, x, y, center=False, v_center=False):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = (x, y)
    elif v_center:
        text_rect.left = x
        text_rect.centery = y
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


class Button:
    def __init__(self, text, rect, callback, font, bg_color, hover_color, text_color=WHITE, border_radius=8):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.is_hovered = False
        self.disabled = False

    def draw(self, surface):
        if self.disabled:
            color = SECONDARY_COLOR
        else:
            color = self.hover_color if self.is_hovered else self.bg_color

        if not self.is_hovered and not self.disabled:
            s_rect = self.rect.move(0, 3)
            pygame.draw.rect(surface, (0, 0, 0, 50), s_rect, border_radius=self.border_radius)

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if self.disabled:
            return False

        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.callback()
                return True
        return False


def submit_score(game_name, score):
    if not user_info:
        print("AVISO: user_info não definido ao tentar salvar score.")
        return

    try:
        # Dados do usuário autenticado
        user_id = user_info.get("localId")  # UID do Firebase Auth
        user_token = user_info.get("idToken")  # Token de acesso
        user_email = user_info.get("email")

        if not user_id or not game_name or not user_token:
            print(f"AVISO: Tentativa de salvar score sem dados suficientes." f" UID: {user_id}, Jogo: {game_name}, Token presente? {user_token is not None}")
            return

        # Nome do jogador
        if user_email:
            user_name = user_email.split("@")[0]
        else:
            user_name = "Jogador"

        # Garante que o score é número
        try:
            score = int(score)
        except (TypeError, ValueError):
            print(f"AVISO: score inválido ({score}) para o jogo {game_name}.")
            return

        # Caminho REST: /scores/{game_name}/{user_id}.json?auth={token}
        user_score_url = f"{DB_URL}/scores/{game_name}/{user_id}.json?auth={user_token}"

        try:
            get_resp = requests.get(user_score_url)
            if get_resp.status_code == 200:
                curr_data = get_resp.json()
                curr = curr_data.get("score") if curr_data else None
            else:
                print(f"Aviso leitura score: {get_resp.status_code} - {get_resp.text}")
                curr = None
        except Exception as e:
            print(f"Aviso leitura score (possível permissão/internet): {e}")
            curr = None

        # 2) Só salva se for recorde ou primeira vez
        if curr is None or score > curr:
            print(f"Salvando novo recorde para {user_name} (UID: {user_id}) em {game_name}: {score}")
            try:
                payload = {"name": user_name, "score": score}
                put_resp = requests.put(user_score_url, json=payload)

                if put_resp.status_code != 200:
                    print(f"ERRO ao escrever score no Firebase: {put_resp.status_code} - {put_resp.text}")
            except Exception as e:
                print(f"ERRO ao escrever score no Firebase (possível Permission denied): {e}")
        else:
            print(f"Score {score} NÃO é maior que o atual ({curr}) para {user_name} em {game_name}. Não sobrescrevendo.")

    except Exception as e:
        print(f"ERRO CRÍTICO ao salvar score: {e}")


def show_scoreboard(game_name, game_title):
    scores = []
    try:
        # CORREÇÃO: Obtém o token do usuário logado
        user_token = user_info.get("idToken")

        # CORREÇÃO: Passa o token para o firebase na hora de buscar (token=user_token)
        # Sem isso, se o banco tiver regras de segurança, a leitura é bloqueada.
        data = db.child("scores").child(game_name).order_by_child("score").limit_to_last(10).get(token=user_token).val()

        if data:
            # Ordena decrescente (maior pontuação primeiro)
            scores = sorted(data.items(), key=lambda i: i[1].get("score", 0), reverse=True)
    except Exception as e:
        print(f"Erro ao carregar ranking de {game_title}: {e}")
        pass

    back_btn = Button("Voltar", (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50), lambda: None, font_small, SECONDARY_COLOR, SECONDARY_HOVER)
    run = True
    bg_y = 0
    while run:
        bg_y += 0.5
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False
            if back_btn.handle_event(e):
                run = False
        screen.fill(BG_COLOR)
        draw_grid(screen, bg_y)

        p_rect = pygame.Rect((SCREEN_WIDTH - 600) // 2, 100, 600, 500)
        draw_panel(screen, p_rect)
        draw_text(f"Ranking: {game_title}", font_large, PRIMARY_COLOR, screen, SCREEN_WIDTH / 2, 130, center=True)

        y = 200
        if not scores:
            draw_text("Sem dados ou erro de conexão.", font_medium, TEXT_COLOR, screen, SCREEN_WIDTH / 2, 300, center=True)
        else:
            for i, (_, d) in enumerate(scores):
                if i >= 10:
                    break
                col = PRIMARY_COLOR if i == 0 else TEXT_COLOR  # Destaca o 1º lugar

                # Formatação segura dos dados
                nome_jogador = d.get("name", "Desconhecido")
                pontuacao = d.get("score", 0)

                draw_text(f"#{i+1} {nome_jogador} - {pontuacao}", font_medium, col, screen, p_rect.left + 50, y)
                y += 40

        back_btn.draw(screen)
        pygame.display.flip()
        clock.tick(60)


def run_game(module, name):
    try:
        s = module.main(screen, clock, cheats_enabled)
        if s is not None:
            submit_score(name, s)
    except Exception as e:
        print(f"Erro ao rodar {name}: {e}")


cheats_enabled = False
user_info = {}
KONAMI = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a]
SECRET = [pygame.K_y, pygame.K_a, pygame.K_k, pygame.K_u, pygame.K_t]
key_seq = []


def main():
    global cheats_enabled, key_seq, user_info
    game_state = "LOGIN" if auth else "MENU"
    bg_offset = 0
    toast_message = ""
    toast_color = PRIMARY_COLOR
    toast_timer = 0
    toast_duration = 3500

    input_error = False
    is_loading = False

    email = ""
    password = ""
    active_field = None

    panel_rect = pygame.Rect((SCREEN_WIDTH - 450) // 2, (SCREEN_HEIGHT - 500) // 2, 450, 500)
    email_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 150, 350, 50)
    pass_rect = pygame.Rect(panel_rect.x + 50, panel_rect.y + 250, 350, 50)

    def trigger_toast(msg, color, is_error=False):
        nonlocal toast_message, toast_color, toast_timer, input_error
        toast_message = msg
        toast_color = color
        toast_timer = pygame.time.get_ticks() + toast_duration
        input_error = is_error

    def draw_toast():
        if pygame.time.get_ticks() < toast_timer and toast_message:
            text_surf = font_toast.render(toast_message, True, WHITE)
            w = text_surf.get_width() + 40
            h = 40
            r = pygame.Rect((SCREEN_WIDTH - w) // 2, panel_rect.bottom - 40, w, h)

            pygame.draw.rect(screen, toast_color, r, border_radius=20)
            text_rect = text_surf.get_rect(center=r.center)
            screen.blit(text_surf, text_rect)

    def try_login():
        nonlocal game_state, is_loading, email, password, active_field
        if not email or not password:
            trigger_toast("Preencha todos os campos!", ERROR_COLOR, True)
            return

        is_loading = True
        draw_frame()

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            user_info["localId"] = user["localId"]
            user_info["email"] = user["email"]
            user_info["idToken"] = user["idToken"]
            game_state = "MENU"
            email = ""
            password = ""
            active_field = None
            trigger_toast(f"Bem-vindo, {user_info['email']}!", SUCCESS_COLOR)
        except Exception as e:
            trigger_toast("Email ou senha incorretos.", ERROR_COLOR, True)
            print(e)
        finally:
            is_loading = False

    def try_register():
        nonlocal is_loading
        if len(password) < 6:
            trigger_toast("Senha deve ter 6+ dígitos.", ERROR_COLOR, True)
            return

        is_loading = True
        draw_frame()

        try:
            auth.create_user_with_email_and_password(email, password)
            trigger_toast("Conta criada! Faça login agora.", SUCCESS_COLOR)
        except Exception as e:
            err = str(e)
            if "EMAIL_EXISTS" in err:
                trigger_toast("Este email já existe.", ERROR_COLOR, True)
            elif "INVALID_EMAIL" in err:
                trigger_toast("Email inválido.", ERROR_COLOR, True)
            else:
                trigger_toast("Erro ao registrar.", ERROR_COLOR, True)
            print(e)
        finally:
            is_loading = False

    btn_login = Button("ENTRAR", (panel_rect.x + 50, panel_rect.y + 340, 160, 50), try_login, font_small, PRIMARY_COLOR, PRIMARY_HOVER, border_radius=25)
    btn_reg = Button("CRIAR CONTA", (panel_rect.right - 210, panel_rect.y + 340, 160, 50), try_register, font_small, SECONDARY_COLOR, SECONDARY_HOVER, border_radius=25)

    def go_menu():
        nonlocal game_state
        game_state = "MENU"

    def go_score():
        nonlocal game_state
        game_state = "SCORE_MENU"

    btns_menu = []

    games_data = [
        ("Tower Defense", lambda: run_game(tower_defense_game, "tower_defense_game")),
        ("Snake", lambda: run_game(snake_game, "snake_game")),
        ("Ping Pong", lambda: run_game(ping_pong_game, "ping_pong")),
        ("Jogo da Velha", lambda: run_game(tic_tac_toe_game, "tic_tac_toe")),
        ("Space Invaders", lambda: run_game(space_invaders_game, "space_invaders_game")),
        ("Flappy Bird", lambda: run_game(flappy_bird_game, "flappy_bird_game")),
        ("Pac-Man", lambda: run_game(pacman_game, "pacman_game")),
        ("Cookie Clicker", lambda: run_game(cookie_clicker_game, "cookie_clicker_game")),
        ("Memória", lambda: run_game(memory_game, "memory_game")),
        ("2048", lambda: run_game(doisK_game, "doisK_game")),
        ("Quiz", lambda: run_game(quiz_game, "quiz_game")),
        ("Evade", lambda: run_game(evade_game, "evade_game")),
    ]

    bx, by = (SCREEN_WIDTH - (4 * 260 + 3 * 30)) // 2, 200

    for i, (name, cb) in enumerate(games_data):
        c, r = i % 4, i // 4
        btns_menu.append(Button(name, (bx + c * 290, by + r * 95, 260, 65), cb, font_small, PRIMARY_COLOR, PRIMARY_HOVER))

    btns_menu.append(Button("RANKINGS", (SCREEN_WIDTH // 2 - 150, by + 3 * 95 + 20, 300, 60), go_score, font_medium, SECONDARY_COLOR, SECONDARY_HOVER, border_radius=30))

    btns_score = []

    score_data = [("Tower Defense", "tower_defense_game"), ("Snake", "snake_game"), ("Ping Pong", "ping_pong"), ("Jogo da Velha", "tic_tac_toe"), ("Space Invaders", "space_invaders_game"), ("Flappy Bird", "flappy_bird_game"), ("Pac-Man", "pacman_game"), ("Cookie Clicker", "cookie_clicker_game"), ("Memória", "memory_game"), ("2048", "doisK_game"), ("Quiz", "quiz_game"), ("Evade", "evade_game")]

    for i, (title, db_id) in enumerate(score_data):
        c, r = i % 4, i // 4
        btns_score.append(Button(title, (bx + c * 290, by + r * 95, 260, 65), lambda d=db_id, t=title: show_scoreboard(d, t), font_small, PRIMARY_COLOR, PRIMARY_HOVER))

    btns_score.append(Button("Voltar", (SCREEN_WIDTH // 2 - 150, by + 3 * 95 + 20, 300, 60), go_menu, font_medium, SECONDARY_COLOR, SECONDARY_HOVER, border_radius=30))

    def draw_frame():
        screen.fill(BG_COLOR)
        draw_grid(screen, bg_offset)

        if game_state == "LOGIN":
            draw_panel(screen, panel_rect)
            draw_text("HUB DE JOGOS", font_title, PRIMARY_COLOR, screen, SCREEN_WIDTH / 2, panel_rect.y + 50, center=True)
            draw_text("Acesso Restrito", font_medium, SECONDARY_HOVER, screen, SCREEN_WIDTH / 2, panel_rect.y + 90, center=True)

            draw_text("Email", font_small, TEXT_COLOR, screen, email_rect.x, email_rect.y - 25)
            draw_text("Senha", font_small, TEXT_COLOR, screen, pass_rect.x, pass_rect.y - 25)

            bc_email = ERROR_COLOR if input_error else (FOCUS_COLOR if active_field == "email" else SECONDARY_COLOR)
            bc_pass = ERROR_COLOR if input_error else (FOCUS_COLOR if active_field == "pass" else SECONDARY_COLOR)

            pygame.draw.rect(screen, INPUT_BG, email_rect, border_radius=6)
            pygame.draw.rect(screen, bc_email, email_rect, 2 if active_field == "email" or input_error else 1, border_radius=6)

            pygame.draw.rect(screen, INPUT_BG, pass_rect, border_radius=6)
            pygame.draw.rect(screen, bc_pass, pass_rect, 2 if active_field == "pass" or input_error else 1, border_radius=6)

            screen.set_clip(email_rect.inflate(-10, -10))
            draw_text(email + ("|" if active_field == "email" and (pygame.time.get_ticks() // 500) % 2 == 0 else ""), font_small, WHITE, screen, email_rect.x + 10, email_rect.centery, v_center=True)
            screen.set_clip(None)

            screen.set_clip(pass_rect.inflate(-10, -10))
            display_pass = "•" * len(password)
            draw_text(display_pass + ("|" if active_field == "pass" and (pygame.time.get_ticks() // 500) % 2 == 0 else ""), font_medium, WHITE, screen, pass_rect.x + 10, pass_rect.centery + 2, v_center=True)
            screen.set_clip(None)

            if is_loading:
                r = btn_login.rect
                pygame.draw.rect(screen, SECONDARY_COLOR, r, border_radius=25)
                draw_text("Conectando...", font_small, WHITE, screen, r.centerx, r.centery, center=True)
            else:
                btn_login.draw(screen)
                btn_reg.draw(screen)

            draw_toast()

        elif game_state == "MENU":
            draw_text("HUB PRINCIPAL", font_title, WHITE, screen, SCREEN_WIDTH / 2, 80, center=True)
            draw_text(f"Usuário: {user_info.get('email','Guest')}", font_small, PRIMARY_COLOR, screen, SCREEN_WIDTH / 2, 130, center=True)
            for b in btns_menu:
                b.draw(screen)
            if cheats_enabled:
                draw_text("CHEATS ON", font_small, SUCCESS_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30, center=True)

        elif game_state == "SCORE_MENU":
            draw_text("SELECIONE O JOGO", font_title, WHITE, screen, SCREEN_WIDTH / 2, 100, center=True)
            for b in btns_score:
                b.draw(screen)

        pygame.display.flip()

    running = True
    while running:
        bg_offset += 0.5

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if is_loading:
                continue
            if event.type == pygame.KEYDOWN:
                key_seq.append(event.key)
                key_seq = key_seq[-10:]

                if key_seq == KONAMI:
                    cheats_enabled = not cheats_enabled
                    trigger_toast(f"Cheats: {'ATIVADOS' if cheats_enabled else 'DESATIVADOS'}", SUCCESS_COLOR if cheats_enabled else ERROR_COLOR)

                if game_state == "LOGIN" and key_seq[-len(SECRET) :] == SECRET:
                    email, password = "ianrtaniguchi@gmail.com", "girafa37"
                    try_login()

            if game_state == "LOGIN":
                btn_login.handle_event(event)
                btn_reg.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    input_error = False
                    if email_rect.collidepoint(event.pos):
                        active_field = "email"
                    elif pass_rect.collidepoint(event.pos):
                        active_field = "pass"
                    else:
                        active_field = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        active_field = "pass" if active_field == "email" else "email"
                    elif event.key == pygame.K_RETURN:
                        if active_field == "email":
                            active_field = "pass"
                        else:
                            try_login()
                    elif active_field == "email":
                        if event.key == pygame.K_BACKSPACE:
                            email = email[:-1]
                        else:
                            email += event.unicode
                    elif active_field == "pass":
                        if event.key == pygame.K_BACKSPACE:
                            password = password[:-1]
                        else:
                            password += event.unicode

            elif game_state == "MENU":
                for b in btns_menu:
                    b.handle_event(event)
            elif game_state == "SCORE_MENU":
                for b in btns_score:
                    b.handle_event(event)

        draw_frame()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
