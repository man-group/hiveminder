from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.seed import Seed
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest


def move_seeds_test_impl(boards, from_details, to_board, to_details):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=boards,
                     board_width=10,
                     board_height=10,
                     hives=[sentinel.hives] * boards,
                     flowers=[sentinel.flowers] * boards,
                     game_length=sentinel.game_length)
      
    game.boards[0].inflight[sentinel.seed_1] = from_details
    game.move_volants()
 
    assert [i for i, board in enumerate(game.boards) if sentinel.seed_1 in board.inflight] == [to_board]    
    assert game.boards[to_board].inflight == {sentinel.seed_1 : to_details}


@pytest.mark.parametrize(("from_details", "to_details"), [(Seed(4, 5, 0), Seed(4, 6, 0)),
                                                          (Seed(4, 5, 180), Seed(4, 4, 180)),
                                                          (Seed(4, 5, 60), Seed(5, 6, 60)),
                                                          (Seed(4, 5, 120), Seed(5, 5, 120)),
                                                          (Seed(4, 5, -60), Seed(3, 6, -60)),
                                                          (Seed(4, 5, -120), Seed(3, 5, -120)),
                                                          (Seed(5, 5, 0), Seed(5, 6, 0)),
                                                          (Seed(5, 5, 180), Seed(5, 4, 180)),
                                                          (Seed(5, 5, 60), Seed(6, 5, 60)),
                                                          (Seed(5, 5, 120), Seed(6, 4, 120)),
                                                          (Seed(5, 5, -60), Seed(4, 5, -60)),
                                                          (Seed(5, 5, -120), Seed(4, 4, -120)),
                                                          ])
def test_move_seeds_no_routing(from_details, to_details):
    move_seeds_test_impl(1, from_details, 0, to_details)


@pytest.mark.parametrize(("from_details", "to_details"), [(Seed(5, 9, 0), Seed(5, 0, 0)),         # North
                                                          (Seed(4, 9, 0), Seed(4, 0, 0)),         #
                                                          (Seed(9, 9, 0), Seed(9, 0, 0)),         #
                                                          (Seed(0, 9, 0), Seed(0, 0, 0)),         #
                                                          (Seed(0, 9, 60), Seed(1, 0, 60)),       #
                                                          (Seed(4, 9, 60), Seed(5, 0, 60)),       #
                                                          (Seed(4, 9, -60), Seed(3, 0, -60)),     #

                                                          (Seed(4, 0, 180), Seed(4, 9, 180)),     # South
                                                          (Seed(5, 0, 180), Seed(5, 9, 180)),     #
                                                          (Seed(0, 0, 180), Seed(0, 9, 180)),     #
                                                          (Seed(9, 0, 180), Seed(9, 9, 180)),     #
                                                          (Seed(5, 0, 120), Seed(6, 9, 120)),     #
                                                          (Seed(5, 0, -120), Seed(4, 9, -120)),   #
                                                          (Seed(9, 0, -120), Seed(8, 9, -120)),   #
            
                                                          (Seed(0, 5, -60), Seed(9, 6, -60)),     # West
                                                          (Seed(0, 0, -60), Seed(9, 1, -60)),     #
                                                          (Seed(0, 5, -120), Seed(9, 5, -120)),   #
                                                          (Seed(0, 0, -120), Seed(9, 0, -120)),   #
                                                          (Seed(0, 9, -120), Seed(9, 9, -120)),   #
            
                                                          (Seed(9, 5, 60), Seed(0, 5, 60)),       # East
                                                          (Seed(9, 0, 60), Seed(0, 0, 60)),       #
                                                          (Seed(9, 9, 60), Seed(0, 9, 60)),       #
                                                          (Seed(9, 5, 120), Seed(0, 4, 120)),     #
                                                          (Seed(9, 9, 120), Seed(0, 8, 120)),     #
                                                          
                                                          (Seed(9, 0, 120), Seed(0, 9, 120)),     # South East
                                                          
                                                          (Seed(0, 9, -60), Seed(9, 0, -60)),     # North West
                                                          ])
def test_single_board_routes_to_itself_on_all_sides(from_details, to_details):
    move_seeds_test_impl(1, from_details, 0, to_details)
 
 
