import pgzrun
from collections import deque
import random
import time

WIDTH = 640
HEIGHT = 480
CELL_SIZE = 64
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

game_state = "intro"
music_on = True
walls = []
items = []
lasers = []
attack_cooldown = 1.0
current_level = 1

intro_active = True
intro_lines = [
    "Virus estao atacando este corpo.",
    "Voce esta como um anticorpo posicionado na linha de frente.",
    "Colete os medicamentos. Elimine os invasores.",
]
intro_index = 0
intro_timer = 0
intro_delay = 5

slash_timer = 0
slash_pos = None

enemy_move_timer = 0
enemy_move_delay = 0.5

class Player:
    def __init__(self, x, y):
        self.pos = [x, y]
        self.dir = [0, 1]
        self.ranged_shots = 3
        self.last_attack_time = 0
        self.state = "idle"
        self.idle_images = [f"playeridle{i}" for i in range(1, 6)]
        self.walk_images = [f"playerw{i}" for i in range(1, 5)]
        self.frame_index = 0
        self.animation_timer = 0
        self.actor = Actor(self.idle_images[0])

    def update_animation(self, dt):
        if self.state == "idle":
            pause_duration = 1.0
            frame_delay = 0.15
            self.animation_timer += dt
            if hasattr(self, "pausing_idle") and self.pausing_idle:
                if self.animation_timer >= pause_duration:
                    self.animation_timer = 0
                    self.frame_index = 0
                    self.actor.image = self.idle_images[self.frame_index]
                    self.pausing_idle = False
            else:
                if self.animation_timer >= frame_delay:
                    self.animation_timer = 0
                    self.frame_index += 1
                    if self.frame_index >= len(self.idle_images):
                        self.frame_index = 0
                        self.pausing_idle = True
                    self.actor.image = self.idle_images[self.frame_index]
        elif self.state == "walk":
            frame_delay = 0.05
            self.animation_timer += dt
            if self.animation_timer >= frame_delay:
                self.animation_timer = 0
                self.frame_index += 1
                total_walk_frames = len(self.walk_images) * 2
                if self.frame_index >= total_walk_frames:
                    self.frame_index = 0
                    self.state = "idle"
                    self.pausing_idle = False
                    self.actor.image = self.idle_images[0]
                    return
                frame = self.walk_images[self.frame_index % len(self.walk_images)]
                self.actor.image = frame

    def draw(self):
        px = self.pos[0] * CELL_SIZE + CELL_SIZE // 2
        py = self.pos[1] * CELL_SIZE + CELL_SIZE // 2
        self.actor.pos = (px, py)
        if self.dir == [0, -1]: self.actor.angle = 180
        elif self.dir == [1, 0]: self.actor.angle = 90
        elif self.dir == [0, 1]: self.actor.angle = 0
        elif self.dir == [-1, 0]: self.actor.angle = 270
        self.actor.draw()

    def melee_attack(self, enemies):
        sounds.hit.play()
        target = [self.pos[0] + self.dir[0], self.pos[1] + self.dir[1]]
        global slash_timer, slash_pos
        slash_pos = target[:]
        slash_timer = 0.15
        for enemy in enemies[:]:
            if enemy.pos == target:
                enemies.remove(enemy)
                break

    def fire_laser(self, lasers):
        if self.ranged_shots > 0:
            sounds.laser.play()
            lasers.append({"pos": self.pos[:], "dir": self.dir[:]})
            self.ranged_shots -= 1

class Enemy:
    def __init__(self, x, y, dx, dy):
        self.pos = [x, y]
        self.dir = [dx, dy]
        self.actor = Actor("enemy")

    def draw(self):
        ex = self.pos[0] * CELL_SIZE + CELL_SIZE // 2
        ey = self.pos[1] * CELL_SIZE + CELL_SIZE // 2
        self.actor.pos = (ex, ey)
        self.actor.draw()

    def move(self, walls):
        x, y = self.pos
        dx, dy = self.dir
        new_x = x + dx
        new_y = y + dy
        if not (0 <= new_x < GRID_WIDTH) or (new_x, y) in walls:
            self.dir[0] *= -1
        else:
            self.pos[0] = new_x
        if not (0 <= new_y < GRID_HEIGHT) or (x, new_y) in walls:
            self.dir[1] *= -1
        else:
            self.pos[1] = new_y

