from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest


@pytest.mark.parametrize("turn_num, game_length, game_over", [(0, 1, False),
                                                              (1, 1, True),
                                                              (2, 1, True),
                                                              (0, 10, False),
                                                              (1, 10, False),
                                                              (2, 10, False),
                                                              (3, 10, False),
                                                              (4, 10, False),
                                                              (5, 10, False),
                                                              (6, 10, False),
                                                              (7, 10, False),
                                                              (8, 10, False),
                                                              (9, 10, False),
                                                              (10, 10, True),
                                                              (11, 10, True),
                                                              ])
def test_game_over(turn_num, game_length, game_over):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     turn_num=turn_num,
                     game_length=game_length)
    
    assert game.game_over() == game_over
