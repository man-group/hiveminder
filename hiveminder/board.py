from __future__ import absolute_import
import collections
from uuid import uuid4
from copy import  copy
from random import choice
from .bee import Bee, QueenBee
from .seed import Seed
from .hive import Hive
from .headings import LEGAL_NEW_HEADINGS
from .flower import Flower
from .game_params import GameParameters


def _del_at_coordinate(items, x, y):
    return tuple(item for item in items if (item.x, item.y) != (x, y))


def volant_from_json(json):
    return {'Seed': Seed, 'Bee': Bee, 'QueenBee': QueenBee}[json[0]].from_json(json)


class Board(object):
    def __init__(self,
                 game_params,
                 board_width,
                 board_height,
                 hives,
                 flowers,
                 neighbours,
                 inflight=None,
                 dead_bees=0):
        self.game_params = game_params
        self.board_width = board_width
        self.board_height = board_height
        self.hives = hives
        self.flowers = flowers
        self.neighbours = neighbours
        self.inflight = inflight or {}
        self.dead_bees = dead_bees
        self._incoming = {}

    def calculate_score(self):
        return (self.dead_bees * self.game_params.dead_bee_score_factor +
                # All boards start with 1 hive & 1 flower; board score starts at self.game_params.hive_score_factor + self.game_params.flower_score_factor
                len(self.hives) * self.game_params.hive_score_factor + len(self.flowers) * self.game_params.flower_score_factor +
                sum(hive.nectar for hive in self.hives) * self.game_params.nectar_score_factor)

    def launch_bees(self, rng, turn_num):
        if self.hives and (rng.random() < self.game_params.launch_probability or turn_num == 0):
            hive = rng.choice(self.hives)
            heading = rng.choice(list(LEGAL_NEW_HEADINGS))
            if hive.nectar >= self.game_params.queen_bee_nectar_threshold:
                self.inflight[str(uuid4())] = QueenBee(hive.x, hive.y, heading,
                                                       self.game_params.initial_energy, self.game_params)
                hive.nectar -= self.game_params.queen_bee_nectar_threshold
            else:
                self.inflight[str(uuid4())] = Bee(hive.x, hive.y, heading,
                                                  self.game_params.initial_energy, self.game_params)

    def summary(self):
        return collections.OrderedDict([('Dead Bees', self.dead_bees),
                ('Dead bee score', self.dead_bees * self.game_params.dead_bee_score_factor),
                ('Number of hives', len(self.hives)),
                ('Hive score', len(self.hives) * self.game_params.hive_score_factor),
                ('Number of flowers', len(self.flowers)),
                ('Flower score', len(self.flowers) * self.game_params.flower_score_factor),
                ('Nectar collected', sum(hive.nectar for hive in self.hives)),
                ('Nectar score', sum(hive.nectar for hive in self.hives) * self.game_params.nectar_score_factor),
                ('Total Score', self.calculate_score())])

    def detect_crashes(self):
        bee_occupied = {}
        seed_occupied = {}
        opposing_states = set()  # Used to look for head on collisions
        for volant_id, volant in self.inflight.items():
            if isinstance(volant, Bee):
                bee_occupied.setdefault((volant.x, volant.y), set()).add(volant_id)
                opposing_states.add(copy(volant).advance(reverse=True).xyh)
            elif isinstance(volant, Seed):
                seed_occupied.setdefault((volant.x, volant.y), set()).add(volant_id)

        collided = {bee for _, bees in bee_occupied.items() for bee in bees if len(bees) > 1}
        exhaused = {bee_id for bee_id, bee in self.inflight.items()
                    if isinstance(bee, Bee) and bee.energy < 0} - collided
        headon = {bee_id for bee_id, bee in self.inflight.items()
                  if isinstance(bee, Bee) and bee.xyh in opposing_states} - exhaused - collided
        self.dead_bees += len(collided) + len(exhaused) + len(headon)

        seeds_collided = {seed for _, seeds in seed_occupied.items() for seed in seeds if len(seeds) > 1}

        return dict(collided={bee_id: self.inflight.pop(bee_id) for bee_id in collided},
                    exhausted={bee_id: self.inflight.pop(bee_id) for bee_id in exhaused},
                    headon={bee_id: self.inflight.pop(bee_id) for bee_id in headon},
                    seeds={seed_id: self.inflight.pop(seed_id) for seed_id in seeds_collided},)

    def land_bees(self):
        hives = {(hive.x, hive.y): hive for hive in self.hives}

        landed = {bee_id: hives[bee.x, bee.y] for bee_id, bee in self.inflight.items()
                  if isinstance(bee, Bee) and (bee.x, bee.y) in hives}

        for bee_id, hive in landed.items():
            inflight_volant = self.inflight[bee_id]
            if isinstance(inflight_volant, QueenBee):
                self.dead_bees += 1
            else:
                hive.nectar += self.inflight[bee_id].nectar

        return {bee_id: self.inflight.pop(bee_id) for bee_id in landed}

    def visit_flowers(self, rng):
        flowers = {(flower.x, flower.y): flower for flower in self.flowers}

        vists = {bee_id: flowers[bee.x, bee.y] for bee_id, bee in self.inflight.items()
                 if isinstance(bee, Bee) and (bee.x, bee.y) in flowers}

        for bee_id, flower in vists.items():
            self.inflight[bee_id] = self.inflight[bee_id].drink(flower.potency)
            launch_seed = flower.visit()
            if launch_seed:
                heading = rng.choice(list(LEGAL_NEW_HEADINGS))
                self.inflight[str(uuid4())] = Seed(flower.x, flower.y, heading)

    def move_volants(self):
        for volant_id, volant in self.inflight.items():
            self.inflight[volant_id] = volant.advance()

    def send_volants(self):

        sent = dict()

        for volant_id, volant in self.inflight.items():
            new_x = (self.board_width + volant.x) % self.board_width
            new_y = (self.board_height + volant.y) % self.board_height

            reciever = None
            if volant.x < 0:
                if volant.y >= self.board_height:
                    reciever = "NW"
                else:
                    reciever = "W"
            elif volant.x >= self.board_width:
                if volant.y < 0:
                    reciever = "SE"
                else:
                    reciever = "E"
            elif volant.y < 0:
                    reciever = "S"
            elif volant.y >= self.board_height:
                reciever = "N"

            if reciever:
                sent[volant_id] = (reciever, volant.set_position(new_x, new_y))

        for volant_id, routing in sent.items():
            del self.inflight[volant_id]
            receiver, routed_volant = routing
            self._neighbours[receiver]._incoming[volant_id] = routed_volant

        return {volant_id: volant for (volant_id, (_, volant)) in sent.items()}

    def apply_command(self, cmd, turn_num):
        if cmd is not None:
            cmd_volant_id, cmd_heading = cmd['entity'], cmd['command']

            if cmd_volant_id not in self.inflight:
                raise RuntimeError("Unknown entity.")

            cmd_volant = self.inflight[cmd_volant_id]

            if isinstance(cmd_volant, Seed) and cmd_heading == "flower":
                # If there is already a hive or a flower on this tile remove it
                self.hives = _del_at_coordinate(self.hives, cmd_volant.x, cmd_volant.y)
                self.flowers = _del_at_coordinate(self.flowers, cmd_volant.x, cmd_volant.y)

                # Add new flower
                self.flowers += (Flower(cmd_volant.x, cmd_volant.y, self.game_params,
                                        expires=turn_num + self.game_params.flower_lifespan),)
                del self.inflight[cmd_volant_id]
            elif isinstance(cmd_volant, QueenBee) and 'create_hive' == cmd_heading:
                try:
                    # If there is a flower on this tile remove it
                    self.flowers = _del_at_coordinate(self.flowers, cmd_volant.x, cmd_volant.y)
                    cmd_volant.create_hive(self)
                    del self.inflight[cmd_volant_id]
                except Exception as e:
                    raise RuntimeError("Can not create hive for this bee {} {}".format(cmd_volant, e))
            elif cmd_heading not in LEGAL_NEW_HEADINGS[cmd_volant.heading]:
                raise RuntimeError("Can not rotate to heading '{}' from heading '{}'.".format(cmd_heading,
                                                                                              cmd_volant.heading))
            else:
                cmd_volant.heading = cmd_heading

    def remove_dead_flowers(self, turn_num):
        for flower in self.flowers:
            if flower.expires is None:
                raise RuntimeError("Flower expiry is None")

        unexpired_flowers = tuple(flower for flower in self.flowers if flower.expires > turn_num)

        # If there are no flowers left on the board we need to keep at least one!
        if unexpired_flowers:
            self.flowers = unexpired_flowers
        elif self.flowers:
            self.flowers = (choice(self.flowers),)

    def to_json(self):
        return {"boardWidth": self.board_width,
                "boardHeight": self.board_height,
                "hives": [hive.to_json() for hive in self.hives],
                "flowers": [flower.to_json() for flower in self.flowers],
                "inflight": {volant_id: volant.to_json() for volant_id, volant in self.inflight.items()},
                "deadbees": self.dead_bees,
                "score": self.calculate_score(),
                "neighbours": self.neighbours,
                "gameParams": self.game_params._asdict()}

    @classmethod
    def from_json(cls, json):
        return cls(game_params=GameParameters(**json["gameParams"]),
                   board_width=json["boardWidth"],
                   board_height=json["boardHeight"],
                   hives=tuple(Hive(*hive) for hive in json["hives"]),
                   flowers=tuple(Flower.from_json(flower) for flower in json["flowers"]),
                   inflight={volant_id: volant_from_json(volant) for volant_id, volant in json["inflight"].items()},
                   dead_bees=json["deadbees"],
                   neighbours=json["neighbours"])

    def _connect_to_neighbours(self, boards):
        self._neighbours = {direction: boards[self.neighbours[direction]]
                            for direction in ("N", "S", "E", "W", "NW", "SE")}

    def receive_volants(self):
        self.inflight.update(self._incoming)
        received_volants = self._incoming
        self._incoming = {}
        return received_volants

    __hash__ = None

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            def filter_dict(d):
                """
                Filter out attributes starting with '_', in particular _neighbours as it
                creates circular references and isn't fundamental to a board's state
                """
                return {k: v for k, v in d.items() if not k.startswith('_')}
            return filter_dict(self.__dict__) == filter_dict(other.__dict__)
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented
