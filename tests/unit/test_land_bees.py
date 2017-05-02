from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from hiveminder.bee import Bee, QueenBee
from hiveminder.seed import Seed
from hiveminder.hive import Hive
from mock import sentinel


def check_bee_nectar_eq_hive_nectar(landed_bees, game):
    """ Check the sum of all the nectar in the hives equals the sum of the nectar
        carried by bees that have landed
        returns: True if they are same
    """
    hive_nectar = sum(sum(hive.nectar for hive in board.hives) for board in game.boards)
    landed_bee_nectar = sum((sum(bee.nectar for bee in board_bees.values()) for board_bees in landed_bees))
    return hive_nectar == landed_bee_nectar


def test_land_bees_do_not_land_bee_not_on_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 4, 0, 10, DEFAULT_GAME_PARAMETERS,  1)
    landed_bees = game.land_bees()

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)
    assert sentinel.bee_1 in game.boards[0].inflight
    assert landed_bees == [{}]
    assert game.boards[0].inflight == {sentinel.bee_1: Bee(5, 4, 0, 10, DEFAULT_GAME_PARAMETERS,  1)}
    assert check_bee_nectar_eq_hive_nectar(landed_bees, game)


def test_land_bees_single_bee_single_board_single_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight

    assert [board.calculate_score() for board in game.boards] == [DEFAULT_GAME_PARAMETERS.hive_score_factor +
                                                                  DEFAULT_GAME_PARAMETERS.nectar_score_factor]
    assert landed_bees == [{sentinel.bee_1: Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)}]
    assert game.boards[0].inflight == {}
    assert check_bee_nectar_eq_hive_nectar(landed_bees, game)


def test_land_bees_two_bees_single_board_single_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    game.boards[0].inflight[sentinel.bee_2] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 2)
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight
        assert sentinel.bee_2 not in board.inflight

    assert [board.calculate_score() for board in game.boards] == [DEFAULT_GAME_PARAMETERS.hive_score_factor +
                                                                  3 * DEFAULT_GAME_PARAMETERS.nectar_score_factor]
    assert landed_bees == [{sentinel.bee_1: Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1),
                            sentinel.bee_2: Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 2)}]
    assert check_bee_nectar_eq_hive_nectar(landed_bees, game)


def test_land_bees_two_bees_single_board_two_hives():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5), Hive(4, 2),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor * 2 for board in game.boards)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    game.boards[0].inflight[sentinel.bee_2] = Bee(4, 2, 0, 10, DEFAULT_GAME_PARAMETERS, 2)
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight
        assert sentinel.bee_2 not in board.inflight

    assert [board.calculate_score() for board in game.boards] == [DEFAULT_GAME_PARAMETERS.hive_score_factor * 2 +
                                                                  DEFAULT_GAME_PARAMETERS.nectar_score_factor * 3]
    assert landed_bees == [{sentinel.bee_1: Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1),
                            sentinel.bee_2: Bee(4, 2, 0, 10, DEFAULT_GAME_PARAMETERS, 2)}]
    assert check_bee_nectar_eq_hive_nectar(landed_bees, game)


def test_land_bees_single_bee_two_boards_single_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=2,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),), (Hive(7, 7),),),
                     flowers=((), (),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == len(board.hives) * DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.bee_1] = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight

    assert [board.calculate_score() - DEFAULT_GAME_PARAMETERS.hive_score_factor
                                        for board in game.boards] == [DEFAULT_GAME_PARAMETERS.nectar_score_factor, 0]
    assert landed_bees == [{sentinel.bee_1: Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)}, {}]
    assert check_bee_nectar_eq_hive_nectar(landed_bees, game)


def test_seeds_do_not_land_in_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.seed_1] = Seed(5, 5, 0)
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight

    assert [board.calculate_score() for board in game.boards] == [DEFAULT_GAME_PARAMETERS.hive_score_factor]
    assert landed_bees == [{}]
    assert game.boards[0].inflight == {sentinel.seed_1: Seed(5, 5, 0)}
    assert check_bee_nectar_eq_hive_nectar(landed_bees, game)


def test_land_queenbees_single_queenbee_single_board_single_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)

    game.boards[0].inflight[sentinel.bee_1] = QueenBee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight

    assert [board.calculate_score() for board in game.boards] == [DEFAULT_GAME_PARAMETERS.hive_score_factor +
                                                                  DEFAULT_GAME_PARAMETERS.dead_bee_score_factor]
    assert landed_bees == [{sentinel.bee_1: QueenBee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)}]
    assert game.boards[0].inflight == {}


def test_land_bees_single_queenbee_single_regular_bee_single_board_single_hive():
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=1,
                     board_width=10,
                     board_height=10,
                     hives=((Hive(5, 5),),),
                     flowers=((),),
                     game_length=sentinel.game_length)

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor for board in game.boards)
    queen_bee = QueenBee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    bee = Bee(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS, 1)
    both_bees = {sentinel.bee_1: queen_bee, sentinel.bee_2: bee}
    game.boards[0].inflight = both_bees.copy()
    landed_bees = game.land_bees()

    for board in game.boards:
        assert sentinel.bee_1 not in board.inflight
        assert sentinel.bee_2 not in board.inflight

    assert [board.calculate_score() for board in game.boards] == [DEFAULT_GAME_PARAMETERS.hive_score_factor +
                                                                  DEFAULT_GAME_PARAMETERS.dead_bee_score_factor +
                                                                  bee.nectar * DEFAULT_GAME_PARAMETERS.nectar_score_factor]
    assert landed_bees == [both_bees]
    assert game.boards[0].inflight == {}
    assert check_bee_nectar_eq_hive_nectar([{sentinel.bee_2: bee}], game)
