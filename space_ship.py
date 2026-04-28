import asyncio
import time
import curses
import random

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258



with open('frames/rocket_frame_1.txt',
          'r') as file:
    frame_1 = file.read()

with open('frames/rocket_frame_2.txt',
          'r') as file:
    frame_2 = file.read()


async def sleep(ticks):
   for i in range(ticks):
        await asyncio.sleep(0)


def process_control(canvas, row, column, row_delta, column_delta):
    max_row, max_column = canvas.getmaxyx()
    rows_direction, columns_direction, space_pressed = read_controls(canvas)
    new_row = row + rows_direction
    new_column = column + columns_direction
    if new_row < 0 or new_row > (max_row - row_delta):
        new_row = row
    if new_column < 0 or new_column > (max_column - column_delta):
        new_column = column
    return new_row, new_column


async def rocket_animation():
    rocket_frames = [frame_1, frame_1, frame_2, frame_2]
    while True:
        for frame in rocket_frames:
            await sleep(0)
            yield frame


async def animate_spaceship(canvas, row, column):
    async for frame in rocket_animation():
        frame_rows, frame_columns = get_frame_size(frame)
        prev_row, prev_col = row - frame_rows/2, column - frame_columns/2
        row, column = process_control(canvas, row, column, frame_rows, frame_columns)
        draw_frame(canvas, prev_row, prev_col, frame)
        await sleep(1)
        draw_frame(canvas, prev_row, prev_col, frame, negative=True)
        draw_frame(canvas, prev_row, prev_col, frame)
        draw_frame(canvas, prev_row, prev_col, frame, negative=True)



def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns