from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.hive import Hive
from mock import sentinel, patch
from random import Random
from hiveminder.headings import LEGAL_HEADINGS
from hiveminder.game_params import GameParameters
from hiveminder.bee import QueenBee, Bee


def test_launch_bees_single_board_single_hive_probability_one():
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
                            flower_lifespan_visit_impact=10,
                            trap_seed_probability=1,
                            venus_score_factor=-50,
                            trap_seed_lifespan=10
                            )

    game = GameState(game_params=params,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=(sentinel.flowers,),
                     game_length=sentinel.game_length)
    
    assert len(game.boards[0].inflight) == 0
    with patch("hiveminder.game_state.rngs", {sentinel.game_id: Random(0)}):
        game.launch_bees(sentinel.turn_num)
 
    assert len(game.boards[0].inflight) == 1
    
    bee = list(game.boards[0].inflight.values())[0]
    assert bee.x == 5
    assert bee.y == 5
    assert bee.heading in LEGAL_HEADINGS
    assert bee.energy == params.initial_energy


def test_launch_bees_single_board_single_hive_probability_zero():
    params = GameParameters(launch_probability=0.0,
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
                            flower_lifespan_visit_impact=10,
                            trap_seed_probability=1,
                            venus_score_factor=-50,
                            trap_seed_lifespan=10
                            )
    game = GameState(game_params=params,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=(sentinel.flowers,),
                     game_length=sentinel.game_length)
    
    assert len(game.boards[0].inflight) == 0
    with patch("hiveminder.game_state.rngs", {sentinel.game_id: Random(0)}):
        game.launch_bees(sentinel.turn_num)
 
    assert len(game.boards[0].inflight) == 0


def test_launch_bees_enough_nectar_get_queen_then_normal_bee():
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
                            flower_lifespan_visit_impact=10,
                            trap_seed_probability=1,
                            venus_score_factor=-50,
                            trap_seed_lifespan=10)
    game = GameState(game_params=params,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5, params.queen_bee_nectar_threshold),),),
                     flowers=(sentinel.flowers,),
                     game_length=sentinel.game_length)

    def launch_a_bee():
        with patch("hiveminder.game_state.rngs", {sentinel.game_id: Random(0)}):
            game.launch_bees(sentinel.turn_num)

    seen_bees = set()

    assert len(game.boards[0].inflight) == 0
    # first should be a queen
    launch_a_bee()
    assert len(game.boards[0].inflight) == 1
    bee_id = list(game.boards[0].inflight)[0]
    seen_bees.add(bee_id)
    queen_bee = game.boards[0].inflight[bee_id]
    assert (queen_bee.x, queen_bee.y, queen_bee.energy, queen_bee.nectar) == (5, 5, params.initial_energy, 0)
    assert queen_bee.heading in LEGAL_HEADINGS
    assert type(queen_bee) == QueenBee
    assert game.boards[0].hives[0].nectar == 0

    # then a normal bee
    launch_a_bee()
    assert len(game.boards[0].inflight) == 2
    bee_id = (set(game.boards[0].inflight.keys()) - seen_bees).pop()
    seen_bees.add(bee_id)
    bee = game.boards[0].inflight[bee_id]
    assert (bee.x, bee.y, bee.energy, bee.nectar) == (5, 5, params.initial_energy, 0)
    assert bee.heading in LEGAL_HEADINGS
    assert type(bee) == Bee
    assert game.boards[0].hives[0].nectar == 0

    # hive goes back to params.queen_bee_nectar_threshold, get another queen
    game.boards[0].hives[0].nectar = params.queen_bee_nectar_threshold
    launch_a_bee()
    bee_id = (set(game.boards[0].inflight.keys()) - seen_bees).pop()
    seen_bees.add(bee_id)
    new_queen = game.boards[0].inflight[bee_id]
    assert type(new_queen) == QueenBee
    assert game.boards[0].hives[0].nectar == 0
