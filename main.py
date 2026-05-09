import pygame
import random
import os
import sys

pygame.init()
pygame.mixer.init()

# =========================
# НАСТРОЙКИ
# =========================
WIDTH, HEIGHT = 800, 600
BLOCK = 32
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Blue Record Edition")
clock = pygame.time.Clock()

IMG = "Imgs"
SND = "sounds"


def load_img(name):
    path = os.path.join(IMG, name)
    return pygame.image.load(path) if os.path.exists(path) else pygame.Surface((BLOCK, BLOCK))


background = load_img("bg_1.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


# =========================
# ЧАСТИЦЫ (ЭФФЕКТЫ)
# =========================
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.dx = random.uniform(-3, 3)
        self.dy = random.uniform(-3, 3)
        self.life = 255
        self.color = color

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 12

    def draw(self, surf):
        if self.life > 0:
            p_surf = pygame.Surface((4, 4))
            p_surf.set_alpha(self.life)
            p_surf.fill(self.color)
            surf.blit(p_surf, (self.x, self.y))


particles = []

# =========================
# МУЗЫКАЛЬНАЯ СИСТЕМА
# =========================
SONGS = [
    "Atlxs & Mxzi & Itamar Mc - Montagem Ladrao (Slowed).mp3",
    "naomi-space-super-slowed.mp3",
    "C418 - Aria Math (Minecraft Volume Beta).mp3"
]
current_song_idx = 0


def prepare_music():
    global current_song_idx
    pygame.mixer.music.stop()
    path = os.path.join(SND, SONGS[current_song_idx])
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
        except:
            pass


def start_music():
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)


prepare_music()


