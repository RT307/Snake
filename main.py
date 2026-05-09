import pygame
import random
import os
import sys

pygame.init()

# =========================
# НАСТРОЙКИ
# =========================
WIDTH = 800
HEIGHT = 600
BLOCK = 32

FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()

# =========================
# ПАПКА IMG
# =========================
IMG = os.path.join(os.path.dirname(__file__), "Imgs")

def load_img(name):
    return pygame.image.load(os.path.join(IMG, name))

background = load_img("bg_1.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# =========================
# РЕЖИМЫ
# =========================
MODE = None

MOVE_DELAY = 120
speed_level = 0

def set_mode(mode):
    global MOVE_DELAY, MODE, speed_level

    MODE = mode
    speed_level = 0

    if mode == "normal":
        MOVE_DELAY = 120

    elif mode == "medium":
        MOVE_DELAY = 120

    elif mode == "hard":
        MOVE_DELAY = 40  # x3 скорость

def update_speed(score):
    global MOVE_DELAY, speed_level

    if MODE != "medium":
        return

    new_level = score // 5

    if new_level > speed_level:
        speed_level = new_level
        MOVE_DELAY = int(MOVE_DELAY * 0.9)

        if MOVE_DELAY < 50:
            MOVE_DELAY = 50

# =========================
# ЗМЕЙКА
# =========================
class Snake:
    def __init__(self):
        self.head = load_img("removebg-preview__1_-removebg-preview.png")
        self.head = pygame.transform.scale(self.head, (BLOCK, BLOCK))

        self.body = [(100, 100)]
        self.dx = 0
        self.dy = 0

        self.last_dx = 0
        self.last_dy = 0

    def move(self):
        self.last_dx = self.dx
        self.last_dy = self.dy

        x = self.body[0][0] + self.dx
        y = self.body[0][1] + self.dy
        self.body.insert(0, (x, y))

    def trim(self):
        self.body.pop()

    def draw(self):
        screen.blit(self.head, self.body[0])

        for part in self.body[1:]:
            pygame.draw.rect(
                screen,
                (0, 200, 0),
                (part[0], part[1], BLOCK, BLOCK),
                border_radius=8
            )

    def dead(self):
        x, y = self.body[0]
        return x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT

    def hit_self(self):
        return self.body[0] in self.body[1:]


# =========================
# ЯБЛОКО
# =========================
class Apple:
    def __init__(self):
        self.image = load_img("image-removebg-preview (10).png")
        self.image = pygame.transform.scale(self.image, (BLOCK, BLOCK))
        self.spawn()

    def spawn(self):
        self.x = random.randrange(0, WIDTH - BLOCK, BLOCK)
        self.y = random.randrange(0, HEIGHT - BLOCK, BLOCK)

    def draw(self):
        screen.blit(self.image, (self.x, self.y))


snake = Snake()
apple = Apple()

running = True
game_over = False

score = 0
best_score = 0

last_move = pygame.time.get_ticks()

font_big = pygame.font.SysFont("Arial", 60)
font_small = pygame.font.SysFont("Arial", 30)

# =========================
# ИГРА
# =========================
while running:

    clock.tick(FPS)

    # =========================
    # МЕНЮ ВЫБОРА РЕЖИМА
    # =========================
    if MODE is None:
        screen.blit(background, (0, 0))

        title = font_big.render("SNAKE GAME", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - 200, 100))

        text1 = font_small.render("1 - NORMAL", True, (0, 255, 0))
        text2 = font_small.render("2 - MEDIUM", True, (255, 255, 0))
        text3 = font_small.render("3 - HARD (x3 speed)", True, (255, 0, 0))

        screen.blit(text1, (WIDTH//2 - 120, 250))
        screen.blit(text2, (WIDTH//2 - 120, 300))
        screen.blit(text3, (WIDTH//2 - 160, 350))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    set_mode("normal")
                if event.key == pygame.K_2:
                    set_mode("medium")
                if event.key == pygame.K_3:
                    set_mode("hard")

        continue

    # =========================
    # GAME OVER
    # =========================
    if game_over:
        screen.blit(background, (0, 0))
        screen.blit(snake.head, snake.body[0])

        text = font_big.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, (WIDTH//2 - 180, HEIGHT//2 - 120))

        score_text = font_small.render(f"Score: {score}", True, (255, 255, 0))
        screen.blit(score_text, (WIDTH//2 - 80, HEIGHT//2 - 60))

        best_text = font_small.render(f"Best: {best_score}", True, (0, 255, 255))
        screen.blit(best_text, (WIDTH//2 - 80, HEIGHT//2 - 20))

        restart_text = font_small.render("R - Restart | G - Menu", True, (255, 255, 255))
        screen.blit(restart_text, (WIDTH//2 - 160, HEIGHT//2 + 40))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                # 🔁 restart
                if event.key == pygame.K_r:
                    snake = Snake()
                    apple.spawn()
                    score = 0
                    game_over = False

                # 🔄 back to menu
                if event.key == pygame.K_g:
                    snake = Snake()
                    apple.spawn()
                    score = 0
                    game_over = False
                    MODE = None

        continue

    # =========================
    # СОБЫТИЯ
    # =========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # =========================
    # УПРАВЛЕНИЕ
    # =========================
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a] and snake.last_dx != BLOCK:
        snake.dx = -BLOCK
        snake.dy = 0

    if keys[pygame.K_d] and snake.last_dx != -BLOCK:
        snake.dx = BLOCK
        snake.dy = 0

    if keys[pygame.K_w] and snake.last_dy != BLOCK:
        snake.dx = 0
        snake.dy = -BLOCK

    if keys[pygame.K_s] and snake.last_dy != -BLOCK:
        snake.dx = 0
        snake.dy = BLOCK

    # =========================
    # ДВИЖЕНИЕ
    # =========================
    now = pygame.time.get_ticks()

    if now - last_move > MOVE_DELAY:
        last_move = now

        snake.move()

        # 🍎 еда
        if abs(snake.body[0][0] - apple.x) < BLOCK and abs(snake.body[0][1] - apple.y) < BLOCK:
            apple.spawn()
            score += 1
            update_speed(score)
        else:
            snake.trim()

        # 💀 смерть
        if snake.dead() or snake.hit_self():
            game_over = True
            if score > best_score:
                best_score = score

    # =========================
    # ОТРИСОВКА
    # =========================
    screen.blit(background, (0, 0))

    apple.draw()
    snake.draw()

    score_text = font_small.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 10))

    pygame.display.update()

pygame.quit()