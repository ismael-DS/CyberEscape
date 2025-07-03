# Cytoguard 🧬🛡️

Um minigame educativo sobre a batalha dos anticorpos contra vírus dentro do corpo humano — desenvolvido com Python e Pygame Zero.

## 📜 Sobre o jogo

Você é um anticorpo posicionado na linha de frente do sistema imunológico.
Sua missão: coletar medicamentos, destruir vírus e impedir que o corpo seja infectado.

Cytoguard é um jogo em estilo roguelike com visão top-down e movimentação por grade. Ele conta com:

* ✅ Geração procedural de fases
* ✅ Mecânica de ataque corpo-a-corpo (melee) e ataque à distância (laser)
* ✅ Sistema de animações para o personagem principal
* ✅ Inteligência simples de inimigos com movimentação automática
* ✅ Trilha sonora em loop e efeitos sonoros
* ✅ Interface gráfica com menus, HUD e game over

## 🎮 Como jogar

* Use as teclas direcionais (← ↑ → ↓) para mover o anticorpo.
* Pressione Z para atacar corpo-a-corpo (melee).
* Pressione ESPAÇO para atirar um laser (limitado a 3 disparos por fase).
* Colete todos os remédios 💊 para avançar de fase.
* Evite encostar nos inimigos! 👾

## 📦 Requisitos

* Python 3.7 ou superior
* Biblioteca Pygame Zero (pgzero)

Instale com:

```bash
pip install pgzero
```

## 🚀 Executando o jogo

Após instalar os requisitos:

```bash
pgzrun cytoguard.py
```

> Certifique-se de que as pastas images/ e sounds/ estejam na mesma pasta que o arquivo .py e contenham os sprites e sons corretos.

## 📁 Estrutura do projeto

```
cytoguard/
├── cytoguard.py
├── images/
│   ├── playeridle1.png ... playeridle5.png
│   ├── playerw1.png ... playerw4.png
│   ├── enemy.png
│   ├── wall.png
│   └── medicine.png
├── sounds/
│   ├── music.wav
│   ├── hit.wav
│   └── laser.wav
└── README.md
```

## 🧠 Conceitos aplicados

* Programação orientada a objetos (OOP)
* Animação de sprites
* Geração procedural com verificação de acessibilidade (BFS)
* Detecção de colisões e interação
* Estrutura modular e boas práticas de código

## 🧑‍💻 Autoria

Desenvolvido por Ismael Araújo para o processo seletivo de tutores de Python - Kodland (2025).
