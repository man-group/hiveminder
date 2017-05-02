from __future__ import absolute_import
from hiveminder.bee import QueenBee
from hiveminder.hive import Hive
from hiveminder.flower import Flower
from hiveminder.game_api import initialise_game
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest


def test_queenbees_die_immediately_when_landing_on_hives():
    game = initialise_game(DEFAULT_GAME_PARAMETERS, 1, 10, 10, 1, 0, 23)
    game.boards[0].hives = (Hive(4, 4, 0),)
    game.boards[0].flowers = (Flower(1, 1, DEFAULT_GAME_PARAMETERS, expires=9999),)
    # create queen bee that will land on hive on the next move
    game.boards[0].inflight = {sentinel.queenbee_id: QueenBee(4, 5, 180, 10, DEFAULT_GAME_PARAMETERS)}
    # with no command, queen bee should land and die
    game.turn([None])
    # make sure the queen is gone and can't execute a hive command on top of existing hive
    with pytest.raises(RuntimeError) as err:
        game.turn([{"entity": sentinel.queenbee_id, "command": "create_hive"}])
    assert "Unknown entity" in str(err.value)


def test_queenbees_cant_create_hive_on_top_of_existing_hive():
    game = initialise_game(DEFAULT_GAME_PARAMETERS, 1, 10, 10, 1, 0, 23)
    board = game.boards[0]
    board.hives = (Hive(4, 4, 10),)
    board.flowers = (Flower(1, 1, DEFAULT_GAME_PARAMETERS, expires=9999),)
    # create queen bee on top of existing hive, like it has just launched
    board.inflight = {sentinel.queenbee_id: QueenBee(4, 4, 180, 10, DEFAULT_GAME_PARAMETERS)}
    # immediately create hive
    game.turn([{"entity": sentinel.queenbee_id, "command": "create_hive"}])
    # should only be one hive (not two)
    assert len(board.hives) == 1
    # it should be the new hive not the original (with 10 nectar)
    assert board.hives[0].nectar == 0
    # queen bee should be gone as she has 'hived'
    assert sentinel.queenbee_id not in board.inflight

