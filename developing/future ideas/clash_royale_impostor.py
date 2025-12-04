import pygame
import sys
import random
import pyrebase
import time

# Configuração do Firebase
firebaseConfig = {
    "apiKey": "AIzaSyB6p7OSeA19GyE1lypGTfWe-_Otbt2b0f8",
    "authDomain": "mechanical-tower-defense.firebaseapp.com",
    "databaseURL": "https://mechanical-tower-defense-default-rtdb.firebaseio.com",
    "storageBucket": "mechanical-tower-defense.appspot.com",
}

try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    db = firebase.database()
except:
    print("Erro ao conectar no firebase")
    db = None

# Cache local de cartas (será preenchido pelo Firebase)
LOCAL_CARDS_CACHE = []


def fetch_cards_from_db():
    """Busca a lista de cartas do nó /impostor_rooms/cards no Firebase"""
    global LOCAL_CARDS_CACHE
    if not db:
        return []

    try:
        # Tenta pegar do caminho onde as cartas foram salvas
        cards_data = db.child("impostor_rooms").child("cards").get().val()

        # Se não achar em impostor_rooms, tenta na raiz (caso tenha importado lá)
        if not cards_data:
            cards_data = db.child("cards").get().val()

        if cards_data:
            # Converte para lista se vier como dicionário ou mantém se já for lista
            if isinstance(cards_data, list):
                LOCAL_CARDS_CACHE = cards_data
            elif isinstance(cards_data, dict):
                LOCAL_CARDS_CACHE = list(cards_data.values())
            return LOCAL_CARDS_CACHE
    except Exception as e:
        print(f"Erro ao buscar cartas: {e}")

    return []


