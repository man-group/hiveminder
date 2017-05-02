from hiveminder.bee import Bee, QueenBee
from hiveminder.headings import heading_to_delta, LEGAL_HEADINGS
from hiveminder._util import is_even
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from mock import sentinel
import pytest


BEE_TYPES = (Bee, QueenBee)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_can_not_hash_a_Bee(BeeType):
    h = BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS)
    with pytest.raises(TypeError) as err:
        hash(h)
    assert str(err.value).startswith("unhashable type: '")


@pytest.mark.parametrize("BeeType", BEE_TYPES)
@pytest.mark.parametrize("x1, y1, heading1, energy1, nectar1, x2, y2, heading2, energy2, nectar2, are_equal",
                         [(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar,
                           sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar, True),
                          (sentinel.x1, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar,
                           sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar, False),
                          (sentinel.x, sentinel.y1, sentinel.h, sentinel.nrg, sentinel.nectar,
                           sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar, False),
                          (sentinel.x, sentinel.y, sentinel.h1, sentinel.nrg, sentinel.nectar,
                           sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar, False),
                          (sentinel.x, sentinel.y, sentinel.h, sentinel.nrg1, sentinel.nectar,
                           sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar, False),
                          (sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar,
                           sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, sentinel.nectar1, False),
                         ])
def test_Bees_equality(BeeType, x1, y1, heading1, energy1, nectar1, x2, y2, heading2, energy2, nectar2, are_equal):
    h1 = BeeType(x1, y1, heading1, energy1, DEFAULT_GAME_PARAMETERS, nectar1)
    h2 = BeeType(x2, y2, heading2, energy2, DEFAULT_GAME_PARAMETERS, nectar2)
    assert (h1 == h2) == are_equal
    assert (h1 != h2) == (not are_equal)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_bee_not_equal_to_other_types(BeeType):
    assert not (BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS) == sentinel.bee)
    assert BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS) != sentinel.bee
    

@pytest.mark.parametrize("BeeType1, BeeType2", [(t1,t2) for t1 in BEE_TYPES for t2 in BEE_TYPES if t1 != t2])
def test_bee_not_equal_to_other_type_of_bee(BeeType1, BeeType2):
    assert not (BeeType1(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS) == BeeType2(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS))
    assert BeeType1(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS) != BeeType2(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_can_convert_Bee_to_json(BeeType):
    assert (BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS, sentinel.nectar).to_json()
            == [BeeType.__name__, sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS._asdict(), sentinel.nectar])


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_can_read_Bee_from_json(BeeType):
    assert BeeType.from_json([sentinel.type, sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS._asdict(), sentinel.nectar]) == BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS, sentinel.nectar)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_repr(BeeType):
    assert repr(BeeType(1337, 2000, 123456, 71077345, DEFAULT_GAME_PARAMETERS, 1234)) == "{}(1337, 2000, 123456, 71077345, {}, 1234)".format(BeeType.__name__, DEFAULT_GAME_PARAMETERS._asdict())


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_str(BeeType):
    assert str(BeeType(1337, 2000, 123456, 71077345, DEFAULT_GAME_PARAMETERS, 1234)) == "{}(1337, 2000, 123456, 71077345, {}, 1234)".format(BeeType.__name__, DEFAULT_GAME_PARAMETERS._asdict())


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_can_get_position_and_heading_from_a_bee(BeeType):
    assert BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS, sentinel.nectar).xyh == (sentinel.x, sentinel.y, sentinel.h)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_can_set_position(BeeType):
    bee = BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS, sentinel.nectar)
    assert bee.set_position(sentinel.newx, sentinel.newy) == BeeType(sentinel.newx, sentinel.newy, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS, sentinel.nectar)

    # Original instance is not actually changed
    assert bee == BeeType(sentinel.x, sentinel.y, sentinel.h, sentinel.nrg, DEFAULT_GAME_PARAMETERS, sentinel.nectar)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
@pytest.mark.parametrize("heading", LEGAL_HEADINGS)
@pytest.mark.parametrize("column", [4, 5])
def test_can_advance_bee_along_a_heading(BeeType, heading, column):
    # Rather than patch heading_to_delta in BeeType.advance we just
    # assert that the effect of advancing the bee matches that
    # defined by heading_to_delta
    
    expected_dx, expected_dy = heading_to_delta(heading, is_even(column))
    
    bee = BeeType(column, 5, heading, 10, DEFAULT_GAME_PARAMETERS)
    assert bee.advance() == BeeType(column + expected_dx, 5 + expected_dy, heading, 9, DEFAULT_GAME_PARAMETERS)
    
    # Original instance is not actually changed
    assert bee == BeeType(column, 5, heading, 10, DEFAULT_GAME_PARAMETERS)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
def test_can_reverse_a_bee_along_a_heading(BeeType):
    bee = BeeType(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)
    assert bee.advance(reverse=True) == BeeType(5, 4, 180, 9, DEFAULT_GAME_PARAMETERS)
    
    # Original instance is not actually changed
    assert bee == BeeType(5, 5, 0, 10, DEFAULT_GAME_PARAMETERS)


@pytest.mark.parametrize("BeeType", BEE_TYPES)
@pytest.mark.parametrize("nectar", range(6))
@pytest.mark.parametrize("energy", [0, 1, 2, 3, 5, 10, 20])
@pytest.mark.parametrize("potency", range(1, 4))
def test_feed_bee(BeeType, energy, nectar, potency):
    bee = BeeType(0, 0, 0, energy, DEFAULT_GAME_PARAMETERS, nectar)

    fed_bee = bee.drink(potency)

    assert fed_bee == BeeType(0, 0, 0,
                          energy + potency * DEFAULT_GAME_PARAMETERS.bee_energy_boost_per_nectar,
                          DEFAULT_GAME_PARAMETERS,
                          min(DEFAULT_GAME_PARAMETERS.bee_nectar_capacity, nectar + potency))

    # Original instance is not actually changed
    assert bee == BeeType(0, 0, 0, energy, DEFAULT_GAME_PARAMETERS, nectar)
