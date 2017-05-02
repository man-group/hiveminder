from __future__ import absolute_import
from hiveminder import game
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from time import sleep, time
from hiveminder.algos import AlgoMetaData
import sys
import pytest


def dummy_algo(*args, **kwargs):
    return None


def sleepy_algo(*args, **kwargs):
    sleep(1)
    return None


@pytest.mark.skipif(sys.version_info < (3,2),
                    reason="requires python3.2")
def test_algos_can_be_run_in_parallel():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as pool:
        start_time = time()
        game(board_width=8,
             board_height=8,
             num_hives=1,
             num_flowers=1,
             algos={"algo{}".format(i) : AlgoMetaData("Sleepy Algo", sleepy_algo, None, None) for i in range(10)},
             game_length=1,
             game_params=DEFAULT_GAME_PARAMETERS,
             pool=pool)
        assert time() - start_time < 2


@pytest.mark.skipif(sys.version_info < (3,2),
                    reason="requires python3.2")
def test_algos_can_be_ended_in_parallel():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as pool:
        start_time = time()
        game(board_width=8,
             board_height=8,
             num_hives=1,
             num_flowers=1,
             algos={"algo{}".format(i) : AlgoMetaData("Sleepy Algo", dummy_algo, sleepy_algo, None) for i in range(10)},
             game_length=1,
             game_params=DEFAULT_GAME_PARAMETERS,
             pool=pool)
        assert time() - start_time < 2


@pytest.mark.skipif(sys.version_info < (3,2),
                    reason="requires python3.2")
def test_algos_can_be_started_in_parallel():
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as pool:
        start_time = time()
        game(board_width=8,
             board_height=8,
             num_hives=1,
             num_flowers=1,
             algos={"algo{}".format(i) : AlgoMetaData("Sleepy Algo", dummy_algo, None, sleepy_algo) for i in range(10)},
             game_length=1,
             game_params=DEFAULT_GAME_PARAMETERS,
             pool=pool)
        assert time() - start_time < 2
