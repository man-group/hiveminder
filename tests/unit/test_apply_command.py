from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.bee import Bee, QueenBee
from hiveminder.seed import Seed
from hiveminder.trap_seed import TrapSeed
from hiveminder.headings import LEGAL_HEADINGS
from hiveminder.flower import Flower
from hiveminder.venus_bee_trap import VenusBeeTrap
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from itertools import product
from mock import sentinel
import pytest
from hiveminder.hive import Hive
import sys


LEGAL_MOVES = {(0, 60),
               (0, 0),
               (0, -60),
               (60, 120),
               (60, 60),
               (60, 0),
               (120, 180),
               (120, 120),
               (120, 60),
               (180, -120),
               (180, 180),
               (180, 120),
               (-120, -60),
               (-120, -120),
               (-120, 180),
               (-60, 0),
               (-60, -60),
               (-60, -120)}


@pytest.mark.parametrize("initial_heading, new_heading", LEGAL_MOVES)
def test_apply_command_single_board_single_bee(initial_heading, new_heading):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)
    game.apply_commands([dict(entity=sentinel.bee_1, command=new_heading)])

    assert game.boards[0].inflight[sentinel.bee_1] == Bee(4, 5, new_heading, 10, DEFAULT_GAME_PARAMETERS)


@pytest.mark.parametrize("initial_heading, new_heading", LEGAL_MOVES)
def test_apply_command_single_board_multiple_bees(initial_heading, new_heading):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)
    game.boards[0].inflight[sentinel.bee_2] = Bee(5, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)
    game.boards[0].inflight[sentinel.bee_3] = Bee(6, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)

    game.apply_commands([dict(entity=sentinel.bee_1, command=new_heading)])

    assert game.boards[0].inflight[sentinel.bee_1] == Bee(4, 5, new_heading, 10, DEFAULT_GAME_PARAMETERS)
    assert game.boards[0].inflight[sentinel.bee_2] == Bee(5, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)
    assert game.boards[0].inflight[sentinel.bee_3] == Bee(6, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)


def test_apply_command_multiple_boards_single_bee():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=3,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives] * 3,
                     flowers=[sentinel.flowers] * 3,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    game.boards[1].inflight[sentinel.bee_2] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    game.boards[2].inflight[sentinel.bee_3] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)

    game.apply_commands([dict(entity=sentinel.bee_1, command=60),
                         None,
                         None])

    assert game.boards[0].inflight[sentinel.bee_1] == Bee(5, 5, 60, 10, DEFAULT_GAME_PARAMETERS)
    assert game.boards[1].inflight[sentinel.bee_2] == Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    assert game.boards[2].inflight[sentinel.bee_3] == Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)


def test_apply_command_no_command():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    game.apply_commands([None])

    assert game.boards[0].inflight[sentinel.bee_1] == Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)


@pytest.mark.parametrize("initial_heading, new_heading", set(product(LEGAL_HEADINGS, range(-180, 180, 10))) - LEGAL_MOVES)
def test_apply_command_illegal_heading(initial_heading, new_heading):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, initial_heading, 10, DEFAULT_GAME_PARAMETERS)

    with pytest.raises(RuntimeError) as err:
        game.apply_commands([dict(entity=sentinel.bee_1, command=new_heading)])

    assert str(err.value).startswith("Can not rotate to heading")


def test_apply_command_unknown_bee():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    with pytest.raises(RuntimeError) as err:
        game.apply_commands([dict(entity=sentinel.bee_2, command=0)])

    assert str(err.value) == "Unknown entity."


def test_apply_command_bee_in_wrong_board():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=2,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives] * 2,
                     flowers=[sentinel.flowers] * 2,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    with pytest.raises(RuntimeError) as err:
        game.apply_commands([None, dict(entity=sentinel.bee_1, command=0)])

    assert str(err.value) == "Unknown entity."


def test_apply_command_not_enough_commands():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=2,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives] * 2,
                     flowers=[sentinel.flowers] * 2,
                     game_length=sentinel.game_length)

    game.boards[1].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    with pytest.raises(ValueError) as err:
        game.apply_commands([dict(entity=sentinel.bee_1, command=0)])

    assert str(err.value) == "You must specify a command for each board."


def test_apply_command_too_many_commands():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    with pytest.raises(ValueError) as err:
        game.apply_commands([dict(entity=sentinel.bee_1, command=0), None])

    assert str(err.value) == "You must specify a command for each board."


def test_apply_flower_command_empty_tile():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = Seed(4, 5, 0)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS),
                                      Flower(4, 5, DEFAULT_GAME_PARAMETERS, expires=12645))
    assert game.boards[0].hives == (Hive(9, 9),)