def draw_gradient_background():
    from math import sin, pi
    for y in range(HEIGHT):
        t = y / HEIGHT
        pulse = int(40 + 30 * sin(t * pi * 4))
        r = 120 + pulse
        g = 40 + pulse // 2
        b = 60 + pulse // 3
        screen.draw.line((0, y), (WIDTH, y), (r, g, b))

player = Player(0, 0)
enemies = []
buttons = [
    {"label": "Start Game", "pos": (WIDTH // 2, 180), "action": "start"},
    {"label": "Sound On/Off", "pos": (WIDTH // 2, 240), "action": "toggle_sound"},
    {"label": "Exit", "pos": (WIDTH // 2, 300), "action": "exit"},
]
retry_button = {"label": "Retry", "pos": (WIDTH // 2, 300), "action": "retry"}
last_time = time.time()

def draw():
    screen.clear()
    if game_state == "intro": draw_intro()
    elif game_state == "menu": draw_menu()
    elif game_state == "game": draw_game()
    elif game_state == "game_over": draw_game_over()

def draw_intro():
    screen.fill((10, 10, 20))
    screen.draw.text("Cytoguard", center=(WIDTH//2, 80), fontsize=60, color="cyan")
    if intro_index < len(intro_lines):
        screen.draw.textbox(intro_lines[intro_index], Rect(WIDTH//2 - 220, HEIGHT//2 - 20, 440, 60), color="white", background="black")

def draw_menu():
    screen.fill((10, 10, 20))
    screen.draw.text("Cytoguard", center=(WIDTH//2, 80), fontsize=60, color="cyan")
    for btn in buttons:
        screen.draw.textbox(btn["label"], Rect(btn["pos"][0]-100, btn["pos"][1]-20, 200, 40), color="white", background="black")

def draw_game_over():
    screen.fill((0, 0, 0))
    screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 60), fontsize=60, color="red")
    screen.draw.textbox(retry_button["label"], Rect(retry_button["pos"][0]-100, retry_button["pos"][1]-20, 200, 40), color="white", background="darkred")

def draw_game():
    draw_gradient_background()
    for wx, wy in walls:
        Actor("wall", (wx * CELL_SIZE + CELL_SIZE // 2, wy * CELL_SIZE + CELL_SIZE // 2)).draw()
    for ix, iy in items:
        Actor("medicine", (ix * CELL_SIZE + CELL_SIZE // 2, iy * CELL_SIZE + CELL_SIZE // 2)).draw()
    for laser in lasers:
        lx = laser["pos"][0] * CELL_SIZE + CELL_SIZE // 2
        ly = laser["pos"][1] * CELL_SIZE + CELL_SIZE // 2
        screen.draw.filled_circle((lx, ly), 8, "yellow")
    if slash_pos:
        x1 = player.pos[0] * CELL_SIZE + CELL_SIZE // 2
        y1 = player.pos[1] * CELL_SIZE + CELL_SIZE // 2
        x2 = slash_pos[0] * CELL_SIZE + CELL_SIZE // 2
        y2 = slash_pos[1] * CELL_SIZE + CELL_SIZE // 2
        screen.draw.line((x1, y1), (x2, y2), (255, 255, 100))
    player.draw()
    for enemy in enemies:
        enemy.draw()
    draw_hud()

def update():
    global intro_index, game_state, intro_timer, slash_timer, slash_pos, enemy_move_timer, last_time
    now = time.time()
    if game_state == "intro":
        if now - intro_timer > intro_delay:
            intro_index += 1
            intro_timer = now
            if intro_index >= len(intro_lines):
                game_state = "menu"
        return
    if game_state != "game": return
    dt = now - last_time
    last_time = now
    player.update_animation(dt)
    if slash_timer > 0:
        slash_timer -= dt
        if slash_timer <= 0:
            slash_pos = None
    enemy_move_timer += dt
    if enemy_move_timer >= enemy_move_delay:
        enemy_move_timer = 0
        for enemy in enemies:
            enemy.move(walls)
    update_lasers()
    check_collision()

def on_key_down(key):
    if game_state != "game": return
    dx, dy = 0, 0
    if key == keys.LEFT: dx = -1
    elif key == keys.RIGHT: dx = 1
    elif key == keys.UP: dy = -1
    elif key == keys.DOWN: dy = 1
    elif key == keys.Z:
        if time.time() - player.last_attack_time >= attack_cooldown:
            player.melee_attack(enemies)
            player.last_attack_time = time.time()
        return
    elif key == keys.SPACE:
        player.fire_laser(lasers)
        return
    new_x = player.pos[0] + dx
    new_y = player.pos[1] + dy
    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and (new_x, new_y) not in walls:
        player.pos = [new_x, new_y]
        player.dir = [dx, dy]
        player.state = "walk"
        player.frame_index = 0
        player.animation_timer = 0
        check_item_collection()

def update_lasers():
    for laser in lasers[:]:
        laser["pos"][0] += laser["dir"][0]
        laser["pos"][1] += laser["dir"][1]
        if not (0 <= laser["pos"][0] < GRID_WIDTH and 0 <= laser["pos"][1] < GRID_HEIGHT):
            lasers.remove(laser)
            continue
        for enemy in enemies:
            if enemy.pos == laser["pos"]:
                enemies.remove(enemy)
                lasers.remove(laser)
                break

def check_collision():
    global game_state
    for enemy in enemies:
        if enemy.pos == player.pos:
            game_state = "game_over"

def on_mouse_down(pos):
    global game_state, music_on, intro_timer
    if game_state == "menu":
        for btn in buttons:
            rect = Rect(btn["pos"][0]-100, btn["pos"][1]-20, 200, 40)
            if rect.collidepoint(pos):
                if btn["action"] == "start":
                    reset_game()
                    game_state = "game"
                elif btn["action"] == "toggle_sound":
                    music_on = not music_on
                    if music_on:
                        sounds.music.play(loops=-1)
                    else:
                        sounds.music.stop()
                elif btn["action"] == "exit":
                    exit()
    elif game_state == "game_over":
        rect = Rect(retry_button["pos"][0]-100, retry_button["pos"][1]-20, 200, 40)
        if rect.collidepoint(pos):
            game_state = "menu"
    elif game_state == "intro":
        intro_timer = time.time()
        if music_on:
            sounds.music.play(loops=-1)

def reset_game():
    global player, enemies, walls, items, lasers, current_level
    player = Player(0, 0)
    lasers.clear()
    walls.clear()
    items.clear()
    enemies.clear()
    num_enemies = min(3, 1 + (current_level - 1) // 2)
    num_items = min(5, current_level)
    num_walls = min(10, 4 + current_level)
    while True:
        walls = [(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)) for _ in range(num_walls)]
        items = []
        while len(items) < num_items:
            ix, iy = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if (ix, iy) not in walls and (ix, iy) != tuple(player.pos) and (ix, iy) not in items:
                items.append((ix, iy))
        enemies.clear()
        while len(enemies) < num_enemies:
            ex, ey = random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)
            if (ex, ey) not in walls and [ex, ey] != player.pos:
                dir = random.choice([[1, 0], [-1, 0], [0, 1], [0, -1]])
                enemies.append(Enemy(ex, ey, dir[0], dir[1]))
        if is_reachable(player.pos, set(items), set(walls)):
            break

def check_item_collection():
    global current_level
    if tuple(player.pos) in items:
        sounds.medicine.play()
        items.remove(tuple(player.pos))
        if not items:
            current_level += 1
            reset_game()

def draw_hud():
    screen.draw.text(f"Fase {current_level}", topleft=(10, 10), fontsize=30, color="white")
    screen.draw.text(f"Tiros: {player.ranged_shots}", topleft=(10, 40), fontsize=24, color="yellow")

def is_reachable(start, goals, walls):
    visited = set()
    queue = deque([tuple(start)])
    visited.add(tuple(start))
    while queue:
        x, y = queue.popleft()
        if (x, y) in goals:
            goals.remove((x, y))
            if not goals:
                return True
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if (nx, ny) not in visited and (nx, ny) not in walls:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
    return False

pgzrun.go()
