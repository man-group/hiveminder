from __future__ import absolute_import, print_function
from collections import namedtuple
import platform
import re
from datetime import datetime, timedelta
ALLOWED_ALGO_NAME = re.compile("^[a-zA-Z0-9 _-]+$")


AlgoMetaData = namedtuple("AlgoMetaData", "description,fn,on_game_over,on_start_game")
_algos = {}


TIME_LIMIT = timedelta(microseconds=200000)


def _time_limit(fn, name):
    def __time_limit(*args, **kwargs):
        then = datetime.now()
        result = fn(*args, **kwargs)
        if ((datetime.now() - then) > TIME_LIMIT):
            print("Timeout calling algo {}".format(name))
            return None
        else:
            return result
    return __time_limit


def _filename(fn):
    if platform.python_version_tuple()[0] == '2':
        return fn.func_code.co_filename
    else:
        return fn.__code__.co_filename


def algo_player(name, description):
    def _on_game_over(fn):
        _algos[name] = AlgoMetaData(description=_algos[name].description,
                                    fn=_algos[name].fn,
                                    on_game_over=fn,
                                    on_start_game=_algos[name].on_start_game)
        return fn

    def _on_start_game(fn):
        _algos[name] = AlgoMetaData(description=_algos[name].description,
                                    fn=_algos[name].fn,
                                    on_game_over=_algos[name].on_game_over,
                                    on_start_game=fn)
        return fn

    def _algo(fn):
        if name in _algos:
            raise ValueError("Algo '{}' is already defined.".format(name))
        elif not ALLOWED_ALGO_NAME.match(name):
            raise ValueError("Algos can only have names containing letters,"
                             " numbers, space, underscore and hyphen.")
        elif _filename(fn) in {_filename(i.fn) for i in _algos.values()}:
            raise ValueError("You must put each algo in its own file.")
        else:
            _algos[name] = AlgoMetaData(description=description,
                                        fn=_time_limit(fn, name),
                                        on_game_over=None,
                                        on_start_game=None)
            fn.on_game_over = _on_game_over
            fn.on_start_game = _on_start_game
            return fn

    return _algo
