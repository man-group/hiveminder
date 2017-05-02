from __future__ import absolute_import, division
from hiveminder.game_params import GameParameters
import sys


class Flower(object):
    def __init__(self, x, y, game_params, potency=1, visits=0, expires=None):
        self.x = x
        self.y = y
        self.game_params = game_params
        self.potency = potency
        self.visits = visits
        self.expires = expires

    def to_json(self):
        return [self.x, self.y, self.game_params._asdict(),
                self.potency, self.visits, self.expires, self.__class__.__name__]

    @classmethod
    def from_json(cls, json):
        module_location = {'Flower': 'flower', 'VenusBeeTrap': 'venus_bee_trap'}
        new_flower_class = getattr(sys.modules['hiveminder.' + module_location[json[-1]]], json[-1])
        return new_flower_class(json[0], json[1], GameParameters(**json[2]), *json[3:-1])

    __hash__ = None

    def __eq__(self, other):
        if isinstance(other, Flower):
            return self.to_json() == other.to_json()
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Flower):
            return self.to_json() != other.to_json()
        else:
            return NotImplemented

    def __repr__(self):
        return "Flower({})".format(", ".join(map(repr, self.to_json()[:-1])))

    def visit(self):
        self.visits += 1
        self.expires += self.game_params.flower_lifespan_visit_impact
        self.potency = min(3, self.visits // self.game_params.flower_visit_potency_ratio + 1)

        # Return True if we make a seed
        return (self.visits >= self.game_params.flower_seed_visit_initial_threshold and
                self.visits % self.game_params.flower_seed_visit_subsequent_threshold == 0)
