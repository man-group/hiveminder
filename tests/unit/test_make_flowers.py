from __future__ import division
from hiveminder.game import make_flowers
from hiveminder.hive import Hive
from hiveminder._util import even_q_distance as distance
from hiveminder.game import GameState
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from random import Random
from mock import Mock, sentinel

import pytest
from hiveminder.seed import Seed


TEST_PARAMETERS = [(6, 6, [Hive(3, 3)]),
                   (12, 12, [Hive(3, 4)]),
                   (8, 5, [Hive(6, 2)]),
                   (12, 12, [Hive(3, 4), Hive(5, 7)]),
                   (8, 5, [Hive(6, 2), Hive(1, 1)]),
                   ]


def _test_make_flowers_impl(width, height, hives):
    # Mock the random number generator so it returns all the tiles
    # not just a sample.
    mock_rng = Mock(name="mock_rng")
    mock_rng.sample.side_effect = lambda arr, n: arr

    return make_flowers(sentinel.n, hives, width, height, mock_rng, DEFAULT_GAME_PARAMETERS)


@pytest.mark.parametrize("width, height, hives", TEST_PARAMETERS)
def test_flowers_created_close_to_hives(width, height, hives):
    flowers = _test_make_flowers_impl(width, height, hives)

    for flower in flowers:
        d = 100000000
        for hive in hives:
            d = min(d, distance(flower.x, flower.y, hive.x, hive.y))
        assert d <= DEFAULT_GAME_PARAMETERS.initial_energy // 2


def test_flowers_seeds_make_flowers_means_points():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.seed_1] = Seed(4, 5, 0)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert all(board.calculate_score() == (DEFAULT_GAME_PARAMETERS.hive_score_factor + DEFAULT_GAME_PARAMETERS.flower_score_factor)
                                            for board in game.boards)


@pytest.mark.parametrize("width, height, hives", TEST_PARAMETERS)
def test_flowers_created_not_too_close_to_hives(width, height, hives):
    flowers = _test_make_flowers_impl(width, height, hives)

    for flower in flowers:
        for hive in hives:
            assert distance(flower.x, flower.y, hive.x, hive.y) > 1


@pytest.mark.parametrize("width, height, hives", TEST_PARAMETERS)
def test_flowers_created_at_minimum_potency(width, height, hives):
    for flower in _test_make_flowers_impl(width, height, hives):
        assert flower.potency == 1


@pytest.mark.parametrize("n", range(24))
def test_the_specified_number_of_flowers_are_created(n):
    assert len(make_flowers(n, [Hive(3, 3)], 8, 7, Random(0), DEFAULT_GAME_PARAMETERS)) == n