def parse_color(color_str):
    """Converte 'rgb(50, 50, 150)' para tupla (50, 50, 150)"""
    if isinstance(color_str, tuple) or isinstance(color_str, list):
        return tuple(color_str)

    try:
        # Remove 'rgb(', ')' e espaços
        clean_str = color_str.replace("rgb(", "").replace(")", "").replace(" ", "")
        r, g, b = map(int, clean_str.split(","))
        return (r, g, b)
    except:
        return (100, 100, 100)  # Cor padrão cinza se falhar


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    BG_COLOR = (20, 20, 25)
    BTN_COLOR = (70, 130, 180)
    IMPOSTOR_RED = (220, 50, 50)
    CREW_BLUE = (50, 150, 220)
    WHITE = (255, 255, 255)

    try:
        font_title = pygame.font.SysFont("Arial", 50, bold=True)
        font_text = pygame.font.SysFont("Arial", 30)
        font_input = pygame.font.SysFont("Arial", 40)
    except:
        font_title = pygame.font.Font(None, 60)
        font_text = pygame.font.Font(None, 40)
        font_input = pygame.font.Font(None, 50)

    # Estado Local
    player_name = ""
    room_id = "1234"  # Sala padrão para facilitar testes
    state = "LOGIN"  # LOGIN, LOBBY, GAME_REVEAL

    my_role = None  # "CREW" ou "IMPOSTOR"
    current_card_info = None
    last_sync = 0
    sync_interval = 1000  # ms (1 segundo)

    # Input rectangles
    name_rect = pygame.Rect(WIDTH // 2 - 150, 200, 300, 50)
    room_rect = pygame.Rect(WIDTH // 2 - 150, 300, 300, 50)
    active_input = "name"  # name ou room

    # Carrega as cartas logo no início
    fetch_cards_from_db()

    def draw_text(text, font, color, x, y, center=True):
        surf = font.render(str(text), True, color)
        rect = surf.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(surf, rect)

    def sync_game_state():
        # Função para ler o estado da sala no Firebase
        if not db:
            return None
        try:
            room_data = db.child("impostor_rooms").child(room_id).get().val()
            return room_data
        except:
            return None

    def start_new_round(players_dict):
        if not players_dict:
            return

        # Garante que temos cartas antes de sortear
        if not LOCAL_CARDS_CACHE:
            if not fetch_cards_from_db():
                print("Nenhuma carta encontrada no banco!")
                return

        # Escolhe carta e impostor
        card_index = random.randint(0, len(LOCAL_CARDS_CACHE) - 1)
        player_ids = list(players_dict.keys())
        impostor_id = random.choice(player_ids)

        # Atualiza Firebase
        update_data = {"state": "REVEAL", "current_card_index": card_index, "impostor_id": impostor_id, "timestamp": time.time()}  # Força atualização
        db.child("impostor_rooms").child(room_id).update(update_data)

    running = True
    while running:
        dt = clock.tick(30)
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False

                if state == "LOGIN":
                    if e.key == pygame.K_TAB:
                        active_input = "room" if active_input == "name" else "name"
                    elif e.key == pygame.K_RETURN:
                        if player_name:
                            try:
                                # Verifica se o banco de dados foi iniciado
                                if db is None:
                                    raise Exception("O objeto 'db' está vazio (falha na inicialização).")

                                # Adiciona jogador ao DB
                                my_id = f"{player_name}_{int(time.time())}"
                                db.child("impostor_rooms").child(room_id).child("players").child(my_id).set(player_name)
                                state = "LOBBY"
                            except Exception as e:
                                print(f"ERRO DETALHADO: {e}")
                    elif e.key == pygame.K_BACKSPACE:
                        if active_input == "name":
                            player_name = player_name[:-1]
                        else:
                            room_id = room_id[:-1]
                    else:
                        if len(e.unicode) > 0 and e.unicode.isprintable():
                            if active_input == "name" and len(player_name) < 12:
                                player_name += e.unicode
                            elif active_input == "room" and len(room_id) < 6:
                                room_id += e.unicode

                # Comandos no Lobby/Game
                if state in ["LOBBY", "GAME_REVEAL"]:
                    if e.key == pygame.K_SPACE:  # Começar nova rodada
                        # Só precisamos ler a lista de players atual para sortear
                        room_data = sync_game_state()
                        if room_data and "players" in room_data:
                            start_new_round(room_data["players"])

        # --- Lógica de Sincronização ---
        if state in ["LOBBY", "GAME_REVEAL"]:
            now = pygame.time.get_ticks()
            if now - last_sync > sync_interval:
                room_data = sync_game_state()
                last_sync = now

                if room_data:
                    # Atualiza estado do jogo localmente
                    server_state = room_data.get("state", "LOBBY")

                    if server_state == "REVEAL":
                        state = "GAME_REVEAL"

                        # Descobre quem é o impostor
                        impostor_id = room_data.get("impostor_id")
                        card_idx = room_data.get("current_card_index", 0)

                        # Garante que temos as cartas carregadas
                        if not LOCAL_CARDS_CACHE:
                            fetch_cards_from_db()

                        # Pega a carta segura pelo índice
                        if 0 <= card_idx < len(LOCAL_CARDS_CACHE):
                            current_card_info = LOCAL_CARDS_CACHE[card_idx]
                        else:
                            current_card_info = {"name": "Erro", "hint": "Carta não encontrada", "color": "rgb(100,100,100)"}

                        # Verifica se EU sou o impostor
                        # A verificação deve ser feita pelo ID exato agora, não só startswith
                        # Mas como my_id é local e persistente no escopo, precisamos garantir que ele exista
                        # Solução simples: se o ID do impostor contém meu nome, assumo que sou eu
                        if impostor_id and player_name in impostor_id:
                            my_role = "IMPOSTOR"
                        else:
                            my_role = "CREW"
                    else:
                        state = "LOBBY"

        # --- Desenho ---
        screen.fill(BG_COLOR)

        if state == "LOGIN":
            draw_text("CLASH IMPOSTOR", font_title, WHITE, WIDTH // 2, 100)

            draw_text("Seu Nome:", font_text, WHITE, WIDTH // 2, 180)
            pygame.draw.rect(screen, WHITE if active_input == "name" else (150, 150, 150), name_rect, 2)
            draw_text(player_name, font_input, WHITE, name_rect.centerx, name_rect.centery)

            draw_text("ID da Sala:", font_text, WHITE, WIDTH // 2, 280)
            pygame.draw.rect(screen, WHITE if active_input == "room" else (150, 150, 150), room_rect, 2)
            draw_text(room_id, font_input, WHITE, room_rect.centerx, room_rect.centery)

            draw_text("Pressione [ENTER] para entrar", font_text, BTN_COLOR, WIDTH // 2, 400)

        elif state == "LOBBY":
            draw_text(f"Sala: {room_id}", font_title, WHITE, WIDTH // 2, 50)
            draw_text(f"Olá, {player_name}!", font_text, WHITE, WIDTH // 2, 100)
            draw_text("Aguardando inicio...", font_text, (150, 150, 150), WIDTH // 2, HEIGHT // 2)
            draw_text("[ESPAÇO] para sortear a carta", font_text, BTN_COLOR, WIDTH // 2, HEIGHT - 100)

        elif state == "GAME_REVEAL":
            if my_role == "IMPOSTOR":
                screen.fill(IMPOSTOR_RED)
                draw_text("VOCÊ É O IMPOSTOR!", font_title, WHITE, WIDTH // 2, 100)
                draw_text("Shh! Finja que sabe qual é a carta.", font_text, WHITE, WIDTH // 2, 150)

                if current_card_info:
                    pygame.draw.rect(screen, (0, 0, 0), (WIDTH // 2 - 300, HEIGHT // 2 - 100, 600, 200), border_radius=15)
                    draw_text("DICA PARA VOCÊ:", font_text, (255, 200, 0), WIDTH // 2, HEIGHT // 2 - 50)
                    draw_text(current_card_info.get("hint", "Sem dica"), font_input, WHITE, WIDTH // 2, HEIGHT // 2 + 20)

            else:
                screen.fill(CREW_BLUE)
                draw_text("VOCÊ NÃO É O IMPOSTOR!", font_title, WHITE, WIDTH // 2, 100)
                draw_text("Descubra quem não sabe a carta!", font_text, WHITE, WIDTH // 2, 150)

                if current_card_info:
                    raw_color = current_card_info.get("color", "rgb(100,100,100)")
                    card_color = parse_color(raw_color)

                    pygame.draw.rect(screen, card_color, (WIDTH // 2 - 200, HEIGHT // 2 - 120, 400, 240), border_radius=15)
                    pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 200, HEIGHT // 2 - 120, 400, 240), 5, border_radius=15)
                    draw_text(current_card_info.get("name", "Desconhecido"), font_title, WHITE, WIDTH // 2, HEIGHT // 2)

            draw_text("[ESPAÇO] Próxima Rodada", font_text, WHITE, WIDTH // 2, HEIGHT - 50)

        pygame.display.flip()

    return 0
