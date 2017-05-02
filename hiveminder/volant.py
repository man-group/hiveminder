from __future__ import absolute_import
from .headings import OPPOSITE_HEADINGS, heading_to_delta
from hiveminder._util import is_even


class Volant(object):
    def __init__(self, x, y, heading):
        self.x = x
        self.y = y
        self.heading = heading

    def _new_from_xyh(self, x, y, h):
        return type(self)(x, y, h)

    def to_json(self):
        return [self.__class__.__name__, self.x, self.y, self.heading]

    def advance(self, reverse=False):
        heading = OPPOSITE_HEADINGS[self.heading] if reverse else self.heading
        dx, dy = heading_to_delta(heading, is_even(self.x))
        return self._new_from_xyh(self.x + dx, self.y + dy, heading)

    def set_position(self, x, y):
        return self._new_from_xyh(x, y, self.heading)

    @property
    def xyh(self):
        return self.x, self.y, self.heading

    @classmethod
    def from_json(cls, json):
        return cls(*json[1:])

    __hash__ = None

    def __eq__(self, other):
        if isinstance(other, Volant):
            return self.to_json() == other.to_json()
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Volant):
            return self.to_json() != other.to_json()
        else:
            return NotImplemented

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, ", ".join(map(repr, self.to_json()[1:])))