def test_apply_venus_command_empty_tile():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(4, 5, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS),
                                      VenusBeeTrap(4, 5, DEFAULT_GAME_PARAMETERS, expires=12645))
    assert game.boards[0].hives == (Hive(9, 9),)


def test_apply_flower_command_over_existing_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = Seed(0, 0, 0)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS, 1, 0, expires=12345 + DEFAULT_GAME_PARAMETERS.flower_lifespan),)
    assert game.boards[0].hives == (Hive(9, 9),)


def test_apply_venus_command_over_existing_single_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(0, 0, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {sentinel.seed_1: TrapSeed(0, 0, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits),)
    assert game.boards[0].hives == (Hive(9, 9),)


def test_apply_venus_command_over_existing_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits), Flower(9, 9, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits)),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(0, 0, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {}
    assert sorted(map(str, game.boards[0].flowers)) == sorted(map(str, (VenusBeeTrap(0, 0, DEFAULT_GAME_PARAMETERS, 1, 0, expires=12345 + DEFAULT_GAME_PARAMETERS.flower_lifespan),
                                                                        Flower(9, 9, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits))))
    assert game.boards[0].hives == (Hive(9, 9),)


def test_apply_flower_command_over_existing_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = Seed(9, 9, 0)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS), Flower(9, 9, DEFAULT_GAME_PARAMETERS, expires=12345 + DEFAULT_GAME_PARAMETERS.flower_lifespan))
    assert game.boards[0].hives == ()


def test_apply_venus_command_over_existing_single_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9),),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 9, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {sentinel.seed_1:TrapSeed(9, 9, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS),)
    assert game.boards[0].hives == (Hive(9, 9),)
    

def test_apply_venus_command_over_existing_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(9, 9), Hive(0, 0)),),
                     flowers=((Flower(0, 0, DEFAULT_GAME_PARAMETERS),),),
                     turn_num=12345,
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = TrapSeed(9, 9, 0, DEFAULT_GAME_PARAMETERS.trap_seed_lifespan)
    game.apply_commands([dict(entity=sentinel.seed_1, command="flower")])

    assert game.boards[0].inflight == {}
    assert game.boards[0].flowers == (Flower(0, 0, DEFAULT_GAME_PARAMETERS), VenusBeeTrap(9, 9, DEFAULT_GAME_PARAMETERS, expires=12345 + DEFAULT_GAME_PARAMETERS.flower_lifespan))
    assert game.boards[0].hives == (Hive(0, 0),)



def test_bees_can_not_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)

    with pytest.raises(RuntimeError) as err:
        game.apply_commands([dict(entity=sentinel.bee_1, command="flower")])

    assert str(err.value).startswith("Can not rotate to heading")


def test_only_queenbees_can_create_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[[]],
                     flowers=[[Flower(1, 2, DEFAULT_GAME_PARAMETERS)]],
                     game_length=sentinel.game_length)

    queen_bee = QueenBee(4, 4, 0, 10, DEFAULT_GAME_PARAMETERS, nectar=sentinel.nectar)
    game.boards[0].inflight[sentinel.bee_1] = Bee(4, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    game.boards[0].inflight[sentinel.queenbee_1] = queen_bee
    game.boards[0].inflight[sentinel.seed_1] = Seed(3, 3, 0)

    with pytest.raises(RuntimeError):
        game.apply_commands([dict(entity=sentinel.bee_1, command="create_hive")])

    with pytest.raises(RuntimeError):
        game.apply_commands([dict(entity=sentinel.seed_1, command="create_hive")])

    game.apply_commands([dict(entity=sentinel.queenbee_1, command="create_hive")])
    assert game.boards[0].hives[0] == Hive(queen_bee.x, queen_bee.y, queen_bee.nectar)
    assert len(game.boards[0].inflight) == 2


def test_create_hive_deletes_flower():
    queen_bee = QueenBee(1, 2, 0, 10, DEFAULT_GAME_PARAMETERS, nectar=sentinel.nectar)
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[[]],
                     flowers=[[Flower(queen_bee.x, queen_bee.y, DEFAULT_GAME_PARAMETERS)]],
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.queenbee_1] = queen_bee

    game.apply_commands([dict(entity=sentinel.queenbee_1, command="create_hive")])
    assert game.boards[0].hives[0] == Hive(queen_bee.x, queen_bee.y, queen_bee.nectar)
    assert len(game.boards[0].inflight) == 0
    assert len(game.boards[0].flowers) == 0
