import pygame
import random
from os import path
import sys
import time

img_dir = path.join(path.dirname(__file__), 'data')

# возможные фигуры
S = [['.00',
      '00.'],
     ['0.',
      '00',
      '.0']]

Z = [['00.',
      '.00'],
     ['.0',
      '00',
      '0.']]

I = [['....',
      '0000.',
      '....',
      '....', ],
     ['.0..',
      '.0..',
      '.0..',
      '.0..']]

O = [['.00',
      '.00']]

J = [['0..',
      '000',
      '...'],
     ['.00',
      '.0.',
      '.0.'],
     ['...',
      '000',
      '..0'],
     ['.0.',
      '.0.',
      '00.']]

L = [['..0',
      '000',
      '...'],
     ['.0.',
      '.0.',
      '.00'],
     ['...',
      '000',
      '0..'],
     ['00.',
      '.0.',
      '.0.']]

T = [['.0.',
      '000',
      '...'],
     ['.0.',
      '.00',
      '.0.', ],
     ['...',
      '000',
      '.0.', ],
     ['.0.',
      '00.',
      '.0.', ]]

shapes = [S, Z, I, O, J, L, T]
# shapes = [O]

# список цветов для деталей
shape_colors = [(150, 85, 240), (255, 128, 0), (20, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255),
                (128, 255, 128)]
screen_rect = (0, 0, 1900, 1050)


# функция загрузки изображения
def load_image(name, colorkey=None):
    fullname = path.join('data', name)
    # если файл не существует, то выходим
    if not path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


# класс частиц (отвечает за спецэффекты)
class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("2021-01-13-15-30-37_resize_53.png")]
    for scale in (10, 20, 30):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = 1

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-40, 40)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


all_sprites = pygame.sprite.Group()


# класс деталей
class Piece(object):  # *
    def __init__(self, x, y, shape):
        self.x = x
        self.y = 3
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        # self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        self.rotation = 0


