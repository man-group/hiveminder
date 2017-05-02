from __future__ import absolute_import
from .volant import Volant


class TrapSeed(Volant):
    def __init__(self, x, y, heading, lifespan):
        super(TrapSeed, self).__init__(x, y, heading)
        self.lifespan = lifespan

    def advance(self, reverse=False):
        trapSeed = super(TrapSeed, self).advance(reverse)
        trapSeed.lifespan -= 1
        return trapSeed

    def _new_from_xyh(self, x, y, h):
        return type(self)(x, y, h, self.lifespan)

    def to_json(self):
        return super(TrapSeed, self).to_json() + [self.lifespan]

    @classmethod
    def from_json(cls, json):
        return cls(*json[1:-1], lifespan=json[-1])
