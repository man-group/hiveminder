from hiveminder import algo_player
from hiveminder.headings import LEGAL_NEW_HEADINGS
import random

from hiveminder.utils import apply_command_and_advance


@algo_player(name="Random Algo",
             description="Example of an algo that randomly directs bees")
def random_algo(board_width, board_height, hives, flowers, inflight, crashed,
                 lost_volants, received_volants, landed, scores, player_id, game_id, turn_num):
    if inflight:
        thing_id = random.choice(list(inflight.keys()))
        thing = inflight[thing_id]
        new_heading = random.choice(list(LEGAL_NEW_HEADINGS[thing[3]]))
        new_command = dict(entity=thing_id, command=new_heading)
        # you might want to see what happens with the new command and then make decisions
        new_result = apply_command_and_advance(board_width, board_height, hives, flowers,
                                               inflight, turn_num, new_command)
        return new_command


@random_algo.on_start_game
def start_game(board_width, board_height, hives, flowers, players, player_id, game_id, game_params):
    pass


@random_algo.on_game_over
def game_over(board_width, board_height, hives, flowers, inflight, crashed,
              lost_volants, received_volants, landed, scores, player_id, game_id, turns):
    pass
