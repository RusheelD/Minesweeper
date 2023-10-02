import random

import pyglet

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
BACKGROUND_GRAYSCALE = 75
UNDERLAY_GRAYSCALE = 125
OVERLAY_GRAYSCALE = 150
NUM_COLORS = [
    (0, 0, 0, 255),
    (0, 0, 255, 255),
    (0, 255, 0, 255),
    (255, 125, 0, 255),
    (255, 0, 255, 255),
    (255, 0, 0, 255),
    (0, 255, 255, 255),
    (255, 125, 125, 255),
    (75, 75, 75, 255)
]


class Mine:
    def __init__(self, size: int, x: int, y: int):
        self.size = size
        self.x = x
        self.y = y
        self.circle = pyglet.shapes.Circle(
            self.size * (x + 0.5), self.size * (y + 0.5), (self.size * 3 // 4) // 2, color=(0, 0, 0, 255))
        self.clicked = False

    def draw(self):
        self.circle.draw()


class Flag:
    def __init__(self, size: int, x: int, y: int):
        self.size = size
        self.x = x
        self.y = y
        self.triangle = pyglet.shapes.Triangle(
            (self.x + 0.5) * self.size, (self.y + 0.5) * self.size,
            (self.x + 0.5) * self.size, (self.y + 0.8) * self.size,
            (self.x + 0.8) * self.size, (self.y + 0.65) * self.size,
            color=(255, 0, 0, 255))
        self.rect = pyglet.shapes.Rectangle(
            (self.x + 0.4) * self.size, (self.y + 0.2) * self.size,
            0.1 * self.size, 0.6 * self.size, color=(0, 0, 0, 255))

    def draw(self):
        self.triangle.draw()
        self.rect.draw()


class Tile:
    def __init__(self, size: int,  x: int, y: int, has_mine: bool, mine: None | Mine = None, number=0, has_flag: bool = False):
        self.size = size
        self.x = x
        self.y = y
        self.clicked = False
        self.has_mine = has_mine
        self.mine = mine
        self.number = number
        self.has_flag = has_flag
        self.flag = Flag(self.size, self.x, self.y)

    def make_flag_blue(self):
        self.flag.triangle.color = (0, 0, 255, 255)

    def draw(self):
        if (self.has_flag):
            self.flag.draw()
        elif (self.has_mine and self.mine != None):
            self.mine.draw()
        elif (self.number > 0):
            img = pyglet.text.Label(f'{self.number}', color=NUM_COLORS[self.number], x=(
                self.x+0.5) * self.size, y=(self.y + 0.75) * self.size, font_size=self.size // 2)
            img.anchor_x = "center"
            img.anchor_y = "center"
            (img.x, img.y) = ((self.x+0.5) * self.size, (self.y + 0.5) * self.size)
            img.draw()


class Game:
    def __init__(self, width: int, height: int, num_mines: int):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.over = False
        self.win = False
        self.num_flags = 0
        self.running = True
        if (num_mines > self.width * self.height // 2):
            print("ERROR: TOO MANY MINES")
            self.running = False
        self.window = pyglet.window.Window(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.window.push_handlers(self)
        self.sq_size = min(WINDOW_WIDTH // width, WINDOW_HEIGHT // height)
        self.background_square = pyglet.image.SolidColorImagePattern(
            (BACKGROUND_GRAYSCALE, BACKGROUND_GRAYSCALE, BACKGROUND_GRAYSCALE, 255)).create_image(self.sq_size, self.sq_size)
        self.underlay_square = pyglet.image.SolidColorImagePattern(
            (UNDERLAY_GRAYSCALE, UNDERLAY_GRAYSCALE, UNDERLAY_GRAYSCALE, 255)).create_image(self.sq_size * 9 // 10, self.sq_size * 9 // 10)
        self.overlay_square = pyglet.image.SolidColorImagePattern(
            (OVERLAY_GRAYSCALE, OVERLAY_GRAYSCALE, OVERLAY_GRAYSCALE, 255)).create_image(self.sq_size * 9 // 10, self.sq_size * 9 // 10)

        self.background_square.anchor_x = int(self.sq_size / 2)
        self.background_square.anchor_y = int(self.sq_size / 2)
        self.underlay_square.anchor_x = int((self.sq_size * 9 // 10) / 2)
        self.underlay_square.anchor_y = int((self.sq_size * 9 // 10) / 2)
        self.overlay_square.anchor_x = int((self.sq_size * 9 // 10) / 2)
        self.overlay_square.anchor_y = int((self.sq_size * 9 // 10) / 2)

        self.grid = [[Tile(self.sq_size, x, y, False)
                      for x in range(self.width)] for y in range(self.height)]
        self.fill_mines()
        self.populate_numbers()

    def fill_mines(self):
        mines_to_fill = self.num_mines
        while mines_to_fill > 0:
            tile = random.choice(random.choice(self.grid))
            if (tile.has_mine):
                continue

            tile.has_mine = True
            tile.mine = Mine(self.sq_size, tile.x, tile.y)
            mines_to_fill -= 1

    def check_over(self):
        num_correct_flags = 0
        all_opened = True
        for col in self.grid:
            for tile in col:
                if (tile.has_flag and tile.has_mine):
                    num_correct_flags += 1
                if (not tile.has_mine and not (tile.clicked or tile.has_flag)):
                    all_opened = False
        if (all_opened or (num_correct_flags == self.num_flags and self.num_flags == self.num_mines)):
            self.over = True
            self.win = True
            if (not all_opened):
                self.open_correct()
            self.place_correct_flags()

    def open_correct(self):
        for col in self.grid:
            for tile in col:
                if (not tile.has_mine and not tile.has_flag):
                    tile.clicked = True

    def place_correct_flags(self):
        for col in self.grid:
            for tile in col:
                if (tile.has_mine):
                    tile.has_flag = True
                # elif (tile.has_flag):
                #     tile.make_flag_blue()

    def click_surrounding(self, tile: Tile):
        x_offsets = [-1, 0, 1]
        y_offsets = [-1, 0, 1]
        for x_offset in x_offsets:
            for y_offset in y_offsets:
                if (x_offset == 0 and y_offset == 0):
                    continue
                x = tile.x + x_offset
                y = tile.y + y_offset
                if (x in range(self.width) and y in range(self.height) and self.grid[y][x].clicked != True):
                    self.grid[y][x].clicked = True
                    self.click_tile(self.grid[y][x])

    def click_tile(self, tile: Tile):
        tile.clicked = True
        if (tile.number == 0 and not tile.has_mine):
            self.click_surrounding(tile)

    def open_all_mines(self):
        for col in self.grid:
            for tile in col:
                if (tile.has_mine and not tile.has_flag):
                    tile.clicked = True
                if (tile.has_flag and not tile.has_mine):
                    tile.make_flag_blue()

    def flag_tile(self, tile: Tile):
        tile.has_flag = not (tile.has_flag)
        if (tile.has_flag):
            self.num_flags += 1
        else:
            self.num_flags -= 1
        self.check_over()

    def populate_numbers(self):
        for col in self.grid:
            for tile in col:
                mine_count = 0
                x_offsets = [-1, 0, 1]
                y_offsets = [-1, 0, 1]
                for x_offset in x_offsets:
                    for y_offset in y_offsets:
                        if (x_offset == 0 and y_offset == 0):
                            continue
                        x = tile.x + x_offset
                        y = tile.y + y_offset
                        if (x in range(self.width) and y in range(self.height)):
                            if self.grid[y][x].has_mine:
                                mine_count += 1
                tile.number = mine_count

    def on_draw(self):
        self.window.clear()
        for x in range(self.width):
            for y in range(self.height):

                used_x = x + 0.5
                used_y = y + 0.5
                self.background_square.blit(
                    used_x * self.sq_size, used_y * self.sq_size)
                if (self.grid[y][x].clicked):
                    self.underlay_square.blit(
                        used_x * self.sq_size, used_y * self.sq_size)
                    self.grid[y][x].draw()
                elif (self.grid[y][x].has_flag):
                    self.overlay_square.blit(
                        used_x * self.sq_size, used_y * self.sq_size)
                    self.grid[y][x].draw()
                else:
                    self.overlay_square.blit(
                        used_x * self.sq_size, used_y * self.sq_size)

    def on_mouse_press(self, x, y, button, modifiers):
        row = int(x // self.sq_size)
        col = int(y // self.sq_size)
        if (self.over):
            self.running = False
            return
        if (button == pyglet.window.mouse.RIGHT and not self.grid[col][row].clicked):
            self.flag_tile(self.grid[col][row])
        elif (button == pyglet.window.mouse.LEFT and not self.grid[col][row].has_flag):
            self.click_tile(self.grid[col][row])
            if (self.grid[col][row].has_mine):
                self.open_all_mines()
                self.over = True
                self.win = False
            else:
                self.check_over()

    def update(self, dt):
        if (not (self.running)):
            pyglet.app.exit()

    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.app.run()


Game(20, 20, 40).run()
