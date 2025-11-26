# JOGO FUNCIONAL
# Implementação de um quiz para o hub de jogos
import pygame
import sys
import random


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    # Cores
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (50, 50, 200)
    GRAY = (100, 100, 100)
    HOVER_GRAY = (150, 150, 150)

    try:
        font_large = pygame.font.SysFont("Arial", 60)
        font_medium = pygame.font.SysFont("Arial", 32)
        font_small = pygame.font.SysFont("Arial", 24)
    except:
        font_large = pygame.font.Font(None, 74)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)

    QUESTIONS = [
        # dev
        {"pergunta": "Qual biblioteca Python é usada nestes jogos?", "opcoes": ["Pygame", "TensorFlow", "React", "PysimpleGUI"], "resposta": 0},
        {"pergunta": "Qual comando define uma função em Python?", "opcoes": ["func", "def", "class", "import"], "resposta": 1},
        {"pergunta": "O que significa a sigla 'CPU'?", "opcoes": ["Central Process Unit", "Computer Personal Unit", "Central Power Unit", "Control Panel Unit"], "resposta": 0},
        # padrao
        {"pergunta": "Qual jogo envolve defender um caminho?", "opcoes": ["Snake", "Pac-Man", "Tower Defense", "Space Invaders"], "resposta": 2},
        {"pergunta": "Qual é a cor do Pac-Man?", "opcoes": ["Vermelho", "Verde", "Azul", "Amarelo"], "resposta": 3},
        {"pergunta": "Em 'Space Invaders', o jogador atira em...", "opcoes": ["Pássaros", "Alienígenas", "Fantasmas", "Frutas"], "resposta": 1},
        {"pergunta": "Qual o nome do irmão do Mario?", "opcoes": ["Wario", "Luigi", "Toad", "Bowser"], "resposta": 1},
        # ian
        {"pergunta": "No Minecraft, qual mob explode ao chegar perto?", "opcoes": ["Zumbi", "Esqueleto", "Creeper", "Enderman"], "resposta": 2},
        {"pergunta": "Qual minério é usado para criar circuitos no Minecraft?", "opcoes": ["Diamante", "Carvão", "Redstone", "Ferro"], "resposta": 2},
        # engenharia
        {"pergunta": "Qual a unidade de Força no Sistema Internacional?", "opcoes": ["Joule", "Watt", "Newton", "Pascal"], "resposta": 2},
        {"pergunta": "A 3ª Lei de Newton é conhecida como...", "opcoes": ["Inércia", "Ação e Reação", "Gravitação", "Termodinâmica"], "resposta": 1},
        # zueira
        {"pergunta": "Quem foi atropelado pos prova de probabilidade?", "opcoes": ["O cavalo", "O cachorro", "O Gava", "O Ian"], "resposta": 3},
        {"pergunta": "Quem é o mais bulinado de engenharia mecanica?", "opcoes": ["Taniguchi", "Ligeirin", "Da o pôpô", "Thragg"], "resposta": 2},
        {"pergunta": "Quem não se dá bem com cadeiras?", "opcoes": ["Igor", "Ligeirin", "Gava", "Ian"], "resposta": 0},
        {"pergunta": "Qual o nome do criador do jogo?", "opcoes": ["Ian", "Ligeirin", "El Fuego", "Você perdeu o jogo"], "resposta": 2},
    ]

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def game_loop():
        score = 0
        if cheats_enabled:
            score = 100000

        current_question_index = 0
        game_state = "pergunta"
        feedback_message = ""
        feedback_color = WHITE

        option_rects = [pygame.Rect(WIDTH // 2 - 250, 250 + i * 80, 500, 60) for i in range(4)]

        random.shuffle(QUESTIONS)

        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_state == "pergunta":
                        for i, rect in enumerate(option_rects):
                            if rect.collidepoint(mouse_pos):
                                if i == QUESTIONS[current_question_index]["resposta"]:
                                    score += 100
                                    feedback_message = "Correto!"
                                    feedback_color = GREEN
                                else:
                                    feedback_message = "Errado!"
                                    feedback_color = RED
                                game_state = "feedback"
                                break
                    elif game_state == "feedback":
                        current_question_index += 1
                        if current_question_index >= len(QUESTIONS):
                            game_state = "fim"
                        else:
                            game_state = "pergunta"

            screen.fill(BLACK)

            if game_state == "pergunta" or game_state == "feedback":
                # Proteção caso o índice ultrapasse (segurança extra)
                if current_question_index < len(QUESTIONS):
                    q_data = QUESTIONS[current_question_index]
                    draw_text(q_data["pergunta"], font_medium, WHITE, screen, WIDTH // 2, 150)
                    for i, rect in enumerate(option_rects):
                        color = GRAY
                        if rect.collidepoint(mouse_pos) and game_state == "pergunta":
                            color = HOVER_GRAY
                        pygame.draw.rect(screen, color, rect, border_radius=8)
                        draw_text(q_data["opcoes"][i], font_small, WHITE, screen, rect.centerx, rect.centery)

                if game_state == "feedback":
                    draw_text(feedback_message, font_large, feedback_color, screen, WIDTH // 2, HEIGHT // 2 + 200)
                    draw_text("Clique para continuar...", font_small, WHITE, screen, WIDTH // 2, HEIGHT - 50)

            elif game_state == "fim":
                draw_text("Quiz Concluído!", font_large, GREEN, screen, WIDTH // 2, HEIGHT // 2 - 40)
                draw_text(f"Pontuação Final: {score}", font_medium, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 20)
                draw_text("Pressione [ESC] para sair", font_small, WHITE, screen, WIDTH // 2, HEIGHT // 2 + 80)

            draw_text(f"Pontuação: {score}", font_medium, WHITE, screen, 10, 10, center=False)

            pygame.display.flip()
            clock.tick(60)

        return score

    return game_loop()
