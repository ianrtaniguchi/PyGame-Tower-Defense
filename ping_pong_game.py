# JOGO FUNCIONAL
# Código feito pelos alunos: Ian Riki Taniguchi, João Alves Gava e João Vitor Del Pupo
# Código reutilizado do trabalho dado pelo professor. (necessárias varias modificações para funcionar no hub)
# Import das bibliotecas necessárias: pygame para o jogo e sys para fechar o programa.
import pygame
import sys
from pygame.locals import *


# Função principal que o hub vai chamar
def main(screen, clock):

    # Usa o relógio e a tela passados pelo hub
    relogio = clock
    tela = screen

    # Obtém as dimensões da tela
    larg = tela.get_width()
    alt = tela.get_height()

    # Posições iniciais (ajustei p2_x para usar 'larg')
    p1_x = 10
    p1_y = 10
    p2_x = larg - 20
    p2_y = 350
    b_x = larg // 2
    b_y = alt // 2
    bdx = 4
    bdy = 4
    raquete_larg = 10
    raquete_alt = 100
    velocidade_raquete = 7

    score_p1 = 0
    score_p2 = 0

    font = pygame.font.SysFont(None, 40)

    # Cores
    PRETO = (0, 0, 0)
    BRANCO = (255, 255, 255)
    VERMELHO = (255, 0, 0)
    AMARELO = (255, 255, 0)
    AZUL = (0, 0, 255)

    # Função de reset adaptada: ela retorna os novos valores
    def reset_bola(direcao):
        new_b_x = larg // 2
        new_b_y = alt // 2
        new_bdx = 4 * direcao
        new_bdy = 4
        return new_b_x, new_b_y, new_bdx, new_bdy

    # Loop principal do jogo
    running = True
    while running:
        relogio.tick(100)
        tela.fill(PRETO)

        # Eventos
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False  # Sai do loop do jogo
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # Adiciona tecla ESC para sair
                    running = False

        # Desenhar raquetes
        p1 = pygame.draw.rect(tela, VERMELHO, (p1_x, p1_y, raquete_larg, raquete_alt))
        p2 = pygame.draw.rect(tela, AMARELO, (p2_x, p2_y, raquete_larg, raquete_alt))

        # Desenhar a bola
        bola = pygame.draw.circle(tela, AZUL, (b_x, b_y), 10)

        # Atualiza posição da bola
        b_x = b_x + bdx
        b_y = b_y + bdy

        # Rebote nas paredes superior/inferior
        if b_y - 10 <= 0 or b_y + 10 >= alt:
            bdy *= -1

        # Verifica colisão com as raquetes
        bola_rect = pygame.Rect(b_x - 10, b_y - 10, 20, 20)
        p1_rect = pygame.Rect(p1_x, p1_y, raquete_larg, raquete_alt)
        p2_rect = pygame.Rect(p2_x, p2_y, raquete_larg, raquete_alt)

        # Colisão com raquete esquerda
        if bola_rect.colliderect(p1_rect):
            bdx = abs(bdx)
            offset = (b_y - (p1_y + raquete_alt / 2)) / (raquete_alt / 2)
            bdy = int(6 * offset)
            if bdy == 0:
                bdy = 1  # Evita que a bola fique reta

        # Colisão com raquete direita
        if bola_rect.colliderect(p2_rect):
            bdx = -abs(bdx)
            offset = (b_y - (p2_y + raquete_alt / 2)) / (raquete_alt / 2)
            bdy = int(6 * offset)
            if bdy == 0:
                bdy = 1  # Evita que a bola fique reta

        # Marcação de ponto
        if b_x < 0:
            score_p2 += 1
            b_x, b_y, bdx, bdy = reset_bola(1)  # Recebe os novos valores
        elif b_x > larg:
            score_p1 += 1
            b_x, b_y, bdx, bdy = reset_bola(-1)  # Recebe os novos valores

        # Controles
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and p1_y > 0:
            p1_y -= velocidade_raquete
        if keys[pygame.K_s] and p1_y + raquete_alt < alt:
            p1_y += velocidade_raquete
        if keys[pygame.K_UP] and p2_y > 0:
            p2_y -= velocidade_raquete
        if keys[pygame.K_DOWN] and p2_y + raquete_alt < alt:
            p2_y += velocidade_raquete

        # Desenhar o placar (antes do update!)
        score_text = f"{score_p1}  -  {score_p2}"
        score_surf = font.render(score_text, True, BRANCO)
        score_rect = score_surf.get_rect(center=(larg // 2, 30))
        tela.blit(score_surf, score_rect)

        # Atualiza a tela (apenas uma vez, no final)
        pygame.display.flip()
