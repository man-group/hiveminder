from __future__ import absolute_import, print_function, division
from uuid import uuid4
from random import Random
from itertools import product
from .hive import Hive
from .flower import Flower
from .game_state import rngs, GameState
from hiveminder._util import even_q_in_range as in_range


def make_hives(n, board_width, board_height, rng):
    all_possible_sites = list(product(range(1, board_width - 1), range(1, board_height - 1)))
    return tuple(Hive(*site) for site in rng.sample(all_possible_sites, n))


def make_flowers(n, hives, board_width, board_height, rng, game_params):
    all_tiles = set(product(range(1, board_width - 1), range(1, board_height - 1)))

    reachable_tiles = set()
    occupied_tiles = set()
    radius = min(game_params.initial_energy // 2, max(board_width, board_height))
    for hive in hives:
        occupied_tiles = occupied_tiles | set(in_range(hive.x, hive.y, 1))
        reachable_tiles = reachable_tiles | set(in_range(hive.x, hive.y, radius))

    all_possible_sites = all_tiles & (reachable_tiles - occupied_tiles)

    return tuple(Flower(*site, game_params=game_params, expires=game_params.flower_lifespan)
                 for site in rng.sample(all_possible_sites, n))


def initialise_game(game_params, boards, board_width, board_height, num_hives, num_flowers, game_length, seed=None):
    game_id = str(uuid4())
    rng = Random(seed)
    rngs[game_id] = rng

    hives = [make_hives(num_hives,
                        board_width,
                        board_height,
                        rng) for _ in range(boards)]

    flowers = [make_flowers(num_flowers,
                            board_hives,
                            board_width,
                            board_height,
                            rng, game_params) for board_hives in hives]

    return GameState(game_params=game_params,
                     game_id=game_id,
                     boards=boards,
                     board_width=board_width,
                     board_height=board_height,
                     hives=hives,
                     flowers=flowers,
                     game_length=game_length)

    
def game(board_width, board_height, num_hives, num_flowers, game_length, algos, game_params):
    algo_names = list(algos.keys())
    algos = list(algos.values())

    game_state = initialise_game(game_params,
                                 len(algos),
                                 board_width=board_width,
                                 board_height=board_height,
                                 num_hives=num_hives,
                                 num_flowers=num_flowers,
                                 game_length=game_length)
    
    for i, algo, board in zip(range(len(algos)), algos, game_state.boards):
        if algo.on_start_game is not None:
            board_json = board.to_json()
            algo.on_start_game(board_json['boardWidth'],
                               board_json['boardHeight'],
                               board_json['hives'],
                               board_json['flowers'],
                               len(algos),
                               i,
                               game_state.game_id,
                               game_params)

    crashed = [dict(headon={}, collided={}, exhausted={})] * len(algos)
    landed_bees = [{}] * len(algos)
    lost_volants = [{}] * len(algos)
    received_volants = [{}] * len(algos)

    while not game_state.game_over():
        assert len(algos) == len(game_state.boards)
        assert len(algos) == len(crashed)

        gamestate_json = game_state.to_json()
        scores = [board['score'] for board in gamestate_json['boards']]

        print(dict(zip(algo_names, scores)))

        commands = [algo.fn(gamestate_json['boards'][i]['boardWidth'],
                            gamestate_json['boards'][i]['boardHeight'],
                            gamestate_json['boards'][i]['hives'],
                            gamestate_json['boards'][i]['flowers'],
                            gamestate_json['boards'][i]['inflight'],
                            {classification: {crashed_id: crashed_item.to_json()
                                              for crashed_id, crashed_item in crashes.items()}
                             for classification, crashes in crashed[i].items()},
                            {volant_id: volant.to_json() for volant_id, volant in lost_volants[i].items()},
                            {volant_id: volant.to_json() for volant_id, volant in received_volants[i].items()},
                            {bee_id: bee.to_json() for bee_id, bee in landed_bees[i].items()},
                            scores,
                            i,
                            gamestate_json['gameId'],
                            game_state.turn_num) for i, algo in enumerate(algos)]

        game_state, crashed, landed_bees, lost_volants, received_volants = game_state.turn(commands)

    scores = [board['score'] for board in gamestate_json['boards']]
    print_game_result(game_state, algo_names)

    for i, algo, board in zip(range(len(algos)), algos, game_state.boards):
        if algo.on_game_over is not None:
            board_json = board.to_json()
            algo.on_game_over(board_json['boardWidth'],
                              board_json['boardHeight'],
                              board_json['hives'],
                              board_json['flowers'],
                              board_json['inflight'],
                              {classification: {crashed_id: crashed_item.to_json()
                                                for crashed_id, crashed_item in crashes.items()}
                              for classification, crashes in crashed[i].items()},
                               {volant_id: volant.to_json() for volant_id, volant in lost_volants[i].items()},
                               {volant_id: volant.to_json() for volant_id, volant in received_volants[i].items()},
                               {bee_id: bee.to_json() for bee_id, bee in landed_bees[i].items()},
                              scores,
                              i,
                              game_state.game_id,
                              game_state.turn_num)
    return game_state

    
def print_game_result(game_state, algo_names):
    winners = calculate_winner(game_state)
    if len(winners) == 1:
        print_single_winner(game_state, winners[0], algo_names)
    else:
        print_multiple_winners(game_state, winners, algo_names)


def calculate_winner(game_state):
    scores = [board.calculate_score() for board in game_state.boards]
    max_score = max(scores)
    return [i for i, score in enumerate(scores) if score == max_score]


def print_single_winner(game_state, winner, algo_names):
    winner_name = algo_names[winner]
    print('Congratulations to {}! You have won!'.format(winner_name))
    print_scores(game_state, algo_names)
    print_stats_table(game_state, algo_names)


def print_multiple_winners(game_state, winners, algo_names):
    print('We have a tie between {}!'.format(' and '.join([algo_names[i] for i in winners])))
    print_scores(game_state, algo_names)
    print_stats_table(game_state, algo_names)


def print_scores(game_state, algo_names):
    print('Final scores were:')
    for i, player in enumerate(algo_names):
        print('\t{}:\t{}'.format(player.ljust(20, ' '), game_state.boards[i].calculate_score()))


def print_stats_table(gamestate_json, algo_names):
    print ('Breakdown of scores as follows:\n')
    summary_tables = {algo_name: gamestate_json.boards[i].summary()
                      for i, algo_name in enumerate(algo_names)}
    keys = list(summary_tables.values())[0].keys()
    max_key_length = max(len(k) for k in keys)
    col_width = 15
    print('Algo Name'.ljust(max_key_length + 5, ' ') + '| ' +
          ' |'.join([algo_name.rjust(col_width, ' ')
                     for algo_name in summary_tables.keys()]))
    print('-' * (max_key_length + 7 + (col_width + 2) * len(algo_names)))
    for key in keys:
        print(key.ljust(max_key_length + 5) + '| ' +
              ' |'.join([str(table[key]).rjust(col_width, ' ')
                         for table in summary_tables.values()]))
