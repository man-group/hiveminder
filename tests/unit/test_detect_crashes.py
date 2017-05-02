from __future__ import absolute_import
from hiveminder.game import GameState
from hiveminder.bee import Bee, QueenBee
from hiveminder.seed import Seed
from hiveminder.hive import Hive
from hiveminder.game_params import DEFAULT_GAME_PARAMETERS
from itertools import combinations_with_replacement
import pytest
from mock import sentinel
from .test_bee import BEE_TYPES
from hiveminder.venus_bee_trap import VenusBeeTrap
from hiveminder.trap_seed import TrapSeed


# There are at most 6 bees in these test cases, so parametrise tests with the different combinations of Bee types
# as from a crashing perspective, bees and queen bees shouldn't behave differently.
# In the test specs, a tuple will be used to instantiate a bee of the appropriate type
@pytest.mark.parametrize("bee_types", combinations_with_replacement(BEE_TYPES, 6))
@pytest.mark.parametrize("crash_board", range(2))
@pytest.mark.parametrize("noncrash_board", range(2))
@pytest.mark.parametrize("crashing_volant_specs", [
                                            # No crashes
                                            {},
                                            # Out of fuel
                                            {"exhausted": {0: (5, 5, 0, -1, 0)}},
                                            {"exhausted": {0: (5, 5, 0, -1, 0), 1: (6, 6, 0, -1, 0)}},
                                            # Same cell same direction
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 0, 10, 0)}},
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 0, 10, 0), 2: (5, 5, 0, 10, 0)}},
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 0, 10, 0), 2: (6, 6, 0, 10, 0), 3: (6, 6, 0, 10, 0)}},
                                            # Same cell different directions
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 60, 10, 0)}},
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 120, 10, 0)}},
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 180, 10, 0)}},
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, -120, 10, 0)}},
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, -60, 10, 0)}},
                                            # Head on collisions
                                            {"headon": {0: (5, 5, 180, 10, 0), 1: (5, 6, 0, 10, 0)}},  # North-South
                                            {"headon": {0: (5, 5, -120, 10, 0), 1: (6, 5, 60, 10, 0)}},  # NorthEast-SouthWest
                                            {"headon": {0: (5, 5, -60, 10, 0), 1: (6, 4, 120, 10, 0)}},  # NorthWest-SouthEast
                                            # Multiple head on collisions
                                            {"headon": {0: (5, 5, 180, 10, 0), 1: (5, 6, 0, 10, 0), 2: (3, 3, -120, 10, 0), 3: (4, 3, 60, 10, 0)}},
                                            {"headon": {0: (5, 5, 180, 10, 0), 1: (5, 6, 0, 10, 0), 4: (7, 7, -60, 10, 0), 5: (8, 6, 120, 10, 0)}},
                                            {"headon": {0: (5, 5, 180, 10, 0), 1: (5, 6, 0, 10, 0), 2: (3, 3, -120, 10, 0), 3: (4, 3, 60, 10, 0), 4: (7, 7, -60, 10, 0), 5: (8, 6, 120, 10, 0)}},
                                             # Mixed collision types
                                            {"collided": {0: (5, 5, 0, 10, 0), 1: (5, 5, 0, 10, 0)}, "exhausted": {2: (6, 6, 0, -1, 0)}},
                                            {"collided": {0: (5, 5, 180, 10, 0), 1: (6, 6, 0, 10, 0), 2: (5, 5, 60, 10, 0), 3: (6, 6, -120, 10, 0)}},
                                            {"collided": {0: (5, 5, 180, 10, 0), 1: (6, 6, 0, 10, 0), 2: (5, 5, 60, 10, 0), 3: (6, 6, -120, 10, 0)}, "exhausted": {4: (3, 3, 0, -1, 0)}},
                                            # Seeds same cell same direction
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, 0)}},
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, 0), 2: Seed(5, 5, 0)}},
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, 0), 2: Seed(6, 6, 0), 3: Seed(6, 6, 0)}},
                                            # Seeds same cell different directions
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, 60)}},
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, 120)}},
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, 180)}},
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, -120)}},
                                            {"seeds": {0: Seed(5, 5, 0), 1: Seed(5, 5, -60)}},
                                            # TrapSeed/Seeds same cell same direction
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, 0)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, 0), 2: Seed(5, 5, 0)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, 0), 2: Seed(6, 6, 0), 3: Seed(6, 6, 0)}},
                                            # TrapSeed/Seeds same cell different directions
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, 60)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, 120)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, 180)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, -120)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: Seed(5, 5, -60)}},
                                            # TrapSeed same cell same direction
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, 0, 5)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, 0, 5), 2: TrapSeed(5, 5, 0, 5)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, 0, 5), 2: TrapSeed(6, 6, 0, 5), 3: TrapSeed(6, 6, 0, 5)}},
                                            # TrapSeed same cell different directions
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, 60, 5)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, 120, 5)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, 180, 5)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, -120, 5)}},
                                            {"seeds": {0: TrapSeed(5, 5, 0, 5), 1: TrapSeed(5, 5, -60, 5)}},
                                            # Gobbled by Venus Bee Trap
                                            {"gobbled": {0: (9, 9, 0, 10, 0)}},
                                            {"gobbled": {0: (9, 9, 0, 10, 0), 1: (9, 9, 0, 10, 0)}},
                                            ])
