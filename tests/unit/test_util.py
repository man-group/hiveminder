from hiveminder._util import is_even, sign, even_q_in_range, even_q_distance, _first
import pytest
from mock import sentinel


@pytest.mark.parametrize("i", range(1, 100))
def test_sign(i):
    assert sign(i) == 1
    assert sign(-i) == -1
    

def test_sign_of_zero():
    assert sign(0) == 0


@pytest.mark.parametrize("i", range(100))
def test_is_even(i):
    assert is_even(2 * i)
    assert not is_even(2 * i + 1)


def test_can_find_tiles_reachable_in_zero_moves():
    assert set(even_q_in_range(5, 5, 0)) == {(5, 5)}


def test_can_find_tiles_reachable_in_one_move():
    assert set(even_q_in_range(5, 5, 1)) == {(4, 5), (4, 4), (5, 6), (5, 5), (5, 4), (6, 5), (6, 4)}


def test_can_find_tiles_reachable_in_two_moves():
    assert set(even_q_in_range(5, 5, 2)) == {(3, 4), (3, 5), (3, 6), (4, 3), (4, 4), (4, 5), (4, 6),
                                             (5, 3), (5, 4), (5, 6), (5, 7), (6, 3), (6, 4), (6, 5),
                                             (6, 6), (7, 4), (7, 5), (7, 6), (5, 5)}


def test_can_find_tiles_reachable_in_three_moves():
    assert set(even_q_in_range(5, 5, 3)) == {(2, 3), (2, 4), (2, 5), (2, 6), (3, 3), (3, 4), (3, 5),
                                             (3, 6), (3, 7), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6),
                                             (4, 7), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
                                             (5, 8), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7),
                                             (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (8, 3), (8, 4),
                                             (8, 5), (8, 6)}


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
    assert distance == even_q_distance(col1, row1, col2, row2)
    assert distance == even_q_distance(col2, row2, col1, row1)


def test_first_of_empty_sequence():
    assert _first([]) is None
    assert _first(()) is None
    assert _first(set([])) is None
    assert _first({}) is None


def test_first_of_list():
    assert _first([sentinel.first, sentinel.second, sentinel.third]) == sentinel.first


def test_first_of_tuple():
    assert _first((sentinel.first, sentinel.second, sentinel.third)) == sentinel.first


def test_first_of_set():
    assert _first({sentinel.first}) == sentinel.first


def test_first_of_dict():
    assert _first({sentinel.first: sentinel.first_value}) == sentinel.first
