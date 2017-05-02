from __future__ import absolute_import, division
from hiveminder._util import even_q_distance, _first
from random import Random
from hiveminder.board import Board, volant_from_json
from hiveminder.hive import Hive
from hiveminder.flower import Flower
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from hiveminder.volant import Volant


def distance_between_hex_cells(cell1, cell2):
    """
    Finds the distance between 2 cells.

    Parameters
    ----------
    cell1: (int, int)
        Coordinates of the first cell
    choices: list[(int, int)]
        Coordinates of the second cell
        
    Returns
    -------
    distance: int
        The distance in cells between the cells
    """
    return even_q_distance(*(cell1 + cell2))


def nearest_hex_cell(target_cell, choices):
    """
    Finds the cell in choices that is nearest from the target_cell.

    Parameters
    ----------
    target_cell: (int, int)
        Coordinates of the target cell
    choices: list[(int, int)]
        A container of cells to choose from        
        
    Returns
    -------
    nearest: (int, int)
        The coordinates of the cell nearest from the target
    """
    if choices:
        return _first(sorted(choices,
                            key=lambda cell: distance_between_hex_cells(target_cell, cell)))


def furthest_hex_cell(target_cell, choices):
    """
    Finds the cell in choices that is furthest from the target_cell.

    Parameters
    ----------
    target_cell: (int, int)
        Coordinates of the target cell
    choices: list[(int, int)]
        A container of cells to choose from        
        
    Returns
    -------
    furthest: (int, int)
        The coordinates of the cell furthest from the target
    """
    if choices:
        return _first(sorted(choices, reverse=True,
                            key=lambda cell: distance_between_hex_cells(target_cell, cell)))


def is_on_course_with(start, heading, target):
    """
    Tests to see if an object starting at start with a given heading will pass through the target cell

    Parameters
    ----------
    start: (int, int)
        The starting coordinates
    heading: int
        The direction of travel
    target: (int, int)
        the target cell
        
        
    Returns
    -------
    is_on_course_with: boolean
        True if an object starting at start with a given heading will pass through the target cell
    """
    v = Volant(*(tuple(start) + (heading,)))

    if start == target:
        return True
    
    for _ in range(distance_between_hex_cells(start, target)):
        v = v.advance()
        if v.xyh == (tuple(target) + (heading,)):
            return True

    return False


class _OtherBoard(object):
    def __init__(self):
        self._incoming = {}


def apply_command_and_advance(board_width, board_height, hives, flowers, inflight, turn_num, cmd):
    """
    You can use this function to try out a potential move and test what happens.

    Parameters
    ----------
    board_width: int
        The number of tiles in each row of the board
    board_height: int
        The number of tiles in each column of the board
    hives: tuple[`Hive`+]
        Hives present on player's board
    flowers: tuple[`Flower`+]
        Flowers present on player's board
    inflight: dict [str, `Volant`]
        A dictionary of volant identifiers to volant
    turn_num: int
        The number of the current turn
        
        
    Returns
    -------
    crashed: dict [str, set[str]]
        A dictionary of causes to Volant identifiers which have been removed
    landed: set[`str`]
        A set of Bee identifiers which have landed back on a hive and are no longer active on the board
    lost: set[`str`]
        A set of Volant identifiers which have moved over the boundary into a neighbouring board
    """
    board = Board(game_params=DEFAULT_GAME_PARAMETERS,
                  board_width=board_width,
                  board_height=board_height,
                  hives=[Hive(*i) for i in hives],
                  flowers=[Flower.from_json(i) for i in flowers],
                  neighbours={'N':1, 'S':1, 'E':1, 'W':1, 'NW':1, 'SE':1, },
                  inflight={volant_id: volant_from_json(volant) for volant_id, volant in inflight.items()},
                  dead_bees=0)
    
    board._connect_to_neighbours([board, _OtherBoard()])
    board.apply_command(cmd, turn_num)
    board.remove_dead_flowers(turn_num)
    board.move_volants()
    lost = set(board.send_volants())
    board.visit_flowers(Random())
    landed = set(board.land_bees())
    crashed = {k: set(v) for k, v in board.detect_crashes().items()}
    
    return crashed, landed, lost