# класс тетрис
class Tetris:
    def __init__(self):
        self.s_width = 1920
        self.s_height = 1080
        self.play_width = 400
        self.play_height = 800
        self.block_size = 40
        self.top_left_x = 760
        self.top_left_y = self.s_height - self.play_height - 100
        self.c = random.randint(1, 3)

    def create_grid(self, locked_pos={}):  # *
        grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in locked_pos:
                    c = locked_pos[(j, i)]
                    grid[i][j] = c
        return grid

    def convert_shape_format(self, shape):
        positions = []
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    positions.append((shape.x + j, shape.y + i))

        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)

        return positions

    def valid_space(self, shape, grid):
        accepted_pos = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
        accepted_pos = [j for sub in accepted_pos for j in sub]

        formatted = self.convert_shape_format(shape)

        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    # проверка на поражение
    def check_lost(self, positions):
        for pos in positions:
            x, y = pos
            if y < 1:
                return True

        return False

    # новая рандомная фигура
    def get_shape(self):
        return Piece(5, 0, random.choice(shapes))

    # расположение текста по центру
    def draw_text_middle(self, surface, text, size, color):
        font = pygame.font.SysFont("a_LCDNova", size, bold=True)
        label = font.render(text, 1, color)

        surface.blit(label, (
            self.top_left_x + self.play_width / 2 - (label.get_width() / 2),
            self.top_left_y + self.play_height / 2 - label.get_height() / 2))

    # отрисовка сетки
    def draw_grid(self, surface, grid):
        sx = self.top_left_x
        sy = self.top_left_y

        for i in range(len(grid)):
            pygame.draw.line(surface, (0, 0, 0), (sx, sy + i * self.block_size),
                             (sx + self.play_width, sy + i * self.block_size))
            for j in range(len(grid[i])):
                pygame.draw.line(surface, (0, 0, 0), (sx + j * self.block_size, sy),
                                 (sx + j * self.block_size, sy + self.play_height))

    # отчистка ряда в случае сбора целой линии
    def clear_rows(self, grid, locked):
        inc = 0
        for i in range(len(grid) - 1, -1, -1):
            row = grid[i]
            if (0, 0, 0) not in row:
                inc += 1
                ind = i
                for j in range(len(row)):
                    try:
                        del locked[(j, i)]
                    except:
                        continue

        if inc > 0:
            for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
                x, y = key
                if y < ind:
                    newKey = (x, y + inc)
                    locked[newKey] = locked.pop(key)

        return inc

    # отрисовка следущей фигуры
    def draw_next_shape(self, shape, surface, q):
        pygame.font.init()
        if q > -1:
            sq = self.top_left_x
            self.top_left_x = self.top_left_x[q]
        font = pygame.font.SysFont('a_LCDNova', 35)
        label = font.render('Следущая:', 1, (255, 255, 255))

        sx = self.top_left_x + self.play_width + 50
        sy = self.top_left_y + self.play_height / 2 - 100
        format = shape.shape[shape.rotation % len(shape.shape)]

        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    pygame.draw.rect(surface, shape.color,
                                     (sx + j * self.block_size + 60, sy + i * self.block_size + 310, self.block_size,
                                      self.block_size), 0)
                    pygame.draw.rect(surface, (0, 0, 0),
                                     (sx + j * self.block_size + 60, sy + i * self.block_size + 310, self.block_size,
                                      self.block_size), 4)
        surface.blit(label, (sx + 20, sy + 190))
        if q > -1:
            self.top_left_x = sq

    # обновление рекорда
    def update_score(self, nscore):
        score = self.max_score()

        with open('data/scores.txt', 'w') as f:
            if int(score) > nscore:
                f.write(str(score))

            else:
                f.write(str(nscore))

    # рекорд
    def max_score(self):
        with open('data/scores.txt', 'r') as f:
            lines = f.readlines()
            score = lines[0].strip()

        return score

    def draw_window(self, surface, grid, q, c, score=0, last_score=0):

        pygame.font.init()

        font = pygame.font.SysFont('a_LCDNova', 100)
        label = font.render('TETRIS', 1, (255, 255, 255))
        if q > -1:
            sq = self.top_left_x
            self.top_left_x = self.top_left_x[q]

        pygame.draw.rect(surface, (0, 126, 178), (self.top_left_x - 225, 0, 995, 1080), 0)
        pygame.draw.rect(surface, (113, 71, 39), (self.top_left_x - 225, 900, 995, 200), 0)
        pygame.draw.rect(surface, (19, 116, 43), (self.top_left_x - 225, 870, 995, 30), 0)

        # отрисовка домика
        image = pygame.image.load(
            path.join(img_dir, f"fon{c}.jpg")).convert()
        surface.blit(image, (self.top_left_x, self.top_left_y))
        # отрисовка крыши
        cr = pygame.image.load(
            path.join(img_dir, "cr.png")).convert()
        surface.blit(cr, (self.top_left_x + 50, self.top_left_y - 40))

        surface.blit(label, (self.top_left_x + self.play_width / 2 - (label.get_width() / 2), 40))

        # current score
        font = pygame.font.SysFont('a_LCDNova', 40)
        label = font.render('Очки: ' + str(score), 1, (255, 255, 255))

        sx = self.top_left_x + self.play_width + 50
        sy = self.top_left_y + self.play_height / 2 - 100

        # зеленая рамка вокруг "Очки"
        pygame.draw.rect(surface, (19, 116, 43), (sx - 11, sy - 157, 230, 45), 0)
        pygame.draw.rect(surface, (0, 0, 0), (sx - 11, sy - 157, 230, 45), 3)
        surface.blit(label, (sx - 3, sy - 150))

        # last score
        sx = self.top_left_x - 200
        sy = self.top_left_y + 200
        # отображения рекорда при одиночной игре
        if q == -1:
            pygame.draw.rect(surface, (19, 116, 43), (sx + 639, sy + 12, 230, 45), 0)
            pygame.draw.rect(surface, (0, 0, 0), (sx + 639, sy + 12, 230, 45), 3)
            label = font.render('Рекорд: ' + str(last_score), 1, (255, 255, 255))
            surface.blit(label, (sx + 647, sy + 20))
        # отрисовка положения всех деталей
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] != (0, 0, 0):
                    pygame.draw.rect(surface, grid[i][j],
                                     (self.top_left_x + j * self.block_size + 2,
                                      self.top_left_y + i * self.block_size + 2,
                                      self.block_size - 4, self.block_size - 4), 0)
                    pygame.draw.rect(surface, (0, 0, 0), (
                        self.top_left_x + j * self.block_size + 3, self.top_left_y + i * self.block_size + 3,
                        self.block_size - 6, self.block_size - 6), 6)

        pygame.draw.rect(surface, (102, 50, 0), (self.top_left_x, self.top_left_y, self.play_width, self.play_height),
                         9)

        self.draw_grid(surface, grid)
        if q > -1:
            self.top_left_x = sq

    def main(self, win):  # *
        last_score = self.max_score()  # рекорд
        locked_positions = {}  # блокировка позиции

        change_piece = False  # возможность смены положения
        run = True
        pause = False
        current_piece = self.get_shape()  # текущее положение детали и сама деталь
        next_piece = self.get_shape()  # следущая деталь
        clock = pygame.time.Clock()
        fall_time = 0  # время обновления скорости
        fall_speed = 0.3  # скорость
        level_time = 0  # время игры
        score = 0  # колличество очков

        while run:
            grid = self.create_grid(locked_positions)
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        image_game_over = pygame.image.load(
                            path.join(img_dir, "gm44.png")).convert()

                        game_over_x = -1080
                        speed = 110

                        while game_over_x < 0:
                            clock.tick(30)
                            speed -= 5
                            game_over_x += speed
                            win.blit(image_game_over, (game_over_x, 0))
                            pygame.display.update()
                        run = False
                        break
                    if not pause:
                        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                            current_piece.x -= 1
                            if not (self.valid_space(current_piece, grid)):
                                current_piece.x += 1
                        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                            current_piece.x += 1
                            if not (self.valid_space(current_piece, grid)):
                                current_piece.x -= 1
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            current_piece.rotation += 1
                            if not (self.valid_space(current_piece, grid)):
                                current_piece.rotation -= 1
                    if event.key == pygame.K_SPACE:
                        if pause:
                            pause = False
                        else:
                            pause = True
                            pause_img = pygame.image.load(path.join(img_dir, "pause.png")).convert_alpha()
                            win.blit(pause_img, (832, 412))
                            pygame.display.update()
            if run:
                if not pause:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                        current_piece.y += 1
                        if not (self.valid_space(current_piece, grid)):
                            current_piece.y -= 1

                if level_time > 5000:
                    level_time = 0
                    fall_speed -= 0.005

                if fall_time / 1000 > fall_speed:
                    fall_time = 0
                    if not pause:
                        current_piece.y += 1
                        if not (self.valid_space(current_piece, grid)) and current_piece.y > 0:
                            current_piece.y -= 1
                            change_piece = True

                shape_pos = self.convert_shape_format(current_piece)

                for i in range(len(shape_pos)):
                    x, y = shape_pos[i]
                    if y > -1:
                        grid[y][x] = current_piece.color

                if change_piece:
                    for pos in shape_pos:
                        p = (pos[0], pos[1])
                        locked_positions[p] = current_piece.color
                    current_piece = next_piece
                    next_piece = self.get_shape()
                    change_piece = False
                    c = self.clear_rows(grid, locked_positions) * 10
                    score += c
                    if c > 0:
                        create_particles((760, 600))
                        create_particles((960, 600))
                        create_particles((1060, 600))

                if not pause:
                    win.fill((0, 126, 178))
                    pygame.draw.rect(win, (113, 71, 39), (0, 900, 2000, 200), 0)
                    pygame.draw.rect(win, (19, 116, 43), (0, 870, 2000, 30), 0)
                    self.draw_window(win, grid, -1, self.c, score, last_score)
                    self.draw_next_shape(next_piece, win, -1)
                    all_sprites.update()
                    all_sprites.draw(win)
                    pygame.display.update()

                if self.check_lost(locked_positions):
                    image_game_over = pygame.image.load(
                        path.join(img_dir, f"gm{random.randint(5, 7)}.png")).convert()

                    game_over_x = - 3840
                    speed = 150

                    while game_over_x < -1920:
                        clock.tick(30)
                        speed -= 3
                        game_over_x += speed
                        win.blit(image_game_over, (game_over_x, 1))
                        pygame.display.update()
                    time.sleep(0.6)
                    speed = 0

                    while game_over_x < 0:
                        clock.tick(30)
                        speed += 2
                        game_over_x += speed
                        win.blit(image_game_over, (min(game_over_x, 0), 1))
                        pygame.display.update()

                    run = False
                    self.update_score(score)