@pytest.mark.parametrize("noncrash_volant_specs", [
                                            # Bees
                                            {10: (8, 8, 0, 10, 0)},
                                            {10: (8, 8, 0, 10, 0), 11: (0, 0, 60, 10, 0)},
                                            {10: (8, 8, 0, 10, 0), 11: (0, 0, 60, 10, 0), 12: (1, 1, 180, 10, 0)},
                                            # Seeds
                                            {100: Seed(8, 8, 0,)},
                                            {100: Seed(8, 8, 0,), 110: Seed(0, 0, 60)},
                                            {100: Seed(8, 8, 0,), 110: Seed(0, 0, 60), 120: Seed(1, 1, 180)},
                                            # Head-on seeds
                                            {200: Seed(1, 1, 180), 201: Seed(1, 2, 0), 202: Seed(3, 3, -120), 203: Seed(4, 3, 60)},
                                            # Bees and Seeds
                                            {10: (8, 8, 0, 10, 0), 100: Seed(8, 8, 0,)},
                                            {10: (8, 8, 0, 10, 0), 11: (0, 0, 60, 10, 0), 100: Seed(8, 8, 0,), 110: Seed(0, 0, 60)},
                                            {10: (8, 8, 0, 10, 0), 11: (0, 0, 60, 10, 0), 12: (1, 1, 180, 10, 0), 100: Seed(8, 8, 0,), 110: Seed(0, 0, 60), 120: Seed(1, 1, 180)},
                                             ])
def test_detect_crashes(bee_types, crash_board, noncrash_board, crashing_volant_specs, noncrash_volant_specs):
    game = GameState(game_params=DEFAULT_GAME_PARAMETERS,
                     game_id=sentinel.game_id,
                     boards=2,
                     board_width=sentinel.board_width,
                     board_height=sentinel.board_height,
                     hives=[[Hive(0, 0, 0)]] * 2,
                     flowers=[[VenusBeeTrap(9, 9, DEFAULT_GAME_PARAMETERS)]] * 2,
                     game_length=sentinel.game_length)

    def apply_bee_type_to_specs(bees_specs):
        """ Create bee instances from the specs in the test cases which are tuples
            if not, return the spec as is (will probably be a seed)"""
        def create_bee_or_seed(id, spec):
            if type(spec) is tuple:
                x, y, h, e, n = spec
                return bee_types[id % 10](x, y, h, e, DEFAULT_GAME_PARAMETERS, n)
            else:
                return spec
        return {bee_id:  create_bee_or_seed(bee_id, bee) for bee_id, bee in bees_specs.items()}

    crashing_volants = {crash_type: apply_bee_type_to_specs(volants)
                        for crash_type, volants in crashing_volant_specs.items()}
    noncrash_volants = apply_bee_type_to_specs(noncrash_volant_specs)
    crashing_volants_summary = {volant_id: volant
                                for volants in crashing_volants.values()
                                for volant_id, volant in volants.items()}
    crashing_bees_summary = {bee_id: bee for bee_id, bee in crashing_volants_summary.items() if isinstance(bee, Bee)}
    crashing_volants.setdefault("collided", {})
    crashing_volants.setdefault("exhausted", {})
    crashing_volants.setdefault("headon", {})
    crashing_volants.setdefault("gobbled", {})
    crashing_volants.setdefault("seeds", {})

    for board, volants in ((crash_board, crashing_volants_summary), (noncrash_board, noncrash_volants)):
        for bee_id, bee_details in volants.items():
            game.boards[board].inflight[bee_id] = bee_details

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor + DEFAULT_GAME_PARAMETERS.venus_score_factor for board in game.boards)

    crashes = game.detect_crashes()

    assert all(board.calculate_score() == DEFAULT_GAME_PARAMETERS.hive_score_factor + DEFAULT_GAME_PARAMETERS.venus_score_factor
                                            for i, board in enumerate(game.boards) if i != crash_board)
    assert (game.boards[crash_board].calculate_score() ==
            DEFAULT_GAME_PARAMETERS.hive_score_factor + DEFAULT_GAME_PARAMETERS.venus_score_factor + DEFAULT_GAME_PARAMETERS.dead_bee_score_factor * len(crashing_bees_summary))

    for board, crashed_bees in enumerate(crashes):
        if board == crash_board:
            assert crashed_bees == crashing_volants
        else:
            assert crashed_bees == dict(collided={}, headon={}, exhausted={}, gobbled={}, seeds={})
