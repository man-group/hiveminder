from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
from .test_bee import BEE_TYPES
import pytest


def move_bees_test_impl(bee_type, boards, from_details, to_board, to_details):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=boards,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives] * boards,
                     flowers=[sentinel.flowers] * boards,
                     game_length=sentinel.game_length)

    x, y, h, e, n = from_details
    xt, yt, ht, et, nt = to_details
    game.boards[0].inflight[sentinel.bee_1] = bee_type(x, y, h, e, DEFAULT_GAME_PARAMETERS, n)
    game.move_volants()

    assert [i for i, board in enumerate(game.boards) if sentinel.bee_1 in board.inflight] == [to_board]    
    assert game.boards[to_board].inflight == {sentinel.bee_1: bee_type(xt, yt, ht, et, DEFAULT_GAME_PARAMETERS, nt)}


@pytest.mark.parametrize("bee_type", BEE_TYPES)
@pytest.mark.parametrize(("from_details", "to_details"), [((4, 5, 0, 10, 0), (4, 6, 0, 9, 0)),
                                                          ((4, 5, 180, 10, 0), (4, 4, 180, 9, 0)),
                                                          ((4, 5, 60, 10, 0), (5, 6, 60, 9, 0)),
                                                          ((4, 5, 120, 10, 0), (5, 5, 120, 9, 0)),
                                                          ((4, 5, -60, 10, 0), (3, 6, -60, 9, 0)),
                                                          ((4, 5, -120, 10, 0), (3, 5, -120, 9, 0)),
                                                          ((5, 5, 0, 10, 0), (5, 6, 0, 9, 0)),
                                                          ((5, 5, 180, 10, 0), (5, 4, 180, 9, 0)),
                                                          ((5, 5, 60, 10, 0), (6, 5, 60, 9, 0)),
                                                          ((5, 5, 120, 10, 0), (6, 4, 120, 9, 0)),
                                                          ((5, 5, -60, 10, 0), (4, 5, -60, 9, 0)),
                                                          ((5, 5, -120, 10, 0), (4, 4, -120, 9, 0)),
                                                          ])
def test_move_bees_no_routing(bee_type, from_details, to_details):
    move_bees_test_impl(bee_type, 1, from_details, 0, to_details)


@pytest.mark.parametrize("bee_type", BEE_TYPES)
@pytest.mark.parametrize(("from_details", "to_details"), [((5, 9, 0, 10, 0), (5, 0, 0, 9, 0)),         # North
                                                          ((4, 9, 0, 10, 0), (4, 0, 0, 9, 0)),         #
                                                          ((9, 9, 0, 10, 0), (9, 0, 0, 9, 0)),         #
                                                          ((0, 9, 0, 10, 0), (0, 0, 0, 9, 0)),         #
                                                          ((0, 9, 60, 10, 0), (1, 0, 60, 9, 0)),       #
                                                          ((4, 9, 60, 10, 0), (5, 0, 60, 9, 0)),       #
                                                          ((4, 9, -60, 10, 0), (3, 0, -60, 9, 0)),     #

                                                          ((4, 0, 180, 10, 0), (4, 9, 180, 9, 0)),     # South
                                                          ((5, 0, 180, 10, 0), (5, 9, 180, 9, 0)),     #
                                                          ((0, 0, 180, 10, 0), (0, 9, 180, 9, 0)),     #
                                                          ((9, 0, 180, 10, 0), (9, 9, 180, 9, 0)),     #
                                                          ((5, 0, 120, 10, 0), (6, 9, 120, 9, 0)),     #
                                                          ((5, 0, -120, 10, 0), (4, 9, -120, 9, 0)),   #
                                                          ((9, 0, -120, 10, 0), (8, 9, -120, 9, 0)),   #
            
                                                          ((0, 5, -60, 10, 0), (9, 6, -60, 9, 0)),     # West
                                                          ((0, 0, -60, 10, 0), (9, 1, -60, 9, 0)),     #
                                                          ((0, 5, -120, 10, 0), (9, 5, -120, 9, 0)),   #
                                                          ((0, 0, -120, 10, 0), (9, 0, -120, 9, 0)),   #
                                                          ((0, 9, -120, 10, 0), (9, 9, -120, 9, 0)),   #
            
                                                          ((9, 5, 60, 10, 0), (0, 5, 60, 9, 0)),       # East
                                                          ((9, 0, 60, 10, 0), (0, 0, 60, 9, 0)),       #
                                                          ((9, 9, 60, 10, 0), (0, 9, 60, 9, 0)),       #
                                                          ((9, 5, 120, 10, 0), (0, 4, 120, 9, 0)),     #
                                                          ((9, 9, 120, 10, 0), (0, 8, 120, 9, 0)),     #
                                                          
                                                          ((9, 0, 120, 10, 0), (0, 9, 120, 9, 0)),     # South East
                                                          
                                                          ((0, 9, -60, 10, 0), (9, 0, -60, 9, 0)),     # North West
                                                          ])
def test_single_board_routes_to_itself_on_all_sides(bee_type, from_details, to_details):
    move_bees_test_impl(bee_type, 1, from_details, 0, to_details)
 
 