class Duo(Tetris):
    def __init__(self):
        super().__init__()
        self.top_left_x = 210, 1150
        self.c = [random.randint(1, 3), random.randint(1, 3)]

    def mein(self, win):

        locked_positions = [{}, {}]
        grid = [0, 0]
        grid[0] = self.create_grid(locked_positions[0])
        grid[1] = self.create_grid(locked_positions[1])

        change_piece = [False, False]
        run = [True, True]
        current_piece = [self.get_shape(), self.get_shape()]
        next_piece = [self.get_shape(), self.get_shape()]
        clock = pygame.time.Clock()
        fall_time = 0
        pause = False
        fall_speed = 0.3
        level_time = 0
        score = [0, 0]

        while run:
            for i in range(2):
                grid[i] = self.create_grid(locked_positions[i])
            fall_time += clock.get_rawtime()
            level_time += clock.get_rawtime()
            clock.tick()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.display.quit()
                # если игрок хочет выйти не доиграв
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        image_game_over = pygame.image.load(
                            path.join(img_dir, "gm44.png")).convert()

                        game_over_x = -1080
                        speed = 110

                        while game_over_x < 0:
                            clock.tick(30)
                            speed -= 5
                            game_over_x += speed
                            win.blit(image_game_over, (game_over_x, 0))
                            pygame.display.update()
                        run = False
                        break
                    # проверка на нажатие кнопок управления
                    if not pause:
                        if event.key == pygame.K_a:
                            current_piece[0].x -= 1
                            if not (self.valid_space(current_piece[0], grid[0])):
                                current_piece[0].x += 1
                        if event.key == pygame.K_LEFT:
                            current_piece[1].x -= 1
                            if not (self.valid_space(current_piece[1], grid[1])):
                                current_piece[1].x += 1
                        if event.key == pygame.K_d:
                            current_piece[0].x += 1
                            if not (self.valid_space(current_piece[0], grid[0])):
                                current_piece[0].x -= 1
                        if event.key == pygame.K_RIGHT:
                            current_piece[1].x += 1
                            if not (self.valid_space(current_piece[1], grid[1])):
                                current_piece[1].x -= 1
                        if event.key == pygame.K_w:
                            current_piece[0].rotation += 1
                            if not (self.valid_space(current_piece[0], grid[0])):
                                current_piece[0].rotation -= 1
                        if event.key == pygame.K_UP:
                            current_piece[1].rotation += 1
                            if not (self.valid_space(current_piece[1], grid[1])):
                                current_piece[1].rotation -= 1
                    if event.key == pygame.K_SPACE:
                        if pause:
                            pause = False
                        else:
                            pause = True
                            pause_img = pygame.image.load(path.join(img_dir, "pause.png")).convert_alpha()
                            win.blit(pause_img, (832, 412))
                            pygame.display.update()
            if not pause:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_DOWN]:
                    current_piece[1].y += 1
                    if not (self.valid_space(current_piece[1], grid[1])):
                        current_piece[1].y -= 1
                if keys[pygame.K_s]:
                    current_piece[0].y += 1
                    if not (self.valid_space(current_piece[0], grid[0])):
                        current_piece[0].y -= 1
            # ускорение при долгой игре
            if level_time > 5000:
                level_time = 0

                fall_speed -= 0.001

            for i in range(2):
                if fall_time / 1000 > fall_speed:
                    if i == 1:
                        fall_time = 0
                    if not pause:
                        current_piece[i].y += 1
                        if not (self.valid_space(current_piece[i], grid[i])) and current_piece[i].y > 0:
                            current_piece[i].y -= 1
                            change_piece[i] = True

            shape_pos = [self.convert_shape_format(current_piece[0]), self.convert_shape_format(current_piece[1])]

            for i in range(2):
                for g in range(len(shape_pos[i])):
                    x, y = shape_pos[i][g]
                    if y > -1:
                        grid[i][y][x] = current_piece[i].color

                if change_piece[i]:
                    for pos in shape_pos[i]:
                        p = (pos[0], pos[1])
                        locked_positions[i][p] = current_piece[i].color
                    current_piece[i] = next_piece[i]
                    next_piece[i] = self.get_shape()
                    change_piece[i] = False
                    c = self.clear_rows(grid[i], locked_positions[i]) * 10
                    score[i] += c
                    if c > 0:
                        if i == 0:
                            create_particles((410, 600))

                        else:
                            create_particles((1350, 600))
                # проверка на поражение
                if self.check_lost(locked_positions[i]):
                    win.fill((0, 126, 178))
                    if i == 1:
                        image_game_over = pygame.image.load(
                            path.join(img_dir, "gw.png")).convert()

                    else:
                        # анимация экрана поражения
                        image_game_over = pygame.image.load(
                            path.join(img_dir, "wg.png")).convert()

                    game_over_y = 1080
                    speed = 110

                    while game_over_y > 0:
                        clock.tick(30)
                        speed -= 5
                        game_over_y -= speed
                        win.fill((0, 126, 178))
                        win.blit(image_game_over, (1, game_over_y))
                        pygame.display.update()
                    time.sleep(1)
                    speed = 0

                    while game_over_y < 1080:
                        clock.tick(30)
                        speed += 2
                        game_over_y += speed
                        win.fill((0, 126, 178))
                        win.blit(image_game_over, (1, game_over_y))
                        pygame.display.update()

                    run = False
                    self.update_score(score[i])
                    break
            if run and not pause:
                # отрисовка кадра
                for i in range(2):
                    self.draw_window(win, grid[i], i, self.c[i], score[i], "Duo")
                    self.draw_next_shape(next_piece[i], win, i)
                    all_sprites.update()
                    all_sprites.draw(win)
                pygame.display.update()


# основная функция
def main_menu(win):
    run = True
    while run:
        pygame.font.init()
        win.fill((0, 126, 178))
        image = pygame.image.load(
            path.join(img_dir, "gm44.png")).convert()
        win.blit(image, (0, 0))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            # отслеживание нажатия на кнопку
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 685 < x < 1225 and 620 < y < 750:
                    tetris = Duo()
                    tetris.mein(win)
                if 685 < x < 1225 and 364 < y < 494:
                    tetris = Tetris()
                    tetris.main(win)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_1:
                    tetris = Tetris()
                    tetris.main(win)
                if event.key == pygame.K_2:
                    tetris = Duo()
                    tetris.mein(win)
    pygame.display.quit()


# запуск программы
pygame.init()
win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

pygame.display.set_caption('Тетрис')
main_menu(win)
