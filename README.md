# 🎮 PyGame Tower Defense

**Versão do jogo Tower Defense usando Pygame**

---

## 📝 Proposta de Projeto

**Título:** *Defesa de Torre* (*Tower Defense*)

**Descrição:**
O jogo tower defense consiste em impedir que os inimigos cheguem ao fim do mapa colocando torres e canhões que ataquem ondas de inimigos.
O jogador constrói e posiciona essas torres ao longo do mapa, utilizando recursos (dinheiro) para derrotar os inimigos.
Possível possibilidade de expansão: Upgrade de torres; novos mapas;

---

## 👥 Componentes do Grupo

1. Ian Riki Taniguchi
2. João Alves Gava
3. João Vitor Del Pupo

---

## ⚡ Funcionalidades esperadas para o trabalho final

### 🗺 Mapa e caminho

* Mapa estático
* Caminho definido por "waypoints" que os inimigos seguem (cada waypoint é um ponto de quebra de direção)

### 🧟 Inimigos (Sprites)

* **Soldado:** vida baixa, velocidade média, recompensa baixa
* **Tanque:** vida alta, velocidade baixa, recompensa alta
* Inimigos surgem no início do caminho e seguem os waypoints até o fim
* Se um inimigo chegar ao fim, o jogador perde uma vida(começa com 20)

### 🏰 Torres (Sprites)

* **Torre de Flecha:** disparo rápido; dano baixo; alvo único; baixo custo
* **Canhão:** disparo lento; dano alto; dano em área; custo alto
* Torres atacam automaticamente inimigos dentro do alcance (funcionalidade)

### 🎮 Sistema de Jogo

* **Vidas:** jogador começa com 20
* **Dinheiro:** usado para construir torres, ganho ao derrotar inimigos
* **Ondas (Waves):** inimigos surgem em ondas progressivamente mais difíceis

### 📊 Interface (UI)

* Exibição constante das Vidas, Dinheiro e Número da onda/ total de ondas
* Menu simples para selecionar e posicionar torres (com reatividade)

---

## 🔧 Dependências

* **Pathlib:** carregamento de assets (sprites, sons, imagem de fundo)
* **Sons:**

  * Música de fundo (mp3 em loop)
  * Som de construção de torre (wav)
  * Som de disparo de torre (wav)
  * Som de inimigo destruído (wav)
  * Som de vida perdida (wav)

* **Estados do jogo:**

  * Tela de Início (instruções de como jogar e botão "Jogar")
  * Tela principal (jogo)
  * Tela de game over (vidas = 0)

---

## 🏗 Etapas da produção do jogo

### 1️⃣ Base e mapa

* Configuração da janela Pygame e estrutura de pastas (`assets/images`, `assets/sounds`)
* Implementação do `pathlib` para carregar o mapa estático (`assets/images/mapa.png`)
* Definição da lista de coordenadas (waypoints) do caminho (vetor, array)

### 2️⃣ O Inimigo e "algoritmo" de pathfinding

* Criação da classe `Enemy` (sprite)
* Implementação da lógica de movimento pelos waypoints
* Teste com um inimigo atravessando o mapa (e vários tbm)

### 3️⃣ Sistema de ondas e UI

* Implementação das ondas de inimigos
* Adição da UI (Vidas, Dinheiro, Wave)
* Lógica de perda de vida e ganho de dinheiro
* Adição do som de vida perdida (Dependência Gava)

### 4️⃣ As torres

* Criação da classe `Tower` (Torre de flechas)
* Definição de slots de construção no mapa (podem ser inseridos mais no vetor)
* Implementação da UI de compra de torres (tbm podem ser inseridos mais tipos)
* Lógica de detecção de alcance e mira automática (algoritmo usando vector e metodos do pygame mais complexos)

### 5️⃣ Disparos e dano

* Criação da classe `Projectile` 
* Projéteis seguem inimigos e causam dano 
* Inimigos removidos quando vida = 0, jogador ganha dinheiro (a depender do inimigo eliminado)
* Sons de disparo e destruição (.wav) 

### 6️⃣ Múltiplas torres e inimigos

* Adição do canhão (segunda torre) com lógica de dano em área (usando vector e metodos do pygame)
* Adição do tanque (segundo inimigo) com mais HP (anda mais devagar)
* Balanceamento dos custos, dano, HP e recompensas(podem-se adicionar mais)

### 7️⃣ Estados de jogo e aperfeiçoamento

* Música de fundo (mp3)
* Tela de início e game over (estados de jogo)
* Sistema de 5–10 ondas progressivas

### 8️⃣ Revisão final

* Limpeza do código
* Amplamente comentado e detalhado
* Cabeçalho no `main.py` com nomes, módulos e instruções de uso para usuários e desenvolvedores.

---

## 📚 Referências de Aprendizado

* Slides e materiais de apoio do professor **José Eduardo Mendonça Xavier**
* [Introdução ao Pygame – Linha de Código](http://www.linhadecodigo.com.br/artigo/503/introducao-ao-pygame.aspx)
* [Tutorial Pygame – Coders Legacy (traduzido)](https://coderslegacy-com.translate.goog/python/python-pygame-tutorial/?_x_tr_sl=auto&_x_tr_tl=pt-BR&_x_tr_hl=pt-BR)

---