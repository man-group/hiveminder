from __future__ import absolute_import
from .app import app, json, request
from .game import initialise_game
from .game_state import GameState
from .game_params import DEFAULT_GAME_PARAMETERS
from traceback import format_exc


@app.route('/newgame', methods=['POST'])
def newgame():
    try:
        data = request.json
        boards = data["boards"]
        board_width = data["boardWidth"]
        board_height = data["boardHeight"]
        num_hives = data["hives"]
        num_flowers = data["flowers"]
        game_length = data["moves"]
        
        game_state = initialise_game(DEFAULT_GAME_PARAMETERS,
                                     boards,
                                     board_width,
                                     board_height,
                                     num_hives,
                                     num_flowers,
                                     game_length)
        
        return json.dumps({"ok" : {"state": game_state.to_json(),
                                   "crashed": [dict(collided={}, exhausted={}, headon={}, seeds={})] * boards,
                                   "lost": [{}] * boards,
                                   "received": [{}] * boards,
                                   "landed": [{}] * boards
                                   }})
    except:
        return json.dumps({"error" : format_exc()})


@app.route('/turn', methods=['POST'])
def take_turn():
    try:
        game_state, crashed, landed, lost_volants, received_volants = GameState.from_json(request.json).turn(request.json["commands"])
        return json.dumps({"ok" : {"state": game_state.to_json(),
                                   "crashed": [{classification: {crashed_id: crashed_item.to_json()
                                                                 for crashed_id, crashed_item in crashes.items()}
                                                for classification, crashes in classified_crashed.items()}
                                               for classified_crashed in crashed],
                                   "received": [{volant_id: volant.to_json() for volant_id, volant in received.items()} for received in received_volants],
                                   "lost": [{volant_id: volant.to_json() for volant_id, volant in lost.items()} for lost in lost_volants],
                                   "landed": [{bee_id: bee.to_json() for bee_id, bee in landed_bees.items()}
                                              for landed_bees in landed],
                                   }})
    except:
        return json.dumps({"error" : format_exc()})
