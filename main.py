# ARQUIVO MAIN PRINCIPAL QUE INICIA O HUB DE JOGOS COM AUTENTICAÇÃO FIREBASE E INTERFACE PYGAME
# RESPONSÁVEL POR GERENCIAR O MENU E INICIAR CADA JOGO INTEGRADO NO HUB
# Necessário instalar as dependências: pygame, pyrebase4
# Use:
# -pip install pygame pyrebase4

import pygame

pygame.init()
pygame.mixer.init()
import sys
import pyrebase
import os
import tower_defense_game
import snake_game
import ping_pong_game
import tic_tac_toe_game
import space_invaders_game
import flappy_bird_game
import pacman_game

# raycaster_game removido

print("--------------------------------------------------------------- INICIANDO O HUB DE JOGOS ---------------------------------------------------------------")

# Adiciona a linha para centralizar a janela ANTES do init
os.environ["SDL_VIDEO_WINDOW_POS"] = "center"

firebaseConfig = {
    "apiKey": "AIzaSyB6p7OSeA19GyE1lypGTfWe-_Otbt2b0f8",
    "authDomain": "mechanical-tower-defense.firebaseapp.com",
    "databaseURL": "https" + "://mechanical-tower-defense.firebaseio.com",
    "storageBucket": "mechanical-tower-defense.appspot.com",
}
try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
except Exception as e:
    print(f"ERRO CRITICO: Falha ao inicializar o Firebase: {e}")
    auth = None


# Define um tamanho de tela único. Sem scaling.
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Hub de Jogos")
clock = pygame.time.Clock()

