"""Run `python simulate.py` from a bash terminal to simulate a shortened run of the game
that uses every algo stored in the algo folder. 
The competition will involve 10 runs of the game, each with 10,000 moves."""

from hiveminder import game
from algos import *
from hiveminder.algos import _algos
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS, BEE_TRAP_GAME_PARAMETERS
from sys import argv


def run_game(no_of_turns, bee_traps=False):
    if bee_traps:
        game_params = BEE_TRAP_GAME_PARAMETERS
    else:
        game_params = DEFAULT_GAME_PARAMETERS
        
    game(board_width=8,
         board_height=8,
         num_hives=1,
         num_flowers=1,
         algos=_algos,
         game_length=no_of_turns,
         game_params=game_params)


if __name__ == "__main__":
    run_game(no_of_turns=int(argv[1]) if len(argv)>=2 else 1000)
