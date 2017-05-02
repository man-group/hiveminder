from __future__ import absolute_import
from hiveminder.game import GameState, make_flowers
from hiveminder.bee import Bee
from hiveminder.seed import Seed
from hiveminder.flower import Flower
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel, patch, Mock, ANY
import pytest


@patch.dict("hiveminder.game_state.rngs", {sentinel.game_id: sentinel.rng})
def test_visit_flowers_does_not_feed_bee_if_not_on_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((Flower(5, 5, DEFAULT_GAME_PARAMETERS, 1, expires=DEFAULT_GAME_PARAMETERS.flower_lifespan),),),
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 4, 0, 10, DEFAULT_GAME_PARAMETERS,  1)
    game.visit_flowers()

    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 4, 0, 10, DEFAULT_GAME_PARAMETERS,  1)}


def test_visit_flowers_single_bee_single_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((Flower(5, 5, DEFAULT_GAME_PARAMETERS, 1, expires=DEFAULT_GAME_PARAMETERS.flower_lifespan),),),
                     game_length=sentinel.game_length)
    
    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS,  1)
    game.visit_flowers()

    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 5, 0, 10 + DEFAULT_GAME_PARAMETERS.bee_energy_boost_per_nectar, DEFAULT_GAME_PARAMETERS,  2)}


def test_visit_flowers_two_bees_two_flowers():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((Flower(5, 5, DEFAULT_GAME_PARAMETERS, 1, expires=DEFAULT_GAME_PARAMETERS.flower_lifespan),
                               Flower(5, 4, DEFAULT_GAME_PARAMETERS, 1, expires=DEFAULT_GAME_PARAMETERS.flower_lifespan)),),
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS,  0)
    game.boards[0].inflight[sentinel.bee_2] = Bee(5, 4, 0, 10, DEFAULT_GAME_PARAMETERS,  0)
    game.visit_flowers()

    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 5, 0, 10 + DEFAULT_GAME_PARAMETERS.bee_energy_boost_per_nectar, DEFAULT_GAME_PARAMETERS,  1),
                                       sentinel.bee_2: Bee(5, 4, 0, 10 + DEFAULT_GAME_PARAMETERS.bee_energy_boost_per_nectar, DEFAULT_GAME_PARAMETERS,  1), }


def test_visit_flowers_two_bees_two_flowers_more_potent_and_live_longer():
    flower1 = Flower(5, 5, DEFAULT_GAME_PARAMETERS, 3, expires=DEFAULT_GAME_PARAMETERS.flower_lifespan)
    flower2 = Flower(5, 4, DEFAULT_GAME_PARAMETERS, 2, expires=DEFAULT_GAME_PARAMETERS.flower_lifespan)

    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((flower1, flower2),),
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS,  3)
    game.boards[0].inflight[sentinel.bee_2] = Bee(5, 4, 0, 10, DEFAULT_GAME_PARAMETERS,  2)
    game.visit_flowers()

    assert flower1.expires == flower2.expires == DEFAULT_GAME_PARAMETERS.flower_lifespan + DEFAULT_GAME_PARAMETERS.flower_lifespan_visit_impact

    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 5, 0, 10 + 3 * DEFAULT_GAME_PARAMETERS.bee_energy_boost_per_nectar, DEFAULT_GAME_PARAMETERS,  5),
                                       sentinel.bee_2: Bee(5, 4, 0, 10 + 2 * DEFAULT_GAME_PARAMETERS.bee_energy_boost_per_nectar, DEFAULT_GAME_PARAMETERS,  4), }


@patch.dict("hiveminder.game_state.rngs", {sentinel.game_id: sentinel.rng})
def test_seed_does_not_visit_flower():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((Flower(5, 5, DEFAULT_GAME_PARAMETERS, 1, DEFAULT_GAME_PARAMETERS.flower_lifespan_visit_impact),),),
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.seed_1] = Seed(5, 5, 0)
    game.visit_flowers()

    assert game.boards[0].inflight == {sentinel.seed_1: Seed(5, 5, 0)}

SEED_GENERATION_VISITS = [DEFAULT_GAME_PARAMETERS.flower_seed_visit_initial_threshold +
                           (DEFAULT_GAME_PARAMETERS.flower_seed_visit_subsequent_threshold * x) for x in range(0, 8)]

@patch.dict("hiveminder.game_state.rngs", {sentinel.game_id: Mock(name="rng", **{"random.return_value": 1})})
@patch("hiveminder.board.uuid4", return_value=sentinel.uuid)
@pytest.mark.parametrize('visits', SEED_GENERATION_VISITS)
def test_visiting_flower_creates_seed_every_ten_visits(_, visits):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((Flower(5, 5, DEFAULT_GAME_PARAMETERS, 3, visits - 1, DEFAULT_GAME_PARAMETERS.flower_lifespan_visit_impact),),),
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    game.visit_flowers()

    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 5, 0, 85, DEFAULT_GAME_PARAMETERS,  3),
                                       'sentinel.uuid': Seed(5, 5, ANY)}


@pytest.mark.parametrize('visits', [n for n in range(0, 45) if n not in SEED_GENERATION_VISITS])
def test_visiting_flower_does_not_create_seeds_when_not_seed_threshold(visits):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=(sentinel.hives,),
                     flowers=((Flower(5, 5, DEFAULT_GAME_PARAMETERS, 3, visits - 1, DEFAULT_GAME_PARAMETERS.flower_lifespan_visit_impact),),),
                     game_length=sentinel.game_length)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    game.visit_flowers()

    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 5, 0, 85, DEFAULT_GAME_PARAMETERS,  3)}
