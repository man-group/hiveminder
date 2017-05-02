from hiveminder.hive import Hive
from mock import sentinel
import pytest


def test_can_not_hash_a_hive():
    h = Hive(sentinel.x, sentinel.y)
    with pytest.raises(TypeError) as err:
        hash(h)
    assert str(err.value) == "unhashable type: 'Hive'"


@pytest.mark.parametrize("x1, y1, n1, are_equal", [(sentinel.x, sentinel.y, sentinel.n, True),
                                                   (sentinel.x1, sentinel.y, sentinel.n, False),
                                                   (sentinel.x, sentinel.y1, sentinel.n, False),
                                                   (sentinel.x, sentinel.y, sentinel.n1, False)
                                                   ])
def test_hives_equality(x1, y1, n1, are_equal):
    h1 = Hive(x1, y1, n1)
    h2 = Hive(sentinel.x, sentinel.y, sentinel.n)
    assert (h1 == h2) == are_equal
    assert (h1 != h2) == (not are_equal)
    

def test_hive_not_equal_to_other_types():
    assert not (Hive(sentinel.x, sentinel.y) == sentinel.hive)
    assert Hive(sentinel.x, sentinel.y) != sentinel.hive


def test_can_convert_hive_to_json():
    assert Hive(sentinel.x, sentinel.y, sentinel.nectar).to_json() == [sentinel.x, sentinel.y, sentinel.nectar]


def test_can_read_hive_from_json():
    assert Hive.from_json([sentinel.x, sentinel.y, sentinel.nectar]) == Hive(sentinel.x, sentinel.y, sentinel.nectar)


def test_repr():
    assert repr(Hive(1337, 2000, 23)) == "Hive(1337, 2000, 23)"
    

def test_str():
    assert str(Hive(1337, 2000, 23)) == "Hive(1337, 2000, 23)"