@pytest.mark.parametrize(("from_details", "to_board", "to_details"), [(Seed(5, 9, 0), 1, Seed(5, 0, 0)),         # North
                                                                      (Seed(4, 9, 0), 1, Seed(4, 0, 0)),         #
                                                                      (Seed(9, 9, 0), 1, Seed(9, 0, 0)),         #
                                                                      (Seed(0, 9, 0), 1, Seed(0, 0, 0)),         #
                                                                      (Seed(0, 9, 60), 1, Seed(1, 0, 60)),       #
                                                                      (Seed(4, 9, 60), 1, Seed(5, 0, 60)),       #
                                                                      (Seed(4, 9, -60), 1, Seed(3, 0, -60)),     #

                                                                      (Seed(4, 0, 180), 1, Seed(4, 9, 180)),     # South
                                                                      (Seed(5, 0, 180), 1, Seed(5, 9, 180)),     #
                                                                      (Seed(0, 0, 180), 1, Seed(0, 9, 180)),     #
                                                                      (Seed(9, 0, 180), 1, Seed(9, 9, 180)),     #
                                                                      (Seed(5, 0, 120), 1, Seed(6, 9, 120)),     #
                                                                      (Seed(5, 0, -120), 1, Seed(4, 9, -120)),   #
                                                                      (Seed(9, 0, -120), 1, Seed(8, 9, -120)),   #
            
                                                                      (Seed(0, 5, -60), 1, Seed(9, 6, -60)),     # West
                                                                      (Seed(0, 0, -60), 1, Seed(9, 1, -60)),     #
                                                                      (Seed(0, 5, -120), 1, Seed(9, 5, -120)),   #
                                                                      (Seed(0, 0, -120), 1, Seed(9, 0, -120)),   #
                                                                      (Seed(0, 9, -120), 1, Seed(9, 9, -120)),   #
            
                                                                      (Seed(9, 5, 60), 1, Seed(0, 5, 60)),       # East
                                                                      (Seed(9, 0, 60), 1, Seed(0, 0, 60)),       #
                                                                      (Seed(9, 9, 60), 1, Seed(0, 9, 60)),       #
                                                                      (Seed(9, 5, 120), 1, Seed(0, 4, 120)),     #
                                                                      (Seed(9, 9, 120), 1, Seed(0, 8, 120)),     #
                                                                      
                                                                      (Seed(9, 0, 120), 0, Seed(0, 9, 120)),     # South East
                                                                      
                                                                      (Seed(0, 9, -60), 0, Seed(9, 0, -60)),     # North West
                                                                      ])
def test_two_boards_route_to_each_other(from_details, to_board, to_details):
    move_seeds_test_impl(2, from_details, to_board, to_details)
 
 
@pytest.mark.parametrize(("from_details", "to_board", "to_details"), [(Seed(5, 9, 0), 3, Seed(5, 0, 0)),         # North
                                                                      (Seed(4, 9, 0), 3, Seed(4, 0, 0)),         #
                                                                      (Seed(9, 9, 0), 3, Seed(9, 0, 0)),         #
                                                                      (Seed(0, 9, 0), 3, Seed(0, 0, 0)),         #
                                                                      (Seed(0, 9, 60), 3, Seed(1, 0, 60)),       #
                                                                      (Seed(4, 9, 60), 3, Seed(5, 0, 60)),       #
                                                                      (Seed(4, 9, -60), 3, Seed(3, 0, -60)),     #

                                                                      (Seed(4, 0, 180), 4, Seed(4, 9, 180)),     # South
                                                                      (Seed(5, 0, 180), 4, Seed(5, 9, 180)),     #
                                                                      (Seed(0, 0, 180), 4, Seed(0, 9, 180)),     #
                                                                      (Seed(9, 0, 180), 4, Seed(9, 9, 180)),     #
                                                                      (Seed(5, 0, 120), 4, Seed(6, 9, 120)),     #
                                                                      (Seed(5, 0, -120), 4, Seed(4, 9, -120)),   #
                                                                      (Seed(9, 0, -120), 4, Seed(8, 9, -120)),   #
            
                                                                      (Seed(0, 5, -60), 6, Seed(9, 6, -60)),     # West
                                                                      (Seed(0, 0, -60), 6, Seed(9, 1, -60)),     #
                                                                      (Seed(0, 5, -120), 6, Seed(9, 5, -120)),   #
                                                                      (Seed(0, 0, -120), 6, Seed(9, 0, -120)),   #
                                                                      (Seed(0, 9, -120), 6, Seed(9, 9, -120)),   #
            
                                                                      (Seed(9, 5, 60), 1, Seed(0, 5, 60)),       # East
                                                                      (Seed(9, 0, 60), 1, Seed(0, 0, 60)),       #
                                                                      (Seed(9, 9, 60), 1, Seed(0, 9, 60)),       #
                                                                      (Seed(9, 5, 120), 1, Seed(0, 4, 120)),     #
                                                                      (Seed(9, 9, 120), 1, Seed(0, 8, 120)),     #
                                                                      
                                                                      (Seed(9, 0, 120), 5, Seed(0, 9, 120)),     # South East
                                                                      
                                                                      (Seed(0, 9, -60), 2, Seed(9, 0, -60)),     # North West
                                                                      ])
def test_seven_boards_routing(from_details, to_board, to_details):
    move_seeds_test_impl(7, from_details, to_board, to_details)
       
