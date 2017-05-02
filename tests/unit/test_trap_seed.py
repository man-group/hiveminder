from hiveminder.trap_seed import TrapSeed
from hiveminder.seed import Seed
from hiveminder.headings import heading_to_delta, LEGAL_HEADINGS
from hiveminder._util import is_even
from mock import sentinel, Mock
import pytest
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from hiveminder.game_state import GameState
from hiveminder.hive import Hive
from hiveminder.venus_bee_trap import VenusBeeTrap
from hiveminder.bee import Bee
from hiveminder.flower import Flower

mock_game_params = Mock(trap_seed_lifespan=DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)


def test_can_not_hash_a_trap_TrapSeed():
    h = TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params)
    with pytest.raises(TypeError) as err:
        hash(h)
    assert str(err.value) == "unhashable type: 'TrapSeed'"


@pytest.mark.parametrize("x1, y1, heading1, x2, y2, heading2, are_equal",
                         [(sentinel.x, sentinel.y, sentinel.h,
                           sentinel.x, sentinel.y, sentinel.h, True),
                          (sentinel.x1, sentinel.y, sentinel.h,
                           sentinel.x, sentinel.y, sentinel.h, False),
                          (sentinel.x, sentinel.y1, sentinel.h,
                           sentinel.x, sentinel.y, sentinel.h, False),
                          (sentinel.x, sentinel.y, sentinel.h1,
                           sentinel.x, sentinel.y, sentinel.h, False),
                          ])
def test_TrapSeeds_equality(x1, y1, heading1, x2, y2, heading2, are_equal):
    h1 = TrapSeed(x1, y1, heading1, mock_game_params)
    h2 = TrapSeed(x2, y2, heading2, mock_game_params)
    assert (h1 == h2) == are_equal
    assert (h1 != h2) == (not are_equal)


def test_TrapSeed_not_equal_to_other_types():
    assert not (TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params) == sentinel.TrapSeed)
    assert TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params) != sentinel.TrapSeed

    assert not (TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params) == Seed(sentinel.x, sentinel.y, sentinel.h))
    assert TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params) != Seed(sentinel.x, sentinel.y, sentinel.h)

    assert not (Seed(sentinel.x, sentinel.y, sentinel.h) == TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params))
    assert Seed(sentinel.x, sentinel.y, sentinel.h) != TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params)


def test_can_convert_TrapSeed_to_json():
    assert (TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params.trap_seed_lifespan).to_json()
            == ["TrapSeed", sentinel.x, sentinel.y, sentinel.h, mock_game_params.trap_seed_lifespan])


def test_can_read_TrapSeed_from_json():
    assert TrapSeed.from_json([sentinel.type, sentinel.x, sentinel.y, sentinel.h, mock_game_params]) == TrapSeed(sentinel.x, sentinel.y, sentinel.h, mock_game_params)


def test_repr():
    assert repr(TrapSeed(1337, 2000, 123456, mock_game_params.trap_seed_lifespan)) == "TrapSeed(1337, 2000, 123456, {0})".format(mock_game_params.trap_seed_lifespan)


def test_str():
    assert str(TrapSeed(1337, 2000, 123456, mock_game_params.trap_seed_lifespan)) == "TrapSeed(1337, 2000, 123456, {0})".format(mock_game_params.trap_seed_lifespan)


def test_can_get_position_and_heading_from_a_TrapSeed():
    assert TrapSeed(sentinel.x, sentinel.y, sentinel.h, sentinel.lifespan).xyh == (sentinel.x, sentinel.y, sentinel.h)


def test_can_set_position():
    trapSeed = TrapSeed(sentinel.x, sentinel.y, sentinel.h, sentinel.lifespan)
    assert trapSeed.set_position(sentinel.newx, sentinel.newy) == TrapSeed(sentinel.newx, sentinel.newy, sentinel.h, sentinel.lifespan)

    # Original instance is not actually changed
    assert trapSeed == TrapSeed(sentinel.x, sentinel.y, sentinel.h, sentinel.lifespan)


@pytest.mark.parametrize("heading", LEGAL_HEADINGS)
@pytest.mark.parametrize("column", [4, 5])
def test_can_advance_TrapSeed_along_a_heading_and_loses_lifespan(heading, column):
    # Rather than patch heading_to_delta in TrapSeed.advance we just
    # assert that the effect of advancing the TrapSeed matches that
    # defined by heading_to_delta

    expected_dx, expected_dy = heading_to_delta(heading, is_even(column))

    trapSeed = TrapSeed(column, 5, heading, 10)
    assert trapSeed.advance() == TrapSeed(column + expected_dx, 5 + expected_dy, heading, 9)

    # Original instance is not actually changed
    assert trapSeed == TrapSeed(column, 5, heading, 10)