@pytest.mark.parametrize("bee_type", BEE_TYPES)
@pytest.mark.parametrize(("from_details", "to_board", "to_details"), [((5, 9, 0, 10, 0), 1, (5, 0, 0, 9, 0)),         # North
                                                                      ((4, 9, 0, 10, 0), 1, (4, 0, 0, 9, 0)),         #
                                                                      ((9, 9, 0, 10, 0), 1, (9, 0, 0, 9, 0)),         #
                                                                      ((0, 9, 0, 10, 0), 1, (0, 0, 0, 9, 0)),         #
                                                                      ((0, 9, 60, 10, 0), 1, (1, 0, 60, 9, 0)),       #
                                                                      ((4, 9, 60, 10, 0), 1, (5, 0, 60, 9, 0)),       #
                                                                      ((4, 9, -60, 10, 0), 1, (3, 0, -60, 9, 0)),     #

                                                                      ((4, 0, 180, 10, 0), 1, (4, 9, 180, 9, 0)),     # South
                                                                      ((5, 0, 180, 10, 0), 1, (5, 9, 180, 9, 0)),     #
                                                                      ((0, 0, 180, 10, 0), 1, (0, 9, 180, 9, 0)),     #
                                                                      ((9, 0, 180, 10, 0), 1, (9, 9, 180, 9, 0)),     #
                                                                      ((5, 0, 120, 10, 0), 1, (6, 9, 120, 9, 0)),     #
                                                                      ((5, 0, -120, 10, 0), 1, (4, 9, -120, 9, 0)),   #
                                                                      ((9, 0, -120, 10, 0), 1, (8, 9, -120, 9, 0)),   #
            
                                                                      ((0, 5, -60, 10, 0), 1, (9, 6, -60, 9, 0)),     # West
                                                                      ((0, 0, -60, 10, 0), 1, (9, 1, -60, 9, 0)),     #
                                                                      ((0, 5, -120, 10, 0), 1, (9, 5, -120, 9, 0)),   #
                                                                      ((0, 0, -120, 10, 0), 1, (9, 0, -120, 9, 0)),   #
                                                                      ((0, 9, -120, 10, 0), 1, (9, 9, -120, 9, 0)),   #
            
                                                                      ((9, 5, 60, 10, 0), 1, (0, 5, 60, 9, 0)),       # East
                                                                      ((9, 0, 60, 10, 0), 1, (0, 0, 60, 9, 0)),       #
                                                                      ((9, 9, 60, 10, 0), 1, (0, 9, 60, 9, 0)),       #
                                                                      ((9, 5, 120, 10, 0), 1, (0, 4, 120, 9, 0)),     #
                                                                      ((9, 9, 120, 10, 0), 1, (0, 8, 120, 9, 0)),     #
                                                                      
                                                                      ((9, 0, 120, 10, 0), 0, (0, 9, 120, 9, 0)),     # South East
                                                                      
                                                                      ((0, 9, -60, 10, 0), 0, (9, 0, -60, 9, 0)),     # North West
                                                                      ])
def test_two_boards_route_to_each_other(bee_type, from_details, to_board, to_details):
    move_bees_test_impl(bee_type, 2, from_details, to_board, to_details)
 
 
@pytest.mark.parametrize("bee_type", BEE_TYPES)
@pytest.mark.parametrize(("from_details", "to_board", "to_details"), [((5, 9, 0, 10, 0), 3, (5, 0, 0, 9, 0)),         # North
                                                                      ((4, 9, 0, 10, 0), 3, (4, 0, 0, 9, 0)),         #
                                                                      ((9, 9, 0, 10, 0), 3, (9, 0, 0, 9, 0)),         #
                                                                      ((0, 9, 0, 10, 0), 3, (0, 0, 0, 9, 0)),         #
                                                                      ((0, 9, 60, 10, 0), 3, (1, 0, 60, 9, 0)),       #
                                                                      ((4, 9, 60, 10, 0), 3, (5, 0, 60, 9, 0)),       #
                                                                      ((4, 9, -60, 10, 0), 3, (3, 0, -60, 9, 0)),     #

                                                                      ((4, 0, 180, 10, 0), 4, (4, 9, 180, 9, 0)),     # South
                                                                      ((5, 0, 180, 10, 0), 4, (5, 9, 180, 9, 0)),     #
                                                                      ((0, 0, 180, 10, 0), 4, (0, 9, 180, 9, 0)),     #
                                                                      ((9, 0, 180, 10, 0), 4, (9, 9, 180, 9, 0)),     #
                                                                      ((5, 0, 120, 10, 0), 4, (6, 9, 120, 9, 0)),     #
                                                                      ((5, 0, -120, 10, 0), 4, (4, 9, -120, 9, 0)),   #
                                                                      ((9, 0, -120, 10, 0), 4, (8, 9, -120, 9, 0)),   #
            
                                                                      ((0, 5, -60, 10, 0), 6, (9, 6, -60, 9, 0)),     # West
                                                                      ((0, 0, -60, 10, 0), 6, (9, 1, -60, 9, 0)),     #
                                                                      ((0, 5, -120, 10, 0), 6, (9, 5, -120, 9, 0)),   #
                                                                      ((0, 0, -120, 10, 0), 6, (9, 0, -120, 9, 0)),   #
                                                                      ((0, 9, -120, 10, 0), 6, (9, 9, -120, 9, 0)),   #
            
                                                                      ((9, 5, 60, 10, 0), 1, (0, 5, 60, 9, 0)),       # East
                                                                      ((9, 0, 60, 10, 0), 1, (0, 0, 60, 9, 0)),       #
                                                                      ((9, 9, 60, 10, 0), 1, (0, 9, 60, 9, 0)),       #
                                                                      ((9, 5, 120, 10, 0), 1, (0, 4, 120, 9, 0)),     #
                                                                      ((9, 9, 120, 10, 0), 1, (0, 8, 120, 9, 0)),     #
                                                                      
                                                                      ((9, 0, 120, 10, 0), 5, (0, 9, 120, 9, 0)),     # South East
                                                                      
                                                                      ((0, 9, -60, 10, 0), 2, (9, 0, -60, 9, 0)),     # North West
                                                                      ])
def test_seven_boards_routing(bee_type, from_details, to_board, to_details):
    move_bees_test_impl(bee_type, 7, from_details, to_board, to_details)

