import pygame
import numpy as np
import time
import random

pygame.font.init()

GREY = (70, 70, 70)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def generate_puzzle():
    numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    random.shuffle(numbers)
    board = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]
    ])

    for x in range(len(board) - 3):
        x_position = random.randint(0, 8)
        y_position = random.randint(0, 8)
        if board[x_position][y_position] == 0:
            board[x_position][y_position] = numbers[x]
    return board


class Grid:
    board = generate_puzzle()

    def __init__(self, width, height):
        self.rows = 9
        self.columns = 9
        self.width = width
        self.height = height
        self.Model = None
        self.selected_cell = None
        self.cells = np.array(
            [[Cell(self.board[i][j], i, j, width, height) for j in range(self.columns)] for i in range(self.rows)])

    def update_model(self):
        self.model = [self.cells[i][j] for i, j in np.ndindex(self.board.shape)]

    def place(self, value):
        row, column = self.selected_cell

        if self.cells[row][column].value == 0:
            self.cells[row, column].set_value(value)
            self.update_model()

            if valid(self.model, value, (row, column)) and solve(self.model):
                return True
            else:
                self.cells[row][column].set_value(0)
                self.cells[row][column].set_subscript_value(0)
                return False

    def draw_subscript(self, value):
        row, column = self.selected_cell
        self.cells[row][column].set_subscript_value(value)

    def draw(self, window):
        cell_size = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                line_thickness = 4
            else:
                line_thickness = 1

            pygame.draw.line(window, BLACK, (0, i * cell_size), (self.width, i * cell_size), line_thickness)
            pygame.draw.line(window, BLACK, (i * cell_size, 0), (i * cell_size, self.height), line_thickness)

        for i in range(self.rows):
            for j in range(self.columns):
                self.cells[i][j].draw(window)

    def select(self, row, column):
        for i, j in np.ndindex(self.board.shape):
            self.cells[i][j].is_selected = False

        if row is None and column is None:
            self.selected_cell = None
        else:
            self.cells[row][column].is_selected = True
            self.selected_cell = (row, column)

    def clear(self):
        row, column = self.selected_cell
        if self.cells[row][column].value == 0:
            self.cells[row][column].set_subscript_value(0)

    def click(self, mouse_position):
        x = mouse_position[0]
        y = mouse_position[1]

        if x < self.width and y < self.height:
            cell_size = self.width / 9
            return int(y // cell_size), int(x // cell_size)
        else:
            return None

    def is_finished(self):
        for x, y in np.ndindex(self.board.shape):
            if self.cells[x][y].value == 0:
                return False
        return True

    def color_cells(self, window):
        for x, y in np.ndindex(self.board.shape):
            self.cells[x][y].color_background(window)

    def update_board(self, board, window):
        self.board = board
        self.update_model()
        self.draw(window)


class Cell:
    rows, cols = 9, 9

    def __init__(self, value, row, column, width, height):
        self.value = value
        self.subscript_value = 0
        self.row = row
        self.column = column
        self.width = width
        self.height = height
        self.is_selected = False
        self.color = WHITE

    def draw(self, window):
        text_font = pygame.font.SysFont("helvetica", 40)
        sub_font = pygame.font.SysFont("helvetica", 20)
        cell_size = (self.width / 9)

        x = self.column * cell_size
        y = self.row * cell_size

        if self.subscript_value != 0 and self.value == 0:
            sub = sub_font.render(str(self.subscript_value), 1, GREY)
            window.blit(sub, (x + cell_size - cell_size / 4, y + 5))
        elif not (self.value == 0):
            text = text_font.render(str(self.value), 1, BLACK)
            window.blit(text, (x + cell_size / 3, y + 5))

        if self.is_selected:
            pygame.draw.rect(window, BLACK, (x, y, cell_size, cell_size), 3)

    def set_value(self, value):
        self.value = value

    def set_subscript_value(self, value):
        self.subscript_value = value

    def color_background(self, window):
        cell_size = (self.width / 9)
        x = self.column * cell_size
        y = self.row * cell_size

        window.fill(self.color, rect=(x, y, cell_size, cell_size))


def find_empty(board):
    board = np.reshape(board, (9, 9))
    for x, y in np.ndindex(board.shape):
        if board[x][y] == 0:
            return (x, y)
    return None


def valid(board, num, position):
    board = np.reshape(board, (9, 9))
    for i in range(9):
        if board[position[0]][i].value == num and position[1] != i:
            return False

    for i in range(len(board)):
        if board[i][position[1]].value == num and position[0] != i:
            return False

    box_x = position[1] // 3
    box_y = position[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num and (i, j) != position:
                return False

    return True


def solve(board):
    find = find_empty(board)
    if not find:
        return True
    else:
        row, column = find

    for i in range(1, 10):
        if valid(board, i, (row, column)):
            board[row][column] = i

            if solve(board):
                return True

            board[row][column] = 0

    return False


def redraw_window(window, ctime, board, strikes):
    window.fill(WHITE)
    small_font = pygame.font.SysFont("Helvetica", 30)
    board.color_cells(window)

    text = small_font.render("Time Taken", 1, BLACK)
    window.blit(text, (380, 540))

    text = small_font.render(get_time(ctime), 1, BLACK)
    window.blit(text, (410, 570))

    text = small_font.render("Strikes", 1, BLACK)
    window.blit(text, (50, 540))

    text = small_font.render("X " * strikes, 1, (255, 0, 0))
    window.blit(text, (60, 570))
    board.draw(window)

    window.fill(BLACK, rect=(200, 560, 150, 30))
    text = pygame.font.SysFont("Helvetica", 24).render("Generate Puzzle", 1, WHITE)
    window.blit(text, (202, 560))

    pygame.draw.circle(window, (255, 0, 0), (570, 30), 20)
    pygame.draw.circle(window, (0, 150, 0), (570, 90), 20)
    pygame.draw.circle(window, (0, 0, 255), (570, 150), 20)
    pygame.draw.circle(window, (158, 111, 254), (570, 210), 20)
    pygame.draw.circle(window, (255, 53, 111), (570, 270), 20)


def get_time(seconds):
    return " " + str(int(seconds) // 60) + ":" + str(seconds % 60).zfill(2)


def color_selector(position):
    colors = [(255, 0, 0), (0, 150, 0), (0, 0, 255), (158, 111, 254), (255, 53, 111)]
    index = (position[1] // 60)

    if index < 5:
        return colors[index]
    return WHITE


def main():
    window = pygame.display.set_mode((600, 600))
    pygame.display.set_caption("Sudoku Solver")
    board = Grid(540, 540)
    key = None
    run = True
    clicked = None
    start = time.time()
    strikes = 0
    color = WHITE
    numerical_keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8,
                      pygame.K_9]
    arrow_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT]

    while run:
        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key in numerical_keys:
                    key = event.key - 48
                if event.key in arrow_keys and board.selected_cell is not None:
                    y, x = board.selected_cell[0], board.selected_cell[1]
                    if event.key == pygame.K_UP and y > 0:
                        board.select(y - 1, x)
                    if event.key == pygame.K_DOWN and y < 8:
                        board.select(y + 1, x)
                    if event.key == pygame.K_RIGHT and x < 8:
                        board.select(y, x + 1)
                    if event.key == pygame.K_LEFT and x > 0:
                        board.select(y, x - 1)

                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected_cell
                    if board.cells[i][j].subscript_value != 0:
                        if not board.place(board.cells[i][j].subscript_value):
                            strikes += 1
                        key = None

                        if board.is_finished():
                            run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                if 200 < position[0] < 350 and 560 < position[1] < 590:
                    board.update_board(generate_puzzle(), window)
                    board.__init__(540, 540)
                    start = time.time()
                    strikes = 0
                elif position[0] > 540:
                    color = color_selector(position)
                else:
                    if clicked == board.click(position):
                        board.select(None, None)
                        clicked = None
                    else:
                        clicked = board.click(position)
                        if clicked:
                            board.select(clicked[0], clicked[1])
                            key = None

            if board.selected_cell:
                current_cell = board.cells[board.selected_cell[0]][board.selected_cell[1]]
                current_cell.color = color
                current_cell.color_background(window)
            if board.selected_cell and key != None:
                board.draw_subscript(key)
            if strikes == 3:
                board.update_board(generate_puzzle(), window)
                board.__init__(540, 540)
                start = time.time()
                strikes = 0

        redraw_window(window, play_time, board, strikes)
        pygame.display.update()


generate_puzzle()
main()
pygame.quit()
