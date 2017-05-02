from hiveminder.seed import Seed
from hiveminder.headings import heading_to_delta, LEGAL_HEADINGS
from hiveminder._util import is_even
from mock import sentinel
import pytest


def test_can_not_hash_a_seed():
    h = Seed(sentinel.x, sentinel.y, sentinel.h)
    with pytest.raises(TypeError) as err:
        hash(h)
    assert str(err.value) == "unhashable type: 'Seed'"


@pytest.mark.parametrize("x1, y1, heading1, x2, y2, heading2, are_equal",
                         [(sentinel.x, sentinel.y, sentinel.h,
                           sentinel.x, sentinel.y, sentinel.h, True),
                          (sentinel.x1, sentinel.y, sentinel.h,
                           sentinel.x, sentinel.y, sentinel.h, False),
                          (sentinel.x, sentinel.y1, sentinel.h,
                           sentinel.x, sentinel.y, sentinel.h, False),
                          (sentinel.x, sentinel.y, sentinel.h1,
                           sentinel.x, sentinel.y, sentinel.h, False),
                         ])
def test_seeds_equality(x1, y1, heading1, x2, y2, heading2, are_equal):
    h1 = Seed(x1, y1, heading1)
    h2 = Seed(x2, y2, heading2)
    assert (h1 == h2) == are_equal
    assert (h1 != h2) == (not are_equal)


def test_seed_not_equal_to_other_types():
    assert not (Seed(sentinel.x, sentinel.y, sentinel.h) == sentinel.seed)
    assert Seed(sentinel.x, sentinel.y, sentinel.h) != sentinel.seed
    

def test_can_convert_seed_to_json():
    assert (Seed(sentinel.x, sentinel.y, sentinel.h).to_json()
            == ["Seed", sentinel.x, sentinel.y, sentinel.h])


def test_can_read_seed_from_json():
    assert Seed.from_json([sentinel.type, sentinel.x, sentinel.y, sentinel.h]) == Seed(sentinel.x, sentinel.y, sentinel.h) 


def test_repr():
    assert repr(Seed(1337, 2000, 123456)) == "Seed(1337, 2000, 123456)"


def test_str():
    assert str(Seed(1337, 2000, 123456)) == "Seed(1337, 2000, 123456)"


def test_can_get_position_and_heading_from_a_seed():
    assert Seed(sentinel.x, sentinel.y, sentinel.h).xyh == (sentinel.x, sentinel.y, sentinel.h)


def test_can_set_position():
    seed = Seed(sentinel.x, sentinel.y, sentinel.h)
    assert seed.set_position(sentinel.newx, sentinel.newy) == Seed(sentinel.newx, sentinel.newy, sentinel.h)

    # Original instance is not actually changed
    assert seed == Seed(sentinel.x, sentinel.y, sentinel.h)


@pytest.mark.parametrize("heading", LEGAL_HEADINGS)
@pytest.mark.parametrize("column", [4, 5])
def test_can_advance_seed_along_a_heading(heading, column):
    # Rather than patch heading_to_delta in Seed.advance we just
    # assert that the effect of advancing the seed matches that
    # defined by heading_to_delta
    
    expected_dx, expected_dy = heading_to_delta(heading, is_even(column))
    
    seed = Seed(column, 5, heading)
    assert seed.advance() == Seed(column + expected_dx, 5 + expected_dy, heading)
    
    # Original instance is not actually changed
    assert seed == Seed(column, 5, heading)


def test_can_reverse_a_seed_along_a_heading():
    seed = Seed(5, 5, 0)
    assert seed.advance(reverse=True) == Seed(5, 4, 180)
    
    # Original instance is not actually changed
    assert seed == Seed(5, 5, 0)
