from __future__ import absolute_import
from hiveminder._util import sign


OPPOSITE_HEADINGS = {0: 180,
                     180: 0,
                     60:-120,
                     - 120: 60,
                     120:-60,
                     - 60: 120}

LEGAL_NEW_HEADINGS = {0: {-60, 0, 60},
                      60: {0, 60, 120},
                      120: {60, 120, 180},
                      180: {120, 180, -120},
                      - 120: {180, -120, -60},
                      - 60: {-120, -60, 0}}

LEGAL_HEADINGS = list(LEGAL_NEW_HEADINGS)


def heading_to_delta(heading, even_col):
    if heading not in LEGAL_HEADINGS:
        raise ValueError('Illegal heading')
    elif (heading % 180) == 0:  # North or South
        return (0, 1 - abs(heading) // 90)
    else:
        dx = sign(heading)
        dy = (2 if even_col else 1) - abs(heading // 60)
        return dx, dy
