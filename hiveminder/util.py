from __future__ import absolute_import, division
from itertools import starmap


def is_even(x):
    return (x % 2) == 0


def sign(x):
    return -1 if x < 0 else 1 if x > 0 else 0

# http://www.redblobgames.com/grids/hexagons
#
# The game uses even-q offset coordinates


def even_q_to_cube(col, row):
    x = col
    z = row - (col + (col % 2)) // 2
    y = -x-z
    return x, y, z


def cube_to_even_q(x, y, z):
    col = x
    row = z + (x + (x % 2)) // 2
    return col, row


def cube_add(cube1, cube2):
    return tuple(cube1[i] + cube2[i] for i in range(3))


def cube_in_range(centre, N):
    return (cube_add(centre, (dx, dy, -dx-dy))
            for dx in range(-N, N+1)
            for dy in range(max(-N, -dx-N), min(N, -dx+N)+1))


def even_q_in_range(col, row, N):
    return starmap(cube_to_even_q, cube_in_range(even_q_to_cube(col, row), N))


def cube_distance(c1, c2):
    return sum(abs(i1 - i2) for i1, i2 in zip(c1, c2)) // 2


def even_q_distance(col1, row1, col2, row2):
    return cube_distance(even_q_to_cube(col1, row1), even_q_to_cube(col2, row2))
