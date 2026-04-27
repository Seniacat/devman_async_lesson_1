import asyncio
import time
import curses
import random

import space_ship

TIC_TIMEOUT = 0.1



async def sleep(ticks):
   for i in range(ticks):
        await asyncio.sleep(0)


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


async def blink(canvas, row, column, symbol):
    """Display animation of stars."""
    curses_list = [curses.A_DIM, 0, curses.A_BOLD, 0]
    while True:
        for param in curses_list:
            canvas.addstr(row, column, symbol, param)
            await sleep(random.randint(2, 20))
            canvas.refresh()


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


def draw(canvas):
    canvas.border()
    curses.curs_set(False)
    window = curses.initscr()
    window.nodelay(True)
    coroutines = []
    shot = fire(canvas, start_row=10, start_column=10)
    coroutines.append(shot)
    max_row, max_column = window.getmaxyx()
    middle_row, middle_column = max_row / 2, max_column / 2
    shot = fire(canvas, start_row=middle_row, start_column=middle_column)
    coroutines.append(shot)
    space_ship_animation = space_ship.animate_spaceship(canvas, middle_row-5, middle_column)
    coroutines.append(space_ship_animation)
    stars = ['+', '*', '.', ':']
    for star in range(100):
        star = blink(canvas,
                     random.randint(2, max_row - 2),
                     random.randint(2, max_column - 2),
                     symbol=random.choice(stars))
        coroutines.append(star)
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)




if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)