from __future__ import absolute_import
from .app import app
from ._flask import json, request
from .algos import _algos
from traceback import format_exc
from time import sleep
from datetime import datetime, timedelta
from contextlib import contextmanager


@contextmanager
def minimum_time(request):
    boards = request.json["boards"]
    if any(len([request.json["state"]["boards"][board]["inflight"]]) > 0 for board in boards):
        minimum_time = float(request.json.get("minimumTime", "0"))
        wait_until = datetime.now() + timedelta(seconds=minimum_time)
    else:
        wait_until = datetime.now()

    yield

    while wait_until > datetime.now():
        sleep(max(0, (wait_until - datetime.now()).total_seconds()))


@app.route('/algos')
def list_algos():
    try:
        return json.dumps({"ok": {algo_name: algo.description for algo_name, algo in _algos.items()}})
    except:
        return json.dumps({"error": format_exc()})


@app.route('/move', methods=['POST'])
def move():
    try:
        with minimum_time(request):
            data = request.json
            state = data["state"]
            crashed = data["crashed"]
            landed = data["landed"]
            lost = data["lost"]
            received = data["received"]
                    
            boards = data["boards"]
            algos = data["algos"]
            assert len(boards) == len(algos)
            
            results = [_algos[algo_name].fn(state["boards"][board]["boardWidth"],
                                            state["boards"][board]["boardHeight"],
                                            state["boards"][board]["hives"],
                                            state["boards"][board]["flowers"],
                                            state["boards"][board]["inflight"],
                                            crashed[board],
                                            lost[board],
                                            received[board],
                                            landed[board],
                                            [state["boards"][board]["score"]],
                                            board,
                                            state["gameId"],
                                            state["turnNum"])
                       for board, algo_name in zip(boards, algos)]
                                                          
            return json.dumps({"ok": results})
    except:
        return json.dumps({"error": format_exc()})


@app.route('/startgame', methods=['POST'])
def start_game():
    try:
        data = request.json
        state = data["state"]
        
        boards = data["boards"]
        algos = data["algos"]
        assert len(boards) == len(algos)
        
        for board, algo_name in zip(boards, algos):
            event_handler = _algos[algo_name].on_start_game
            if event_handler is not None:
                event_handler(state["boards"][board]["boardWidth"],
                              state["boards"][board]["boardHeight"],
                              state["boards"][board]["hives"],
                              state["boards"][board]["flowers"],
                              len(state["boards"]),
                              board,
                              state["gameId"],
                              state["gameParams"])
        return json.dumps({"ok": "ok"})
    except:
        return json.dumps({"error": format_exc()})


@app.route('/gameover', methods=['POST'])
def game_over():
    try:
        data = request.json
        state = data["state"]
        crashed = data["crashed"]
        landed = data["landed"]
        lost = data["lost"]
        received = data["received"]

        boards = data["boards"]
        algos = data["algos"]
        assert len(boards) == len(algos)
        
        for board, algo_name in zip(boards, algos):
            event_handler = _algos[algo_name].on_game_over
            if event_handler is not None:
                event_handler(state["boards"][board]["boardWidth"],
                              state["boards"][board]["boardHeight"],
                              state["boards"][board]["hives"],
                              state["boards"][board]["flowers"],
                              state["boards"][board]["inflight"],
                              crashed[board],
                              lost[board],
                              received[board],
                              landed[board],
                              [state["boards"][board]["score"]],
                              board,
                              state["gameId"],
                              state["turnNum"])
        return json.dumps({"ok": "ok"})
    except:
        return json.dumps({"error": format_exc()})
