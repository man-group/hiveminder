from __future__ import absolute_import

from collections import defaultdict
from random import Random

from .board import Board
from .game_params import GameParameters

# The workers in the server are stateless apart from this RandomNumGen map
# If in a running system, a request is directed at a new worker that hasn't been
# initialised with a rng for the requested game_id, it's ok to create a new one
# This dict contains game_id as keys and RandomGens as values
rngs = defaultdict(Random)


class GameState(object):
    def __init__(self,
                 game_params,
                 game_id,
                 boards,
                 board_width,
                 board_height,
                 hives,
                 flowers,
                 game_length,
                 turn_num=0):

        self.game_id = game_id
        self.game_length = game_length
        self.turn_num = turn_num

        if len(hives) != boards:
            raise ValueError("Length of hives should match the number of boards.")

        if len(flowers) != boards:
            raise ValueError("Length of flowers should match the number of boards.")

        self.boards = [Board(game_params=game_params,
                             board_width=board_width,
                             board_height=board_height,
                             hives=hives[i],
                             flowers=flowers[i],
                             neighbours={"N": (boards + i + 3) % boards,
                                         "S": (boards + i - 3) % boards,
                                         "E": (boards + i + 1) % boards,
                                         "W": (boards + i - 1) % boards,
                                         "NW": (boards + i + 2) % boards,
                                         "SE": (boards + i - 2) % boards})
                       for i in range(boards)]

        self.game_parameters = game_params

        for board in self.boards:
            board._connect_to_neighbours(self.boards)
    
    def game_over(self):
        return self.turn_num >= self.game_length
        
    def launch_bees(self, turn_num):
        rng = rngs[self.game_id]
        for board in self.boards:
            board.launch_bees(rng, turn_num)

    def detect_crashes(self):
        return [board.detect_crashes() for board in self.boards]

    def land_bees(self):
        return [board.land_bees() for board in self.boards]

    def visit_flowers(self):
        rng = rngs[self.game_id]
        for board in self.boards:
            board.visit_flowers(rng)

    def move_volants(self):
        lost_volants = [None] * len(self.boards)
        received_volants = [None] * len(self.boards)

        for board in self.boards:
            board.move_volants()

        for i, board in enumerate(self.boards):
            lost_volants[i] = board.send_volants()

        for i, board in enumerate(self.boards):
            received_volants[i] = board.receive_volants()

        return lost_volants, received_volants

    def apply_commands(self, cmds):
        if len(cmds) != len(self.boards):
            raise ValueError("You must specify a command for each board.")
        for board, cmd in zip(self.boards, cmds):
            board.apply_command(cmd, self.turn_num)

    def remove_dead_flowers(self):
        for board in self.boards:
            board.remove_dead_flowers(self.turn_num)

    def turn(self, commands):
        self.apply_commands(commands)

        self.remove_dead_flowers()

        lost_volants, received_volants = self.move_volants()

        self.visit_flowers()

        landed_bees = self.land_bees()

        crashed = self.detect_crashes()

        self.launch_bees(self.turn_num)

        self.turn_num += 1

        return self, crashed, landed_bees, lost_volants, received_volants

    def to_json(self):
        return {"gameId": self.game_id,
                "gameParams": self.game_parameters._asdict(),
                "gameLength": self.game_length,
                "turnNum": self.turn_num,
                "boards": [board.to_json() for board in self.boards]}

    @classmethod
    def from_json(cls, json):
        retval = cls(game_params=GameParameters(**json["gameParams"]),
                     game_id=json["gameId"],
                     boards=0,
                     board_width=None,
                     board_height=None,
                     hives=[],
                     flowers=[],
                     game_length=json["gameLength"],
                     turn_num=json["turnNum"]
                     )

        retval.boards = [Board.from_json(board) for board in json["boards"]]
        for board in retval.boards:
            board._connect_to_neighbours(retval.boards)

        return retval

    __hash__ = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