def test_can_reverse_a_TrapSeed_along_a_heading_and_loses_lifespan():
    trapSeed = TrapSeed(5, 5, 0, 10)
    assert trapSeed.advance(reverse=True) == TrapSeed(5, 4, 180, 9)

    # Original instance is not actually changed
    assert trapSeed == TrapSeed(5, 5, 0, 10)


def test_trapseed_becomes_venus_after_10_moves():
    turn_num = 12345

    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 9),),),
                     flowers=((),),
                     turn_num=turn_num,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 8, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)

    for _ in range(DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + 1):
        game.turn([None])

    assert not [(_, volant) for (_, volant) in game.boards[0].inflight.items() if isinstance(volant, TrapSeed)]
    assert game.boards[0].flowers == ((VenusBeeTrap(9, 5, DEFAULT_GAME_PARAMETERS, expires=turn_num + DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + DEFAULT_GAME_PARAMETERS.flower_lifespan)),)
    assert game.boards[0].hives == (Hive(5, 9),)


def test_trapseed_becomes_venus_after_10_moves_on_top_of_a_hive():
    turn_num = 12345

    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 5), Hive(5, 5),),),
                     flowers=((),),
                     turn_num=turn_num,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 8, 0, mock_game_params.trap_seed_lifespan)

    for _ in range(DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + 1):
        game.turn([None])

    assert not [(_, volant) for (_, volant) in game.boards[0].inflight.items() if isinstance(volant, TrapSeed)]
    assert game.boards[0].flowers == ((VenusBeeTrap(9, 5, DEFAULT_GAME_PARAMETERS, expires=turn_num + DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + DEFAULT_GAME_PARAMETERS.flower_lifespan)),)
    assert game.boards[0].hives == (Hive(5, 5),)
    

def test_trapseed_does_not_become_venus_after_10_moves_on_top_of_only_flower():
    turn_num = 12345

    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((),),
                     flowers=((Flower(9, 5, DEFAULT_GAME_PARAMETERS, expires=20000),),),
                     turn_num=turn_num,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 8, 0, mock_game_params.trap_seed_lifespan)

    for _ in range(DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + 1):
        game.turn([None])

    assert {vid: volant for (vid, volant) in game.boards[0].inflight.items() if not isinstance(volant, Bee)} == {sentinel.seed_1: TrapSeed(9, 5, 0, -1)}
    assert game.boards[0].flowers == (Flower(9, 5, DEFAULT_GAME_PARAMETERS, expires=20000),)
    assert game.boards[0].hives == ()


def test_trapseed_becomes_venus_after_10_moves_on_top_of_a_flower():
    turn_num = 12345

    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((),),
                     flowers=((Flower(9, 5, DEFAULT_GAME_PARAMETERS, expires=20000), Flower(5, 5, DEFAULT_GAME_PARAMETERS, expires=20000)),),
                     turn_num=turn_num,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 8, 0, mock_game_params.trap_seed_lifespan)

    for _ in range(DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + 1):
        game.turn([None])

    assert not [(_, volant) for (_, volant) in game.boards[0].inflight.items() if isinstance(volant, TrapSeed)]
    assert sorted(map(str, game.boards[0].flowers)) == sorted(map(str,(VenusBeeTrap(9, 5, DEFAULT_GAME_PARAMETERS, expires=turn_num + DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + DEFAULT_GAME_PARAMETERS.flower_lifespan), Flower(5, 5, DEFAULT_GAME_PARAMETERS, expires=20000)))) 
    assert game.boards[0].hives == ()
    

def test_trapseed_does_not_become_venus_after_10_moves_on_top_of_only_hive():
    turn_num = 12345

    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 5),),),
                     flowers=((),),
                     turn_num=turn_num,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 8, 0, mock_game_params.trap_seed_lifespan)

    for _ in range(DEFAULT_GAME_PARAMETERS.trap_seed_lifespan + 1):
        game.turn([None])

    assert {vid: volant for (vid, volant) in game.boards[0].inflight.items() if not isinstance(volant, Bee)} == {sentinel.seed_1: TrapSeed(9, 5, 0, -1)}
    assert game.boards[0].flowers == ()
    assert game.boards[0].hives == (Hive(9, 5),)
