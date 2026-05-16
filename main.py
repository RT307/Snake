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
SND = "Song"


def load_img(name, color_fallback=(255, 0, 0)):
    """Загружает картинку. Если файла нет, создает цветной квадрат."""
    path = os.path.join(IMG, name)
    if os.path.exists(path):
        return pygame.image.load(path)
    else:
        print(f"Предупреждение: Файл {name} не найден в папке {IMG}. Используется заглушка.")
        surf = pygame.Surface((BLOCK, BLOCK))
        surf.fill(color_fallback)
        return surf


# Загрузка фона
background = load_img("bg_1.jpg", color_fallback=(30, 30, 40))
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
music_loaded = False


def prepare_music():
    global current_song_idx, music_loaded
    music_loaded = False
    pygame.mixer.music.stop()

    path = os.path.join(SND, SONGS[current_song_idx])
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.5)
            music_loaded = True
        except Exception as e:
            print(f"Ошибка загрузки трека {SONGS[current_song_idx]}: {e}")
    else:
        print(f"Файл не найден по пути: {path}")


def start_music():
    if music_loaded and not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)


prepare_music()


# =========================
# КЛАССЫ ИГРЫ
# =========================
class Snake:
    def __init__(self):
        self.head = load_img("removebg-preview__1_-removebg-preview.png", color_fallback=(0, 255, 0))
        self.head = pygame.transform.scale(self.head, (BLOCK, BLOCK))
        self.reset()

    def reset(self):
        self.body = [(WIDTH // 2 // BLOCK * BLOCK, HEIGHT // 2 // BLOCK * BLOCK)]
        self.dx, self.dy = 0, 0
        self.last_dx, self.last_dy = 0, 0

    def move(self):
        self.last_dx, self.last_dy = self.dx, self.dy
        self.body.insert(0, (self.body[0][0] + self.dx, self.body[0][1] + self.dy))

    def trim(self):
        if len(self.body) > 1:
            self.body.pop()

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
        self.img_reg = load_img("image-removebg-preview (10).png", color_fallback=(255, 0, 0))
        self.img_reg = pygame.transform.scale(self.img_reg, (BLOCK, BLOCK))

        self.img_gold = load_img("image-removebg-preview (1) (1).png", color_fallback=(255, 215, 0))
        self.img_gold = pygame.transform.scale(self.img_gold, (BLOCK, BLOCK))

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
# УПРАВЛЕНИЕ ПЕРЕМЕННЫМИ
# =========================
snake, apple = Snake(), Apple()
MODE = None  # Базовый режим ("normal", "medium", "hard", "secret", "reverse", "rules")
score, best_record = 0, 0
game_over = False

# Флаги уровней и меню
unlocked_lvl4, unlocked_lvl5 = False, False
show_secret_menu = False
current_secret_trigger = 4

# ТАЙМЕРЫ И СКОРОСТЬ ДЛЯ РЕЖИМОВ 4 И 5
mode_timer_start = 0
is_mode_active = True
base_move_delay = 130  # Переменная для запоминания начальной скорости уровня
ACTIVE_DURATION = 25000  # Секретный режим работает (25 секунд)
COOLDOWN_DURATION = 20000  # Перерыв, игра как обычно (20 секунд)

last_move, MOVE_DELAY = pygame.time.get_ticks(), 120
GOLD_TIME = 10000
font_b = pygame.font.SysFont("Arial", 80, bold=True)  # Сделали чуть крупнее для SNAKE
font_s = pygame.font.SysFont("Arial", 30, bold=True)

music_buttons = [
    pygame.Rect(WIDTH - 160, HEIGHT - 150, 140, 40),
    pygame.Rect(WIDTH - 160, HEIGHT - 100, 140, 40),
    pygame.Rect(WIDTH - 160, HEIGHT - 50, 140, 40)
]

# =========================
# ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ
# =========================
while True:
    clock.tick(FPS)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # --- ЭКРАН ПРАВИЛ (УКРАИНСКИЙ ЯЗЫК) ---
    if MODE == "rules":
        screen.blit(background, (0, 0))
        r_title = font_b.render("ПРАВИЛА", True, (255, 255, 255))
        screen.blit(r_title, (WIDTH // 2 - r_title.get_width() // 2, 50))

        ukr_rules = [
            "• Керування: WASD або стрілочки.",
            "• Червоне яблуко: +1 бал.",
            "• Золоте яблуко: +3 бали (час обмежений!).",
            "• Набери 50 та 70 балів для секретів.",
            "• Не врізайся у стіни або свій хвіст.",
            "",
            "Натисни ESC або G для виходу в меню."
        ]
        for i, line in enumerate(ukr_rules):
            color = (0, 255, 255) if "Натисни" in line else (220, 220, 220)
            txt = font_s.render(line, True, color)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 180 + i * 40))

        pygame.display.update()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_g]:
                    MODE = None
        continue

    # --- ГЛАВНОЕ МЕНЮ ---
    if MODE is None:
        screen.blit(background, (0, 0))

        # Рендерим заголовок "SNAKE"
        title_text = "SNAKE"
        title_surf = font_b.render(title_text, True, (0, 255, 127))
        shadow_surf = font_b.render(title_text, True, (0, 60, 30))

        # Центрирование
        title_x = WIDTH // 2 - title_surf.get_width() // 2
        screen.blit(shadow_surf, (title_x + 5, 85))  # Тень
        screen.blit(title_surf, (title_x, 80))  # Основной текст

        # Опции выбора
        screen.blit(font_s.render("1 - NORMAL (10s Gold)", True, (0, 255, 0)), (WIDTH // 2 - 130, 220))
        screen.blit(font_s.render("2 - MEDIUM (7s Gold)", True, (255, 255, 0)), (WIDTH // 2 - 130, 260))
        screen.blit(font_s.render("3 - HARD (4s Gold)", True, (255, 50, 50)), (WIDTH // 2 - 130, 300))
        screen.blit(font_s.render("H - ПРАВИЛА (Rules)", True, (255, 255, 255)), (WIDTH // 2 - 130, 350))

        for i, btn in enumerate(music_buttons):
            color = (50, 120, 255) if current_song_idx == i else (80, 80, 80)
            pygame.draw.rect(screen, color, btn, border_radius=8)
            screen.blit(font_s.render(f"Song {i + 1}", True, (255, 255, 255)), (btn.x + 25, btn.y + 5))

        pygame.display.update()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(music_buttons):
                    if btn.collidepoint(event.pos):
                        current_song_idx = i
                        prepare_music()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    MODE = "rules"
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    snake.reset()
                    score = 0
                    unlocked_lvl4 = False
                    unlocked_lvl5 = False

                    if event.key == pygame.K_1:
                        MODE = "normal"
                        MOVE_DELAY = 130
                        GOLD_TIME = 10000
                    elif event.key == pygame.K_2:
                        MODE = "medium"
                        MOVE_DELAY = 90
                        GOLD_TIME = 7000
                    elif event.key == pygame.K_3:
                        MODE = "hard"
                        MOVE_DELAY = 60
                        GOLD_TIME = 4000

                    base_move_delay = MOVE_DELAY
                    apple.spawn(GOLD_TIME)
                    start_music()
        continue

    # --- ОСТАЛЬНАЯ ЧАСТЬ КОДА БЕЗ ИЗМЕНЕНИЙ ---
    if show_secret_menu:
        screen.blit(background, (0, 0))
        screen.blit(font_b.render("SECRET!", True, (255, 0, 255)),
                    (WIDTH // 2 - 140, 130))  # Тоже поменял на центрирование

        if current_secret_trigger == 4:
            screen.blit(font_s.render("4 - Secret Mode", True, (0, 255, 255)), (140, 240))
            screen.blit(font_s.render("C - Continue Level", True, (255, 255, 255)), (140, 300))
        elif current_secret_trigger == 5:
            screen.blit(font_s.render("4 - Secret Mode", True, (0, 255, 255)), (140, 240))
            screen.blit(font_s.render("5 - Reverse Mode", True, (255, 128, 0)), (140, 300))
            screen.blit(font_s.render("C - Continue Level", True, (255, 255, 255)), (140, 360))

        pygame.display.update()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_4:
                    MODE = "secret"
                    show_secret_menu = False
                    is_mode_active = True
                    MOVE_DELAY = 130
                    mode_timer_start = pygame.time.get_ticks()
                    pygame.mixer.music.unpause()
                if event.key == pygame.K_5 and current_secret_trigger == 5:
                    MODE = "reverse"
                    show_secret_menu = False
                    is_mode_active = True
                    MOVE_DELAY = 130
                    mode_timer_start = pygame.time.get_ticks()
                    pygame.mixer.music.unpause()
                if event.key == pygame.K_c:
                    show_secret_menu = False
                    pygame.mixer.music.unpause()
        continue

    if game_over:
        if score > best_record:
            best_record = score
        screen.blit(background, (0, 0))
        screen.blit(font_b.render("GAME OVER", True, (255, 0, 0)), (WIDTH // 2 - 200, 180))
        screen.blit(font_s.render(f"Your Score: {score}", True, (255, 255, 255)), (WIDTH // 2 - 90, 280))
        screen.blit(font_s.render("R - Restart | G - Menu", True, (255, 255, 255)), (WIDTH // 2 - 130, 350))
        pygame.display.update()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    snake.reset()
                    apple.spawn(GOLD_TIME)
                    score = 0
                    game_over = False
                    unlocked_lvl4 = False
                    unlocked_lvl5 = False
                    start_music()
                if event.key == pygame.K_g:
                    MODE = None
                    game_over = False
                    unlocked_lvl4 = False
                    unlocked_lvl5 = False
                    score = 0
                    pygame.mixer.music.stop()
        continue

    current_time = pygame.time.get_ticks()
    time_left_sec = 0.0

    if MODE in ["secret", "reverse"]:
        elapsed = current_time - mode_timer_start
        if is_mode_active:
            MOVE_DELAY = 130
            time_left_sec = max(0.0, (ACTIVE_DURATION - elapsed) / 1000.0)
            if elapsed >= ACTIVE_DURATION:
                is_mode_active = False
                mode_timer_start = current_time
        else:
            MOVE_DELAY = base_move_delay
            time_left_sec = max(0.0, (COOLDOWN_DURATION - elapsed) / 1000.0)
            if elapsed >= COOLDOWN_DURATION:
                is_mode_active = True
                mode_timer_start = current_time

    keys = pygame.key.get_pressed()
    press_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    press_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    press_up = keys[pygame.K_w] or keys[pygame.K_UP]
    press_down = keys[pygame.K_s] or keys[pygame.K_DOWN]

    if MODE == "reverse" and is_mode_active:
        press_left, press_right = press_right, press_left
        press_up, press_down = press_down, press_up

    if press_left and snake.last_dx != BLOCK:
        snake.dx, snake.dy = -BLOCK, 0
    elif press_right and snake.last_dx != -BLOCK:
        snake.dx, snake.dy = BLOCK, 0
    elif press_up and snake.last_dy != BLOCK:
        snake.dx, snake.dy = 0, -BLOCK
    elif press_down and snake.last_dy != -BLOCK:
        snake.dx, snake.dy = 0, BLOCK

    apple.update()
    now = pygame.time.get_ticks()

    if now - last_move > MOVE_DELAY:
        last_move = now
        if snake.dx != 0 or snake.dy != 0:
            snake.move()
            if abs(snake.body[0][0] - apple.x) < BLOCK and abs(snake.body[0][1] - apple.y) < BLOCK:
                p_color = (255, 215, 0) if apple.is_gold else (255, 0, 0)
                for _ in range(15):
                    particles.append(Particle(apple.x + 16, apple.y + 16, p_color))

                score += 3 if apple.is_gold else 1
                apple.spawn(GOLD_TIME)

                if score >= 50 and not unlocked_lvl4:
                    unlocked_lvl4 = True
                    current_secret_trigger = 4
                    show_secret_menu = True
                    pygame.mixer.music.pause()
                elif score >= 70 and not unlocked_lvl5:
                    unlocked_lvl5 = True
                    current_secret_trigger = 5
                    show_secret_menu = True
                    pygame.mixer.music.pause()
            else:
                snake.trim()

            walls_wrap = (MODE == "secret" and is_mode_active)
            if snake.dead(walls_wrap):
                game_over = True
                pygame.mixer.music.stop()

    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)

    screen.blit(background, (0, 0))
    for p in particles:
        p.draw(screen)
    apple.draw()
    snake.draw()

    screen.blit(font_s.render(f"Score: {score}", True, (255, 255, 0)), (10, 10))
    screen.blit(font_s.render(f"Best: {best_record}", True, (0, 100, 255)), (10, 45))

    if MODE in ["secret", "reverse"]:
        timer_color = (0, 255, 0) if is_mode_active else (255, 50, 50)
        timer_text = f"Timer: {time_left_sec:.1f}s"
        screen.blit(font_s.render(timer_text, True, timer_color), (10, 80))

    pygame.display.update()
