# JOGO FUNCIONAL
# Código feito pelos alunos: Ian Riki Taniguchi, João Alves Gava e João Vitor Del Pupo
# Código reutilizado do trabalho dado pelo professor. (necessárias varias modificações para funcionar no hub)
# Import das bibliotecas necessárias: pygame para o jogo e sys para fechar o programa.
import pygame
import sys
from pygame.locals import *


def main(screen, clock, cheats_enabled):
    # Usa o relógio e a tela passados pelo hub
    relogio = clock
    tela = screen

    # Obtém as dimensões da tela
    larg = tela.get_width()
    alt = tela.get_height()

    BG_COLOR = (20, 20, 30)
    LINE_COLOR = (50, 50, 65)
    BALL_COLOR = (255, 255, 255)
    P1_COLOR = (255, 50, 100)
    P2_COLOR = (0, 200, 255)
    TEXT_COLOR = (200, 200, 200)
    CHEAT_COLOR = (0, 255, 100)

    paddle_margin = 20
    p1_x = paddle_margin
    p2_x = larg - paddle_margin - 10

    raquete_larg = 12
    raquete_alt = 100
    p1_y = alt // 2 - raquete_alt // 2
    p2_y = alt // 2 - raquete_alt // 2

    b_x = larg // 2
    b_y = alt // 2
    bola_radius = 8
    bdx = 5
    bdy = 5

    ball_trail = []
    TRAIL_LENGTH = 15

    velocidade_raquete = 8

    score_p1 = 0
    score_p2 = 0

    try:
        font_score = pygame.font.SysFont("Arial", 60, bold=True)
        font_cheat = pygame.font.SysFont("Arial", 20)
    except:
        font_score = pygame.font.Font(None, 74)
        font_cheat = pygame.font.Font(None, 24)

    p1_altura_cheat = alt if cheats_enabled else raquete_alt
    p1_velocidade_cheat = 0 if cheats_enabled else velocidade_raquete

    def reset_bola(direcao):
        return larg // 2, alt // 2, 5 * direcao, 5

    def draw_dashed_line(surface, color, start_pos, end_pos, width=1, dash_length=10):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dl = dash_length

        if x1 == x2:
            ycoords = [y for y in range(y1, y2, dl if dl > 0 else 1)]
            for i, y in enumerate(ycoords):
                if i % 2 == 0:
                    pygame.draw.line(surface, color, (x1, y), (x1, y + dl), width)

    # Loop principal do jogo
    running = True
    while running:
        relogio.tick(60)  # 60 FPS estável é melhor para física que 100
        tela.fill(BG_COLOR)

        # Eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

        if cheats_enabled:
            p1_y = 0

        # Atualiza posição da bola
        b_x += bdx
        b_y += bdy

        ball_trail.append((b_x, b_y))
        if len(ball_trail) > TRAIL_LENGTH:
            ball_trail.pop(0)

        # Rebote nas paredes superior/inferior
        if b_y - bola_radius <= 0 or b_y + bola_radius >= alt:
            bdy *= -1

        # Retângulos de colisão
        bola_rect = pygame.Rect(b_x - bola_radius, b_y - bola_radius, bola_radius * 2, bola_radius * 2)
        p1_rect = pygame.Rect(p1_x, p1_y, raquete_larg, p1_altura_cheat)
        p2_rect = pygame.Rect(p2_x, p2_y, raquete_larg, raquete_alt)

        # Colisão P1
        if bola_rect.colliderect(p1_rect):
            bdx = abs(bdx) * 1.05  # Aumenta um pouco a velocidade a cada batida
            offset = (b_y - (p1_y + p1_altura_cheat / 2)) / (p1_altura_cheat / 2)
            bdy = int(8 * offset)  # Mais ângulo
            if bdy == 0:
                bdy = 1

        # Colisão P2
        if bola_rect.colliderect(p2_rect):
            bdx = -abs(bdx) * 1.05
            offset = (b_y - (p2_y + raquete_alt / 2)) / (raquete_alt / 2)
            bdy = int(8 * offset)
            if bdy == 0:
                bdy = 1

        # Limitar velocidade máxima para não quebrar a física
        if bdx > 15:
            bdx = 15
        if bdx < -15:
            bdx = -15

        # Marcação de ponto
        if b_x < 0:
            score_p2 += 1
            b_x, b_y, bdx, bdy = reset_bola(1)
            ball_trail.clear()
        elif b_x > larg:
            score_p1 += 1
            b_x, b_y, bdx, bdy = reset_bola(-1)
            ball_trail.clear()

        # Controles
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and p1_y > 0:
            p1_y -= p1_velocidade_cheat
        if keys[pygame.K_s] and p1_y + p1_altura_cheat < alt:
            p1_y += p1_velocidade_cheat
        if keys[pygame.K_UP] and p2_y > 0:
            p2_y -= velocidade_raquete
        if keys[pygame.K_DOWN] and p2_y + raquete_alt < alt:
            p2_y += velocidade_raquete

        draw_dashed_line(tela, LINE_COLOR, (larg // 2, 0), (larg // 2, alt), width=4, dash_length=20)

        p1_score_surf = font_score.render(str(score_p1), True, LINE_COLOR)  # Cor discreta
        p2_score_surf = font_score.render(str(score_p2), True, LINE_COLOR)
        tela.blit(p1_score_surf, (larg // 4, 50))
        tela.blit(p2_score_surf, (larg * 3 // 4, 50))

        pygame.draw.rect(tela, P1_COLOR, p1_rect, border_radius=6)
        pygame.draw.rect(tela, P2_COLOR, p2_rect, border_radius=6)

        for i, pos in enumerate(ball_trail):  # rastro
            alpha = int((i / len(ball_trail)) * 255)
            radius = int(bola_radius * (i / len(ball_trail)))
            trail_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*BALL_COLOR, alpha // 2), (radius, radius), radius)
            tela.blit(trail_surf, (pos[0] - radius, pos[1] - radius))

        pygame.draw.circle(tela, BALL_COLOR, (int(b_x), int(b_y)), bola_radius)

        if cheats_enabled:
            cheat_surf = font_cheat.render("CHEATS ON: Raquete Gigante", True, CHEAT_COLOR)
            tela.blit(cheat_surf, (10, alt - 30))

        pygame.display.flip()
