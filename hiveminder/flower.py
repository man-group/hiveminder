from __future__ import absolute_import, division
from hiveminder.game_params import GameParameters


class Flower(object):
    def __init__(self, x, y, game_params, potency=1, visits=0, expires=None):
        self.x = x
        self.y = y
        self.game_params = game_params
        self.potency = potency
        self.visits = visits
        self.expires = expires

    def to_json(self):
        return [self.x, self.y, self.game_params._asdict(), self.potency, self.visits, self.expires]

    @classmethod
    def from_json(cls, json):
        return cls(json[0], json[1], GameParameters(**json[2]), *json[3:])

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
        return "Flower({})".format(", ".join(map(repr, self.to_json())))

    def visit(self):
        self.visits += 1
        self.expires += self.game_params.flower_lifespan_visit_impact
        self.potency = min(3, self.visits // self.game_params.flower_visit_potency_ratio + 1)

        # Return True if we make a seed
        return (self.visits >= self.game_params.flower_seed_visit_initial_threshold and
                self.visits % self.game_params.flower_seed_visit_subsequent_threshold == 0)