# =========================
# КЛАССЫ
# =========================
class Snake:
    def __init__(self):
        self.head = pygame.transform.scale(load_img("removebg-preview (1).png"), (BLOCK, BLOCK))
        self.reset()

    def reset(self):
        self.body = [(WIDTH // 2 // BLOCK * BLOCK, HEIGHT // 2 // BLOCK * BLOCK)]
        self.dx, self.dy = 0, 0
        self.last_dx, self.last_dy = 0, 0

    def move(self):
        self.last_dx, self.last_dy = self.dx, self.dy
        self.body.insert(0, (self.body[0][0] + self.dx, self.body[0][1] + self.dy))

    def trim(self):
        if len(self.body) > 1: self.body.pop()

    def draw(self):
        screen.blit(self.head, self.body[0])
        for part in self.body[1:]:
            pygame.draw.rect(screen, (0, 200, 0), (part[0], part[1], BLOCK, BLOCK), border_radius=8)

    def dead(self, is_secret):
        x, y = self.body[0]
        if is_secret:
            if x < 0:
                self.body[0] = (WIDTH - BLOCK, y)
            elif x >= WIDTH:
                self.body[0] = (0, y)
            elif y < 0:
                self.body[0] = (x, HEIGHT - BLOCK)
            elif y >= HEIGHT:
                self.body[0] = (x, 0)
            return self.body[0] in self.body[1:]
        return x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT or self.body[0] in self.body[1:]


class Apple:
    def __init__(self):
        self.img_reg = pygame.transform.scale(load_img("image-removebg-preview.png"), (BLOCK, BLOCK))
        self.img_gold = pygame.transform.scale(load_img("image-removebg-preview (1).png"), (BLOCK, BLOCK))
        self.spawn(10000)

    def spawn(self, time_limit):
        self.x = random.randrange(0, WIDTH - BLOCK, BLOCK)
        self.y = random.randrange(0, HEIGHT - BLOCK, BLOCK)
        self.is_gold = random.random() < 0.3
        self.timer = time_limit
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        if self.is_gold:
            passed = pygame.time.get_ticks() - self.spawn_time
            if passed > self.timer:
                self.is_gold = False

    def draw(self):
        img = self.img_gold if self.is_gold else self.img_reg
        screen.blit(img, (self.x, self.y))
        if self.is_gold:
            passed = pygame.time.get_ticks() - self.spawn_time
            width = BLOCK * (1 - passed / self.timer)
            pygame.draw.rect(screen, (255, 215, 0), (self.x, self.y - 8, width, 4))


# =========================
# ПЕРЕМЕННЫЕ
# =========================
snake, apple = Snake(), Apple()
MODE = None
score, best_record = 0, 0
game_over = False
secret_unlocked, show_secret_menu = False, False
last_move, MOVE_DELAY = pygame.time.get_ticks(), 120
GOLD_TIME = 10000
font_b = pygame.font.SysFont("Arial", 60, bold=True)
font_s = pygame.font.SysFont("Arial", 30, bold=True)

music_buttons = [pygame.Rect(WIDTH - 160, HEIGHT - 150, 140, 40),
                 pygame.Rect(WIDTH - 160, HEIGHT - 100, 140, 40),
                 pygame.Rect(WIDTH - 160, HEIGHT - 50, 140, 40)]

# =========================
# ЦИКЛ
# =========================
while True:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()

    if MODE is None:
        screen.blit(background, (0, 0))
        screen.blit(font_b.render("SNAKE GAME", True, (255, 255, 255)), (WIDTH // 2 - 180, 100))

        screen.blit(font_s.render("1 - NORMAL (10s Gold)", True, (0, 255, 0)), (WIDTH // 2 - 130, 230))
        screen.blit(font_s.render("2 - MEDIUM (7s Gold)", True, (255, 255, 0)), (WIDTH // 2 - 130, 280))
        screen.blit(font_s.render("3 - HARD (4s Gold)", True, (255, 50, 50)), (WIDTH // 2 - 130, 330))

        for i, btn in enumerate(music_buttons):
            color = (50, 120, 255) if current_song_idx == i else (80, 80, 80)
            pygame.draw.rect(screen, color, btn, border_radius=8)
            screen.blit(font_s.render(f"Song {i + 1}", True, (255, 255, 255)), (btn.x + 25, btn.y + 5))

        pygame.display.update()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(music_buttons):
                    if btn.collidepoint(event.pos): current_song_idx = i; prepare_music()
            if event.type == pygame.KEYDOWN:
                snake.reset();
                score = 0
                if event.key == pygame.K_1: MODE = "normal"; MOVE_DELAY = 130; GOLD_TIME = 10000; start_music()
                if event.key == pygame.K_2: MODE = "medium"; MOVE_DELAY = 90; GOLD_TIME = 7000; start_music()
                if event.key == pygame.K_3: MODE = "hard"; MOVE_DELAY = 60; GOLD_TIME = 4000; start_music()
                apple.spawn(GOLD_TIME)
        continue

    if show_secret_menu:
        screen.blit(background, (0, 0))
        screen.blit(font_b.render("SECRET UNLOCKED!", True, (255, 0, 255)), (140, 180))
        screen.blit(font_s.render("4 - Secret Mode | C - Continue", True, (255, 255, 255)), (140, 300))
        pygame.display.update()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4: MODE = "secret"; show_secret_menu = False; pygame.mixer.music.unpause()
                if event.key == pygame.K_c: show_secret_menu = False; pygame.mixer.music.unpause()
        continue

    if game_over:
        if score > best_record: best_record = score
        screen.blit(background, (0, 0))
        screen.blit(font_b.render("GAME OVER", True, (255, 0, 0)), (WIDTH // 2 - 170, 180))
        screen.blit(font_s.render(f"Your Score: {score}", True, (255, 255, 255)), (WIDTH // 2 - 90, 260))
        screen.blit(font_s.render("R - Restart | G - Menu", True, (255, 255, 255)), (WIDTH // 2 - 130, 330))
        pygame.display.update()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: snake.reset(); apple.spawn(
                    GOLD_TIME); score = 0; game_over = False; start_music()
                if event.key == pygame.K_g: MODE = None; game_over = False; secret_unlocked = False; score = 0; pygame.mixer.music.stop()
        continue

    # --- УПРАВЛЕНИЕ ---
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and snake.last_dx != BLOCK:
        snake.dx, snake.dy = -BLOCK, 0
    elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and snake.last_dx != -BLOCK:
        snake.dx, snake.dy = BLOCK, 0
    elif (keys[pygame.K_w] or keys[pygame.K_UP]) and snake.last_dy != BLOCK:
        snake.dx, snake.dy = 0, -BLOCK
    elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and snake.last_dy != -BLOCK:
        snake.dx, snake.dy = 0, BLOCK

    # --- ЛОГИКА ---
    apple.update()
    now = pygame.time.get_ticks()
    if now - last_move > MOVE_DELAY:
        last_move = now
        if snake.dx != 0 or snake.dy != 0:
            snake.move()
            if abs(snake.body[0][0] - apple.x) < BLOCK and abs(snake.body[0][1] - apple.y) < BLOCK:
                p_color = (255, 215, 0) if apple.is_gold else (255, 0, 0)
                for _ in range(15): particles.append(Particle(apple.x + 16, apple.y + 16, p_color))

                score += 3 if apple.is_gold else 1
                apple.spawn(GOLD_TIME)
                if score >= 50 and not secret_unlocked:
                    secret_unlocked = True;
                    show_secret_menu = True;
                    pygame.mixer.music.pause()
            else:
                snake.trim()
            if snake.dead(MODE == "secret"): game_over = True; pygame.mixer.music.stop()

    for p in particles[:]:
        p.update()
        if p.life <= 0: particles.remove(p)

    # --- ОТРИСОВКА ---
    screen.blit(background, (0, 0))
    for p in particles: p.draw(screen)
    apple.draw()
    snake.draw()
    screen.blit(font_s.render(f"Score: {score}", True, (255, 255, 0)), (10, 10))
    # СИНИЙ РЕКОРД
    screen.blit(font_s.render(f"Best: {best_record}", True, (0, 100, 255)), (10, 45))
    pygame.display.update()
