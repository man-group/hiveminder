from __future__ import absolute_import
from hiveminder.headings import heading_to_delta
import pytest

@pytest.mark.parametrize(("heading", "even_col", "expected_delta"), [(0, True, (0, 1)),
                                                                     (0, False, (0, 1)),
                                                                     (60, True, (1, 1)),
                                                                     (60, False, (1, 0)),
                                                                     (120, True, (1, 0)),
                                                                     (120, False, (1, -1)),
                                                                     (180, True, (0, -1)),
                                                                     (180, False, (0, -1)),
                                                                     (-120, True, (-1, 0)),
                                                                     (-120, False, (-1, -1)),
                                                                     (-60, True, (-1, 1)),
                                                                     (-60, False, (-1, 0)),])
def test_heading_to_delta(heading, even_col, expected_delta):
    assert expected_delta == heading_to_delta(heading, even_col)
    

def test_illegal_heading_to_delta():
    with pytest.raises(ValueError) as err:
        heading_to_delta(1, True)
    assert str(err.value) == "Illegal heading"
