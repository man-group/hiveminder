from hiveminder.board import volant_from_json
from hiveminder.bee import Bee, QueenBee
from hiveminder.seed import Seed
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest

@pytest.mark.parametrize("json, expected_type", [(["Bee", sentinel.x, sentinel.y, sentinel.h, sentinel.e, DEFAULT_GAME_PARAMETERS._asdict(), sentinel.n], Bee),
                                                 (["QueenBee", sentinel.x, sentinel.y, sentinel.h, sentinel.e, DEFAULT_GAME_PARAMETERS._asdict(), sentinel.n], QueenBee),
                                                 (["Seed", sentinel.x, sentinel.y, sentinel.h], Seed),
                                                 ])
def test_volant_from_json(json, expected_type):
    assert isinstance(volant_from_json(json), expected_type)
