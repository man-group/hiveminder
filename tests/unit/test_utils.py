from hiveminder.flower import Flower
from hiveminder.utils import (distance_between_hex_cells, nearest_hex_cell,
                              furthest_hex_cell, apply_command_and_advance,
                              is_on_course_with)
import pytest
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS


@pytest.mark.parametrize("col1, row1, col2, row2, distance", [(5, 5, 5, 5, 0),
                                                              
                                                              (5, 5, 6, 4, 1),
                                                              (5, 5, 6, 5, 1),
                                                              (5, 5, 5, 6, 1),
                                                              (5, 5, 4, 5, 1),
                                                              (5, 5, 5, 4, 1),
                                                              (5, 5, 4, 4, 1),
                                                              
                                                              (4, 4, 5, 4, 1),
                                                              (4, 4, 4, 5, 1),
                                                              (4, 4, 3, 4, 1),
                                                              (4, 4, 4, 3, 1),
                                                              (4, 4, 5, 5, 1),
                                                              (4, 4, 3, 5, 1),
                                                              
                                                              (0, 0, 0, 1, 1),
                                                              (0, 0, 0, 2, 2),
                                                              (0, 0, 0, 3, 3),
                                                              (0, 0, 0, 4, 4),
                                                              (0, 0, 0, 5, 5),
                                                              (0, 0, 0, 6, 6),
                                                              (0, 0, 0, 7, 7),
                                                              
                                                              (0, 0, 1, 0, 1),
                                                              (0, 0, 2, 0, 2),
                                                              (0, 0, 3, 0, 3),
                                                              (0, 0, 4, 0, 4),
                                                              (0, 0, 5, 0, 5),
                                                              (0, 0, 6, 0, 6),
                                                              (0, 0, 7, 0, 7),

                                                              (0, 0, 1, 1, 1),
                                                              (0, 0, 2, 2, 3),
                                                              (0, 0, 3, 3, 4),
                                                              (0, 0, 4, 4, 6),
                                                              (0, 0, 5, 5, 7),
                                                              (0, 0, 6, 6, 9),
                                                              (0, 0, 7, 7, 10),
                                                              ])
def test_can_find_distance_between_two_tiles(col1, row1, col2, row2, distance):
    assert distance == distance_between_hex_cells((col1, row1), (col2, row2))
    assert distance == distance_between_hex_cells((col2, row2), (col1, row1))
    
    
def test_find_nearest_returns_none_if_no_cells():
    assert nearest_hex_cell((1, 1), []) is None    
    

def test_find_nearest_returns_nearest_of_one():
    assert nearest_hex_cell((1, 1), [(1, 2)]) == (1, 2)
    

def test_find_nearest_returns_nearest_of_two():
    assert nearest_hex_cell((1, 1), [(1, 2), (5, 5)]) == (1, 2)
    

def test_find_nearest_returns_nearest_of_three():
    assert nearest_hex_cell((1, 1), [(1, 2), (5, 5), (100, 100)]) == (1, 2)
    
    
def test_find_furthest_returns_none_if_no_cells():
    assert furthest_hex_cell((1, 1), []) is None    
    

def test_find_furthest_returns_furthest_of_one():
    assert furthest_hex_cell((1, 1), [(1, 2)]) == (1, 2)


def test_find_furthest_returns_furthest_of_two():
    assert furthest_hex_cell((1, 1), [(1, 2), (5, 5)]) == (5, 5)
    

def test_find_furthest_returns_furthest_of_three():
    assert furthest_hex_cell((1, 1), [(1, 2), (5, 5), (100, 100)]) == (100, 100)


def test_apply_command_and_advance_no_command_nothing_happens():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 1, 1, 0, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert not crashed['collided']
    assert not crashed['exhausted']
    assert not crashed['headon']
    assert not crashed['seeds']
    assert not landed
    assert not lost


def test_apply_command_and_advance_no_command_bee_leaves_board():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 0, 0, 180, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert not crashed['collided']
    assert not crashed['exhausted']
    assert not crashed['headon']
    assert not crashed['seeds']
    assert not landed
    assert lost == {"abee"}


def test_apply_command_and_advance_no_command_bee_dies_of_exhaustion():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 0, 0, 0, 0, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert not crashed['collided']
    assert crashed['exhausted'] == {"abee"}
    assert not crashed['headon']
    assert not crashed['seeds']
    assert not landed
    assert not lost


def test_apply_command_and_advance_no_command_bee_lands():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[(0, 1)],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 0, 0, 0, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert not crashed['collided']
    assert not crashed['exhausted']
    assert not crashed['headon']
    assert not crashed['seeds']
    assert landed == {"abee"}
    assert not lost


def test_apply_command_and_advance_no_command_bee_saved_from_exhaustion_by_flower():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[Flower(0, 1, DEFAULT_GAME_PARAMETERS, 1, 0, 1000).to_json()],
                                                      inflight={"abee": ("Bee", 0, 0, 0, 0, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert not crashed['collided']
    assert not crashed['exhausted']
    assert not crashed['headon']
    assert not crashed['seeds']
    assert not landed
    assert not lost


def test_apply_command_and_advance_no_command_two_bees_crash_headon():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 0, 0, 0, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0),
                                                                "anotherbee": ("Bee", 0, 1, 180, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert not crashed['collided']
    assert not crashed['exhausted']
    assert crashed['headon'] == {"abee", "anotherbee"}
    assert not crashed['seeds']
    assert not landed
    assert not lost


def test_apply_command_and_advance_no_command_two_bees_crash():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 0, 0, 0, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0),
                                                                "anotherbee": ("Bee", 0, 2, 180, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=None)
    
    assert crashed['collided'] == {"abee", "anotherbee"}
    assert not crashed['exhausted']
    assert not crashed['headon']
    assert not crashed['seeds']
    assert not landed
    assert not lost


def test_apply_command_and_advance_command_stops_two_bees_crashing():
    crashed, landed, lost = apply_command_and_advance(board_width=10,
                                                      board_height=10,
                                                      hives=[],
                                                      flowers=[],
                                                      inflight={"abee": ("Bee", 0, 0, 0, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0),
                                                                "anotherbee": ("Bee", 0, 2, 180, 100, DEFAULT_GAME_PARAMETERS._asdict(), 0)},
                                                      turn_num=0,
                                                      cmd=dict(entity="anotherbee", command=120))
    
    assert not crashed['collided']
    assert not crashed['exhausted']
    assert not crashed['headon']
    assert not crashed['seeds']
    assert not landed
    assert not lost


@pytest.mark.parametrize("heading", [60, 120, 180, -120, -60])
def test_is_on_course_with_itself(heading):
    assert is_on_course_with((0, 0), heading, (0, 0))


@pytest.mark.parametrize("y", range(1, 10))
def test_is_on_course_with(y):
    assert is_on_course_with((0, 0), 0, (0, y))


@pytest.mark.parametrize("heading", [60, 120, 180, -120, -60])
@pytest.mark.parametrize("y", range(1, 10))
def test_is_not_on_course_with(heading, y):
    assert not is_on_course_with((0, 0), heading, (0, y))

