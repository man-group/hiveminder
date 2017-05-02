from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.flower import Flower
from hiveminder.venus_bee_trap import VenusBeeTrap
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest


def test_no_expiry_causes_error():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[[Flower(sentinel.x,
                                      sentinel.y,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency,
                                      sentinel.visits,
                                      expires=None)]],
                     turn_num=0,
                     game_length=sentinel.game_length)
    
    with pytest.raises(RuntimeError):
        game.remove_dead_flowers()


def test_flowers_remain_if_unexpired():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[[Flower(sentinel.x,
                                      sentinel.y,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency,
                                      sentinel.visits,
                                      expires=100)]],
                     turn_num=0,
                     game_length=sentinel.game_length)
    
    game.remove_dead_flowers()
    
    assert game.boards[0].flowers == (Flower(sentinel.x,
                                             sentinel.y,
                                             DEFAULT_GAME_PARAMETERS,
                                             sentinel.potency,
                                             sentinel.visits,
                                             expires=100),)


def test_venus_remain_if_unexpired():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[[Flower(sentinel.x,
                                      sentinel.y,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency,
                                      sentinel.visits,
                                      expires=100),
                               VenusBeeTrap(sentinel.x,
                                      sentinel.y,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency,
                                      sentinel.visits,
                                      expires=100)]],
                     turn_num=0,
                     game_length=sentinel.game_length)

    game.remove_dead_flowers()

    assert game.boards[0].flowers == (Flower(sentinel.x,
                                             sentinel.y,
                                             DEFAULT_GAME_PARAMETERS,
                                             sentinel.potency,
                                             sentinel.visits,
                                             expires=100),
                                      VenusBeeTrap(sentinel.x,
                                             sentinel.y,
                                             DEFAULT_GAME_PARAMETERS,
                                             sentinel.potency,
                                             sentinel.visits,
                                             expires=100),)


def test_flowers_and_venus_removed_if_expired():
    flowers = [
        Flower(sentinel.x,
               sentinel.y,
                DEFAULT_GAME_PARAMETERS,
               sentinel.potency,
               sentinel.visits,
               expires=99),
        Flower(sentinel.x,
               sentinel.y,
               DEFAULT_GAME_PARAMETERS,
               sentinel.potency,
               sentinel.visits,
               expires=102),
        VenusBeeTrap(sentinel.x,
                     sentinel.y,
                     DEFAULT_GAME_PARAMETERS,
                     sentinel.potency,
                     sentinel.visits,
                     expires=99),
        VenusBeeTrap(sentinel.x,
                     sentinel.y,
                     DEFAULT_GAME_PARAMETERS,
                     sentinel.potency,
                     sentinel.visits,
                     expires=102)
    ]
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[flowers],
                     turn_num=100,
                     game_length=sentinel.game_length)

    game.remove_dead_flowers()

    assert game.boards[0].flowers == (flowers[1], flowers[3])


def test_keep_one_healthy_flower_if_all_expired():
    healthy_flower = Flower(sentinel.x,
               sentinel.y,
               DEFAULT_GAME_PARAMETERS,
               sentinel.potency,
               sentinel.visits,
               expires=99)
    venus = VenusBeeTrap(sentinel.x,
               sentinel.y,
               DEFAULT_GAME_PARAMETERS,
               sentinel.potency,
               sentinel.visits,
               expires=99)
    flowers = [
        healthy_flower,
        venus
    ]
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[flowers],
                     turn_num=100,
                     game_length=sentinel.game_length)

    game.remove_dead_flowers()

    assert len(game.boards[0].flowers) == 1
    assert game.boards[0].flowers[0] == healthy_flower


def test_remove_over_expired_flowers_if_new_are_made():
    flowers = [
        Flower(sentinel.x,
               sentinel.y,
               DEFAULT_GAME_PARAMETERS,
               sentinel.potency,
               sentinel.visits,
               expires=99)
    ]
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[flowers],
                     turn_num=100,
                     game_length=sentinel.game_length)

    game.remove_dead_flowers()

    assert len(game.boards[0].flowers) == 1
    assert game.boards[0].flowers[0] in flowers

    flower = Flower(sentinel.x,
                   sentinel.y,
                   DEFAULT_GAME_PARAMETERS,
                   sentinel.potency,
                   sentinel.visits,
                   expires=203)

    game.boards[0].flowers += (flower,)
    game.remove_dead_flowers()

    assert len(game.boards[0].flowers) == 1
    assert game.boards[0].flowers[0] == flower


def test_only_expired_flowers_removed_from_mixed_bunch():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[[Flower(sentinel.x1,
                                      sentinel.y1,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency1,
                                      sentinel.visits1,
                                      expires=10),
                               Flower(sentinel.x2,
                                      sentinel.y2,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency2,
                                      sentinel.visits2,
                                      expires=50),
                               Flower(sentinel.x3,
                                      sentinel.y3,
                                      DEFAULT_GAME_PARAMETERS,
                                      sentinel.potency3,
                                      sentinel.visits3,
                                      expires=100),
                               VenusBeeTrap(sentinel.x3,
                                            sentinel.y3,
                                            DEFAULT_GAME_PARAMETERS,
                                            sentinel.potency3,
                                            sentinel.visits3,
                                            expires=50),
                               VenusBeeTrap(sentinel.x3,
                                            sentinel.y3,
                                            DEFAULT_GAME_PARAMETERS,
                                            sentinel.potency3,
                                            sentinel.visits3,
                                            expires=100),
                               ]],
                     turn_num=75,
                     game_length=sentinel.game_length)
    
    game.remove_dead_flowers()
    
    assert game.boards[0].flowers == (Flower(sentinel.x3,
                                             sentinel.y3,
                                             DEFAULT_GAME_PARAMETERS,
                                             sentinel.potency3,
                                             sentinel.visits3,
                                             expires=100),
                                      VenusBeeTrap(sentinel.x3,
                                                   sentinel.y3,
                                                   DEFAULT_GAME_PARAMETERS,
                                                   sentinel.potency3,
                                                   sentinel.visits3,
                                                   expires=100),)


def test_do_nothing_if_there_are_no_flowers():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[[]],
                     turn_num=100,
                     game_length=sentinel.game_length)

    game.remove_dead_flowers()

    assert len(game.boards[0].flowers) == 0


def test_expire_venus_flowers_when_there_are_no_healthy_flowers():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives],
                     flowers=[[VenusBeeTrap(sentinel.x1,
                                            sentinel.y1,
                                            DEFAULT_GAME_PARAMETERS,
                                            sentinel.potency,
                                            sentinel.visits,
                                            expires=100),
                               VenusBeeTrap(sentinel.x2,
                                            sentinel.y2,
                                            DEFAULT_GAME_PARAMETERS,
                                            sentinel.potency,
                                            sentinel.visits,
                                            expires=200)]],
                     turn_num=100,
                     game_length=sentinel.game_length)

    game.remove_dead_flowers()

    assert game.boards[0].flowers == (VenusBeeTrap(sentinel.x2,
                                                   sentinel.y2,
                                                   DEFAULT_GAME_PARAMETERS,
                                                   sentinel.potency,
                                                   sentinel.visits,
                                                   expires=200),)
