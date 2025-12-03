# JOGO FUNCIONAL PRONTO
# Implementação de um quiz para o hub de jogos - Versão Estilizada
import pygame
import sys
import random
import os


def main(screen, clock, cheats_enabled):
    WIDTH = screen.get_width()
    HEIGHT = screen.get_height()

    BG_COLOR = (30, 33, 40)
    CARD_BG = (45, 48, 55)
    CARD_HOVER = (60, 63, 75)
    TEXT_COLOR = (230, 230, 230)
    ACCENT_COLOR = (100, 180, 255)

    SUCCESS_BG = (40, 167, 69)
    ERROR_BG = (220, 53, 69)
    SUCCESS_TEXT = (255, 255, 255)

    BORDER_COLOR = (70, 70, 80)

    try:
        font_large = pygame.font.SysFont("Arial", 50, bold=True)
        font_medium = pygame.font.SysFont("Arial", 28)
        font_small = pygame.font.SysFont("Arial", 22)
        font_bold = pygame.font.SysFont("Arial", 24, bold=True)
    except:
        font_large = pygame.font.Font(None, 60)
        font_medium = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 28)
        font_bold = pygame.font.Font(None, 30)

    sound_correct = None
    sound_wrong = None

    try:
        base_sound_path = os.path.join("assets", "sounds", "quiz")
        sound_correct = pygame.mixer.Sound(os.path.join(base_sound_path, "acertou.mp3"))
        sound_wrong = pygame.mixer.Sound(os.path.join(base_sound_path, "errou.mp3"))
        sound_correct.set_volume(0.5)
        sound_wrong.set_volume(0.5)
    except Exception as e:
        pass

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
        {"pergunta": "Quem foi atropelado pós prova de probabilidade?", "opcoes": ["O cavalo", "O cachorro", "O Gava", "O Ian"], "resposta": 2},
        {"pergunta": "Quem é o mais 'bulinado' de engenharia mecânica?", "opcoes": ["Taniguchi", "Ligeirin", "Da o pôpô", "Thragg"], "resposta": 1},
        {"pergunta": "Quem não se dá bem com cadeiras?", "opcoes": ["Down", "Ligeirin", "Gava", "Ian"], "resposta": 0},
        {"pergunta": "Qual o nome do criador desse jogo?", "opcoes": ["GDT", "Ligeirin", "El Fuego", "Você perdeu O jogo"], "resposta": 2},
    ]

    def draw_text(text, font, color, surface, x, y, center=True):
        text_obj = font.render(text, True, color)
        text_rect = text_obj.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        surface.blit(text_obj, text_rect)

    def draw_progress_bar(current, total):
        bar_width = 400
        bar_height = 10
        x = (WIDTH - bar_width) // 2
        y = 80  # Subiu um pouco

        pygame.draw.rect(screen, CARD_BG, (x, y, bar_width, bar_height), border_radius=5)
        progress = (current / total) * bar_width
        pygame.draw.rect(screen, ACCENT_COLOR, (x, y, progress, bar_height), border_radius=5)

        draw_text(f"Questão {current + 1} de {total}", font_small, TEXT_COLOR, screen, WIDTH // 2, y - 25)

    def game_loop():
        score = 0
        if cheats_enabled:
            score = 100000

        current_question_index = 0
        game_state = "pergunta"
        feedback_message = ""
        feedback_color = SUCCESS_BG
        selected_option_index = -1

        button_width = 600
        button_height = 70
        button_gap = 20
        # Ajustado layout para subir tudo um pouco e dar espaço para o feedback embaixo
        start_y = 230

        option_rects = []
        for i in range(4):
            x = (WIDTH - button_width) // 2
            y = start_y + i * (button_height + button_gap)
            option_rects.append(pygame.Rect(x, y, button_width, button_height))

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

                    if game_state == "feedback" and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                        current_question_index += 1
                        if current_question_index >= len(QUESTIONS):
                            game_state = "fim"
                        else:
                            game_state = "pergunta"
                            selected_option_index = -1

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if game_state == "pergunta":
                        for i, rect in enumerate(option_rects):
                            if rect.collidepoint(mouse_pos):
                                selected_option_index = i
                                if i == QUESTIONS[current_question_index]["resposta"]:
                                    score += 100
                                    feedback_message = "RESPOSTA CORRETA!"
                                    feedback_color = SUCCESS_BG
                                    if sound_correct:
                                        sound_correct.play()
                                else:
                                    feedback_message = "RESPOSTA ERRADA..."
                                    feedback_color = ERROR_BG
                                    if sound_wrong:
                                        sound_wrong.play()

                                game_state = "feedback"
                                break

                    elif game_state == "feedback":
                        current_question_index += 1
                        if current_question_index >= len(QUESTIONS):
                            game_state = "fim"
                        else:
                            game_state = "pergunta"
                            selected_option_index = -1

            screen.fill(BG_COLOR)

            if game_state == "pergunta" or game_state == "feedback":
                if current_question_index < len(QUESTIONS):
                    q_data = QUESTIONS[current_question_index]

                    draw_progress_bar(current_question_index, len(QUESTIONS))

                    question_y = 150  # Subiu para 150
                    draw_text(q_data["pergunta"], font_medium, TEXT_COLOR, screen, WIDTH // 2, question_y)

                    for i, rect in enumerate(option_rects):
                        # Lógica de cor do botão
                        bg_color = CARD_BG
                        border_col = BORDER_COLOR
                        text_col = TEXT_COLOR

                        if game_state == "pergunta":
                            if rect.collidepoint(mouse_pos):
                                bg_color = CARD_HOVER
                                border_col = ACCENT_COLOR

                        elif game_state == "feedback":
                            if i == q_data["resposta"]:
                                bg_color = SUCCESS_BG
                                border_col = SUCCESS_BG
                            elif i == selected_option_index:
                                bg_color = ERROR_BG
                                border_col = ERROR_BG
                            else:
                                bg_color = (40, 40, 45)
                                text_col = (100, 100, 100)

                        pygame.draw.rect(screen, bg_color, rect, border_radius=12)
                        pygame.draw.rect(screen, border_col, rect, 2, border_radius=12)

                        draw_text(q_data["opcoes"][i], font_small, text_col, screen, rect.centerx, rect.centery)

                if game_state == "feedback":
                    # Painel de feedback na parte inferior da tela
                    panel_width = 500
                    panel_height = 90
                    panel_x = (WIDTH - panel_width) // 2
                    panel_y = HEIGHT - 130  # Posição fixa no fundo

                    feedback_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)

                    # Fundo do painel
                    pygame.draw.rect(screen, CARD_BG, feedback_rect, border_radius=15)
                    # Borda colorida indicando acerto/erro
                    pygame.draw.rect(screen, feedback_color, feedback_rect, 3, border_radius=15)

                    draw_text(feedback_message, font_large, feedback_color, screen, feedback_rect.centerx, feedback_rect.centery - 15)
                    draw_text("Pressione [ESPAÇO] para continuar", font_small, (180, 180, 180), screen, feedback_rect.centerx, feedback_rect.centery + 25)

            elif game_state == "fim":
                pygame.draw.rect(screen, CARD_BG, (WIDTH // 2 - 300, HEIGHT // 2 - 150, 600, 300), border_radius=20)
                pygame.draw.rect(screen, ACCENT_COLOR, (WIDTH // 2 - 300, HEIGHT // 2 - 150, 600, 300), 2, border_radius=20)

                draw_text("Quiz Concluído!", font_large, ACCENT_COLOR, screen, WIDTH // 2, HEIGHT // 2 - 80)

                final_score_text = f"Pontuação: {score} / {len(QUESTIONS) * 100}"
                draw_text(final_score_text, font_medium, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2)

                perc = score / (len(QUESTIONS) * 100)
                if perc == 1.0:
                    msg = "Perfeito! Você é um gênio!"
                elif perc >= 0.7:
                    msg = "Muito bom! Mandou bem!"
                elif perc >= 0.5:
                    msg = "Na média... dá para melhorar."
                else:
                    msg = "Vixe... estude mais!"

                draw_text(msg, font_small, (180, 180, 180), screen, WIDTH // 2, HEIGHT // 2 + 40)
                draw_text("Pressione [ESC] para sair", font_bold, TEXT_COLOR, screen, WIDTH // 2, HEIGHT // 2 + 100)

            score_surf = font_small.render(f"Pts: {score}", True, ACCENT_COLOR)
            screen.blit(score_surf, (20, 20))

            pygame.display.flip()
            clock.tick(60)

        return score

    return game_loop()
