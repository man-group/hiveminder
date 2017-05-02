from hiveminder.flower import Flower
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest

from hiveminder.venus_bee_trap import VenusBeeTrap


def test_can_not_hash_a_flower():
    h = Flower(sentinel.x, sentinel.y, DEFAULT_GAME_PARAMETERS, sentinel.potency)
    with pytest.raises(TypeError) as err:
        hash(h)
    assert str(err.value) == "unhashable type: 'Flower'"


@pytest.mark.parametrize("x1, y1, size1, x2, y2, size2, are_equal", [(sentinel.x, sentinel.y, sentinel.potency, sentinel.x, sentinel.y, sentinel.potency, True),
                                                                     (sentinel.x1, sentinel.y, sentinel.potency, sentinel.x, sentinel.y, sentinel.potency, False),
                                                                     (sentinel.x, sentinel.y1, sentinel.potency, sentinel.x, sentinel.y, sentinel.potency, False),
                                                                     (sentinel.x, sentinel.y, sentinel.size1, sentinel.x, sentinel.y, sentinel.potency, False)
                                                                     ])
def test_Flowers_equality(x1, y1, size1, x2, y2, size2, are_equal):
    h1 = Flower(x1, y1, DEFAULT_GAME_PARAMETERS, size1)
    h2 = Flower(x2, y2, DEFAULT_GAME_PARAMETERS, size2)
    assert (h1 == h2) == are_equal
    assert (h1 != h2) == (not are_equal)


@pytest.mark.parametrize("flower_type", [Flower, VenusBeeTrap])
def test_can_convert_flower_to_from_json(flower_type):
    flower = flower_type(sentinel.x, sentinel.y, DEFAULT_GAME_PARAMETERS, sentinel.potency, sentinel.visits, sentinel.expires)
    bounce_flower = Flower.from_json(flower.to_json())
    assert flower == bounce_flower


def test_repr():
    assert repr(Flower(1337, 2000, DEFAULT_GAME_PARAMETERS, 54321, 1234, 3000)) == "Flower(1337, 2000, %s, 54321, 1234, 3000)" % DEFAULT_GAME_PARAMETERS._asdict()


def test_repr_venus_bee_trap():
    assert (repr(VenusBeeTrap(1337, 2000, DEFAULT_GAME_PARAMETERS, 54321, 1234, 3000)) ==
            "VenusBeeTrap(1337, 2000, %s, 54321, 1234, 3000)" % DEFAULT_GAME_PARAMETERS._asdict())


def test_str():
    assert str(Flower(1337, 2000, DEFAULT_GAME_PARAMETERS, 54321, 1234, 3000)) == "Flower(1337, 2000, %s, 54321, 1234, 3000)" % DEFAULT_GAME_PARAMETERS._asdict()
