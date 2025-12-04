Com base na análise do código fonte, o projeto evoluiu de um simples *Tower Defense* para um **Hub de Jogos** completo, integrado com Firebase para autenticação e placar online, contendo mais de 10 jogos diferentes.

Aqui está o `README.md` atualizado para refletir o estado real do projeto:

````markdown
# 🎮 PyGame Game Hub & Tower Defense

**Uma plataforma completa de mini-games desenvolvida em Python e Pygame, com sistema de login, ranking online e múltiplos jogos.**

---

## 📝 Sobre o Projeto

Este projeto, originalmente focado em um *Tower Defense*, expandiu-se para se tornar um **Hub de Jogos**. O sistema conta com autenticação de usuários via Firebase, salvamento de pontuações na nuvem e uma variedade de jogos clássicos e originais.

---

## 👥 Desenvolvedores

1. **Ian Riki Taniguchi**
2. **João Alves Gava**
3. **João Vitor Del Pupo**

---

## 🚀 Funcionalidades Principais

### 🔐 Sistema de Hub (Main)
* **Autenticação:** Login e Registro de usuários integrados ao Firebase Auth.
* **Ranking Global:** Placar de líderes online (Top 10) para cada jogo.
* **Menu Interativo:** Interface gráfica para seleção de jogos e visualização de scores.
* **Sistema de Cheats:** Códigos secretos (Konami Code) para ativar modos de trapaça.

### 🏰 Tower Defense (Carro Chefe)
O jogo principal do projeto, onde o objetivo é impedir que inimigos atravessem o mapa.
* **Inimigos:** Soldado (rápido, vida baixa) e Tanque (lento, vida alta, recompensa alta).
* **Torres:**
    * *Flecha:* Rápida, baixo custo, alvo único.
    * *Canhão:* Lento, alto custo, dano em área (splash damage).
* **Mecânicas:** Sistema de ondas (waves), economia (dinheiro por abate), sistema de vidas e upgrades de torres (Dano e Velocidade).

### 🕹️ Outros Jogos Incluídos
Além do Tower Defense, o Hub inclui recriações de clássicos:
1.  **Snake:** O clássico jogo da cobrinha.
2.  **Ping Pong:** Jogo estilo Pong para 2 jogadores ou contra parede.
3.  **Jogo da Velha:** Modo local e **Multiplayer Online** (criação de salas).
4.  **Clash Royale Impostor:** Jogo de dedução social e memória com cartas.
5.  **Flappy Bird:** Clone do famoso jogo de desviar de canos.
6.  **Pac-Man:** Implementação com mapas, pastilhas e fantasmas com IA básica.
7.  **Cookie Clicker:** Jogo incremental com loja, upgrades e "Golden Cookies".
8.  **Jogo da Memória:** Encontre os pares antes do tempo acabar.
9.  **2048:** Jogo de raciocínio lógico matemático.
10. **Quiz:** Perguntas e respostas sobre programação e cultura geral.
11. **Evade:** Jogo de esquiva de obstáculos caindo.

---

## 🔧 Dependências e Instalação

Para executar este projeto, você precisará do Python instalado e das seguintes bibliotecas:

```bash
pip install pygame pyrebase4 requests
````

> **Nota:** A biblioteca `typing-extensions` pode ser necessária dependendo da sua versão do Python.

-----

## ▶️ Como Executar

1.  Certifique-se de que a pasta `assets` (contendo imagens e sons) esteja no mesmo diretório do script.
2.  Execute o arquivo principal:

<!-- end list -->

```bash
python main.py
```

3.  No menu inicial:
      * Crie uma conta ou faça login.
      * Selecione o jogo desejado no grid.
      * Para ver os recordes, clique em "RANKINGS".

-----

## 🕵️ Segredos (Cheats)

O Hub possui um sistema de trapaças global. Se ativado, concede vantagens como vidas infinitas, dinheiro infinito ou "God Mode" na maioria dos jogos.

  * **Ativar Cheats:** Na tela de login ou menu, insira a sequência:
    `Cima, Cima, Baixo, Baixo, Esquerda, Direita, Esquerda, Direita, B, A` (Konami Code).

-----

## 📚 Referências e Créditos

  * **Assets:** Sprites e sons utilizados são de uso livre ou criados pela equipe.
  * **Firebase:** Utilizado para backend (Auth e Realtime Database).
  * **Professor:** José Eduardo Mendonça Xavier (IFES).

-----

*Projeto desenvolvido para a disciplina de Engenharia Mecânica / Programação - 2025.*

```
```