BG_COLOR = (30, 30, 40)
TEXT_COLOR = (230, 230, 230)
PRIMARY_COLOR = (0, 150, 136)
PRIMARY_HOVER = (0, 170, 156)
SECONDARY_COLOR = (70, 70, 90)
SECONDARY_HOVER = (90, 90, 110)
INPUT_BG = (50, 50, 60)
FOCUS_COLOR = (50, 150, 255)
ERROR_COLOR = (200, 50, 50)
SUCCESS_COLOR = (0, 200, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

try:
    font_large = pygame.font.SysFont("Arial", 40)
    font_medium = pygame.font.SysFont("Arial", 32)
    font_small = pygame.font.SysFont("Arial", 24)
except:
    font_large = pygame.font.Font(None, 54)
    font_medium = pygame.font.Font(None, 42)
    font_small = pygame.font.Font(None, 32)


class Button:
    def __init__(
        self,
        text,
        rect,
        callback,
        font,
        bg_color,
        hover_color,
        text_color=WHITE,
        border_radius=8,
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.callback()
                return True
        return False


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


cheats_enabled = False
KONAMI_CODE = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a]
key_sequence = []


def run_tower_defense():
    tower_defense_game.main(screen, clock, cheats_enabled)


def run_snake():
    snake_game.main(screen, clock, cheats_enabled)


def run_ping_pong():
    ping_pong_game.main(screen, clock, cheats_enabled)


def run_tic_tac_toe():
    tic_tac_toe_game.main(screen, clock, cheats_enabled)


def run_space_invaders():
    space_invaders_game.main(screen, clock, cheats_enabled)


def run_flappy_bird():
    flappy_bird_game.main(screen, clock, cheats_enabled)


def run_pacman():
    pacman_game.main(screen, clock, cheats_enabled)


def main():
    global auth, cheats_enabled, key_sequence
    game_state = "LOGIN"

    if auth is None:
        game_state = "MENU"

    email_input = ""
    password_input = ""
    active_field = None
    login_message = ""
    message_color = ERROR_COLOR

    input_width = 400
    input_height = 50
    button_width = 190
    button_height = 50
    center_x = SCREEN_WIDTH // 2

    email_rect = pygame.Rect(center_x - (input_width // 2), 250, input_width, input_height)
    password_rect = pygame.Rect(center_x - (input_width // 2), 330, input_width, input_height)

    def do_login():
        nonlocal login_message, game_state, email_input, password_input, active_field, message_color
        try:
            user = auth.sign_in_with_email_and_password(email_input, password_input)
            game_state = "MENU"
            email_input = ""
            password_input = ""
            active_field = None
        except Exception as e:
            login_message = "Email ou senha inválidos."
            message_color = ERROR_COLOR

    def do_register():
        nonlocal login_message, message_color
        try:
            user = auth.create_user_with_email_and_password(email_input, password_input)
            login_message = "Registrado! Faça o login."
            message_color = SUCCESS_COLOR
        except Exception as e:
            message_color = ERROR_COLOR
            try:
                error_info = e.args[1]
                if "EMAIL_EXISTS" in error_info:
                    login_message = "Email já cadastrado."
                elif "WEAK_PASSWORD" in error_info:
                    login_message = "Senha fraca (mín. 6 chars)."
                else:
                    login_message = "Erro no registro."
            except (IndexError, TypeError, KeyError):
                login_message = "Erro no registro."

    login_button = Button(
        "Login",
        (email_rect.left, 410, button_width, button_height),
        do_login,
        font_small,
        PRIMARY_COLOR,
        PRIMARY_HOVER,
    )

    register_button = Button(
        "Registrar",
        (email_rect.right - button_width, 410, button_width, button_height),
        do_register,
        font_small,
        SECONDARY_COLOR,
        SECONDARY_HOVER,
    )

    login_buttons = [login_button, register_button]

    btn_w, btn_h = 280, 70
    col1, col2, col3, col4 = 100, 400, 700, 980

    game_buttons = [
        Button(
            "Tower Defense",
            (col1, 200, btn_w, btn_h),
            run_tower_defense,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
        Button(
            "Snake",
            (col2, 200, btn_w, btn_h),
            run_snake,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
        Button(
            "Ping Pong",
            (col3, 200, btn_w, btn_h),
            run_ping_pong,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
        Button(
            "Jogo da Velha",
            (col4, 200, btn_w, btn_h),
            run_tic_tac_toe,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
        Button(
            "Space Invaders",
            (col1, 300, btn_w, btn_h),
            run_space_invaders,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
        Button(
            "Flappy Bird",
            (col2, 300, btn_w, btn_h),
            run_flappy_bird,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
        Button(
            "Pac-Man",
            (col3, 300, btn_w, btn_h),
            run_pacman,
            font_small,
            PRIMARY_COLOR,
            PRIMARY_HOVER,
        ),
    ]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_state == "LOGIN":
                for btn in login_buttons:
                    btn.handle_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    login_message = ""
                    if email_rect.collidepoint(event.pos):
                        active_field = "email"
                    elif password_rect.collidepoint(event.pos):
                        active_field = "password"
                    else:
                        active_field = None

                if event.type == pygame.KEYDOWN:
                    # --- LÓGICA DE CHEAT ---
                    key_sequence.append(event.key)
                    key_sequence = key_sequence[-len(KONAMI_CODE) :]
                    if key_sequence == KONAMI_CODE:
                        cheats_enabled = not cheats_enabled  # Alterna o cheat
                        login_message = "CHEATS ATIVADOS!" if cheats_enabled else "CHEATS DESATIVADOS"
                        message_color = SUCCESS_COLOR if cheats_enabled else ERROR_COLOR
                    # --- FIM DA LÓGICA DE CHEAT ---

                    if event.key == pygame.K_RETURN:
                        if active_field == "email":
                            active_field = "password"
                        elif active_field == "password":
                            do_login()

                    if active_field == "email":
                        if event.key == pygame.K_BACKSPACE:
                            email_input = email_input[:-1]
                        elif event.key != pygame.K_TAB:
                            email_input += event.unicode
                    elif active_field == "password":
                        if event.key == pygame.K_BACKSPACE:
                            password_input = password_input[:-1]
                        elif event.key != pygame.K_TAB:
                            password_input += event.unicode

            elif game_state == "MENU":
                for button in game_buttons:
                    button.handle_event(event)

                if event.type == pygame.KEYDOWN:
                    # --- LÓGICA DE CHEAT (também no menu) ---
                    key_sequence.append(event.key)
                    key_sequence = key_sequence[-len(KONAMI_CODE) :]
                    if key_sequence == KONAMI_CODE:
                        cheats_enabled = not cheats_enabled
                    # --- FIM DA LÓGICA DE CHEAT ---

        screen.fill(BG_COLOR)

        if game_state == "LOGIN":
            draw_text(
                "HUB DE JOGOS - LOGIN",
                font_large,
                TEXT_COLOR,
                screen,
                SCREEN_WIDTH / 2,
                150,
                center=True,
            )

            draw_text(
                "Email:",
                font_small,
                TEXT_COLOR,
                screen,
                email_rect.left,
                email_rect.top - 28,
                center=False,
            )
            border_color_email = FOCUS_COLOR if active_field == "email" else TEXT_COLOR
            pygame.draw.rect(screen, INPUT_BG, email_rect, border_radius=8)
            pygame.draw.rect(screen, border_color_email, email_rect, 2, border_radius=8)
            draw_text(
                email_input,
                font_small,
                TEXT_COLOR,
                screen,
                email_rect.left + 15,
                email_rect.centery,
                v_center=True,
            )

            draw_text(
                "Senha:",
                font_small,
                TEXT_COLOR,
                screen,
                password_rect.left,
                password_rect.top - 28,
                center=False,
            )
            border_color_pass = FOCUS_COLOR if active_field == "password" else TEXT_COLOR
            pygame.draw.rect(screen, INPUT_BG, password_rect, border_radius=8)
            pygame.draw.rect(screen, border_color_pass, password_rect, 2, border_radius=8)
            draw_text(
                "*" * len(password_input),
                font_small,
                TEXT_COLOR,
                screen,
                password_rect.left + 15,
                password_rect.centery,
                v_center=True,
            )

            for btn in login_buttons:
                btn.draw(screen)

            draw_text(
                login_message,
                font_small,
                message_color,  # Usa a cor da mensagem (erro ou sucesso)
                screen,
                SCREEN_WIDTH / 2,
                480,
                center=True,
            )

        elif game_state == "MENU":
            draw_text(
                "HUB DE JOGOS",
                font_large,
                TEXT_COLOR,
                screen,
                SCREEN_WIDTH / 2,
                100,
                center=True,
            )
            for button in game_buttons:
                button.draw(screen)

            # --- Indicador de Cheat ---
            if cheats_enabled:
                draw_text("CHEATS ATIVADOS", font_small, SUCCESS_COLOR, screen, SCREEN_WIDTH / 2, SCREEN_HEIGHT - 30, center=True)
            # --- Fim do Indicador ---

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
