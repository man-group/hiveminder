from __future__ import absolute_import


class Hive(object):
    def __init__(self, x, y, nectar=0):
        self.x = x
        self.y = y
        self.nectar = nectar

    def to_json(self):
        return [self.x, self.y, self.nectar]

    @classmethod
    def from_json(cls, json):
        return cls(*json)

    __hash__ = None

    def __eq__(self, other):
        if isinstance(other, Hive):
            return self.to_json() == other.to_json()
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, Hive):
            return self.to_json() != other.to_json()
        else:
            return NotImplemented

    def __repr__(self):
        return "Hive({})".format(", ".join(map(repr, self.to_json())))
