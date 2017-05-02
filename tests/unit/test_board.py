from __future__ import absolute_import

from hiveminder.board import Board
from hiveminder.game import GameState
from hiveminder.hive import Hive
from hiveminder.flower import Flower
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS, GameParameters
from mock import sentinel, patch, Mock
from random import Random
import pytest


def test_single_board_neighbours_itself_on_all_sides():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=sentinel.board_width,
                     board_height=sentinel.board_height,
                     hives=[sentinel.hives],
                     flowers=[sentinel.flowers],
                     game_length=sentinel.game_length)
    
    assert len(game.boards) == 1
    board = game.boards[0]
    assert board._neighbours == {"N": board,
                                 "S": board,
                                 "E": board,
                                 "W": board,
                                 "NW": board,
                                 "SE": board}


def lag(arr, n):
    l = len(arr)
    n = (n + l) % l
    return (arr * 2)[n:n + l]


@pytest.mark.parametrize("nboards", range(1, 16))
def test_multiple_boards_neighbours(nboards):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=nboards,
                     board_width=sentinel.board_width,
                     board_height=sentinel.board_height,
                     hives=[sentinel.hives] * nboards,
                     flowers=[sentinel.flowers] * nboards,
                     game_length=sentinel.game_length)
    
    assert len(game.boards) == nboards
    for s, se, w, board, e, nw, n in zip(*[lag(game.boards, i) for i in range(-3, 4)]):
        assert board._neighbours == {"N": n,
                                     "S": s,
                                     "E": e,
                                     "W": w,
                                     "NW": nw,
                                     "SE": se}


@pytest.mark.parametrize("nboards", range(1, 16))
def test_serialise_deserialise_game_state_to_json(nboards):
    params = GameParameters(launch_probability=1.0,
                            initial_energy=10,
                            dead_bee_score_factor=-5,
                            hive_score_factor=100,
                            flower_score_factor=100,
                            nectar_score_factor=2,
                            queen_bee_nectar_threshold=20,
                            bee_nectar_capacity=5,
                            bee_energy_boost_per_nectar=25,
                            flower_seed_visit_initial_threshold=10,
                            flower_seed_visit_subsequent_threshold=10,
                            flower_visit_potency_ratio=10,
                            flower_lifespan=100,
                            flower_lifespan_visit_impact=30,
                            trap_seed_probability=1,
                            venus_score_factor=-50,
                            trap_seed_lifespan=10)

    game = GameState(game_params=params,
                     game_id=sentinel.game_id,
                     boards=nboards,
                     board_width=sentinel.board_width,
                     board_height=sentinel.board_height,
                     hives=[(Hive(sentinel.hive_x, sentinel.hive_y, 23 * nboards),)] * nboards,
                     flowers=[(Flower(sentinel.fx, sentinel.fy, DEFAULT_GAME_PARAMETERS, sentinel.flower_size),)] * nboards,
                     game_length=sentinel.game_length)
    # make sure there are some bees on the boards, and some of them will be queens
    # as the nectar in the hives should be over the queen making threshold
    with patch("hiveminder.game_state.rngs", {sentinel.game_id: Random(0)}):
        game.launch_bees(sentinel.turn_num)

    game_state_json = game.to_json()
    game_state_bounce = game.from_json(game_state_json)
    assert game == game_state_bounce


def test_board_receives_incoming():
    incoming = {sentinel.incoming_volant_id: sentinel.incoming_volant}
    b = Board(sentinel.game_params, sentinel.width, sentinel.height, sentinel.hives, sentinel.flowers, sentinel.neighbours, {sentinel.bee1_id: sentinel.bee1})
    b._incoming = incoming
    received_volants = b.receive_volants()
    assert received_volants == incoming
    assert b.inflight == {sentinel.bee1_id: sentinel.bee1, sentinel.incoming_volant_id: sentinel.incoming_volant}


@pytest.mark.parametrize(['inflight', 'expected_sent_volants', 'neighbour_sent_to'],
                         [
                             ({sentinel.volant1: Mock(x=0, y=1, set_position=lambda s, *args: sentinel.new_volant1), sentinel.volant2: Mock(x=0, y=0)}, {sentinel.volant1: sentinel.new_volant1}, 'N'),
                             ({sentinel.volant1: Mock(x=1, y=0, set_position=lambda s, *args: sentinel.new_volant1), sentinel.volant2: Mock(x=0, y=0)}, {sentinel.volant1: sentinel.new_volant1}, 'E'),
                             ({sentinel.volant1: Mock(x=1, y=-1, set_position=lambda s, *args: sentinel.new_volant1), sentinel.volant2: Mock(x=0, y=0)}, {sentinel.volant1: sentinel.new_volant1}, 'SE'),
                             ({sentinel.volant1: Mock(x=0, y=-1, set_position=lambda s, *args: sentinel.new_volant1), sentinel.volant2: Mock(x=0, y=0)}, {sentinel.volant1: sentinel.new_volant1}, 'S'),
                             ({sentinel.volant1: Mock(x=-1, y=0, set_position=lambda s, *args: sentinel.new_volant1), sentinel.volant2: Mock(x=0, y=0)}, {sentinel.volant1: sentinel.new_volant1}, 'W'),
                             ({sentinel.volant1: Mock(x=-1, y=1, set_position=lambda s, *args: sentinel.new_volant1), sentinel.volant2: Mock(x=0, y=0)}, {sentinel.volant1: sentinel.new_volant1}, 'NW'),
                         ])
def test_board_sends_volants_over_boundaries(inflight, expected_sent_volants, neighbour_sent_to):
    neighbours = {
        'N': Mock(_incoming=dict()),
        'E': Mock(_incoming=dict()),
        'W': Mock(_incoming=dict()),
        'S': Mock(_incoming=dict()),
        'NW': Mock(_incoming=dict()),
        'SE': Mock(_incoming=dict()),
    }

    b = Board(sentinel.game_params, 1, 1, sentinel.hives, sentinel.flowers, sentinel.neighbours, dict(inflight))
    b._neighbours = neighbours
    sent_volants = b.send_volants()

    assert sent_volants == expected_sent_volants
    assert neighbours[neighbour_sent_to]._incoming == {sentinel.volant1: sentinel.new_volant1}
    assert all(neighbours[n]._incoming == dict() for n in neighbours if n != neighbour_sent_to)

    assert b.inflight == {sentinel.volant2: inflight[sentinel.volant2]}
