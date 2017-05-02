from __future__ import absolute_import, division
from .flower import Flower


class VenusBeeTrap(Flower):
    def __eq__(self, other):
        if isinstance(other, VenusBeeTrap):
            return self.to_json() == other.to_json()
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, VenusBeeTrap):
            return self.to_json() != other.to_json()
        else:
            return NotImplemented

    def __repr__(self):
        return "VenusBeeTrap({})".format(", ".join(map(repr, self.to_json()[:-1])))
