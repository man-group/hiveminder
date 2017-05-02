from collections import namedtuple

GameParameters = namedtuple("GameParameters",
                            ["launch_probability",  # How likely a bee will be launched from a hive in each turn
                             "initial_energy",  # Initial energy that a newly launched bee has
                             "dead_bee_score_factor",  # How your score changes by having a bee die on your board
                             "hive_score_factor",  # How many points having a hive on your board is worth
                             "flower_score_factor",  # How many points having a flower on your board is worth
                             "nectar_score_factor",  # How many points returning nectar to your hive is worth
                             "queen_bee_nectar_threshold",  # Above this nectar value in a hive,
                                                            # the next bee a hive launches will be a queen
                             "bee_nectar_capacity",  # The maximum amount of nectar a bee can carry at one time
                             "bee_energy_boost_per_nectar",  # How much energy a bee gains each time it picks up nectar
                             "flower_seed_visit_initial_threshold",  # Number of times a flower must be visited
                                                                     # before generating a seed
                             "flower_seed_visit_subsequent_threshold",  # Number of times after initial visit,
                                                                        # a flower must be visited to generate a seed
                             "flower_visit_potency_ratio",  # The ratio of bee visits for flower potency increases
                             "flower_lifespan",  # How long a flower will live for if it is never visited
                             "flower_lifespan_visit_impact"  # Extra turns through which a flower will live
                                                             # for every visit from a bee
                             ])


DEFAULT_GAME_PARAMETERS = GameParameters(launch_probability=0.2,
                                         initial_energy=10,
                                         dead_bee_score_factor=-3,
                                         hive_score_factor=200,
                                         flower_score_factor=50,
                                         nectar_score_factor=2,
                                         queen_bee_nectar_threshold=100,
                                         bee_nectar_capacity=5,
                                         bee_energy_boost_per_nectar=25,
                                         flower_seed_visit_initial_threshold=10,
                                         flower_seed_visit_subsequent_threshold=10,
                                         flower_visit_potency_ratio=10,
                                         flower_lifespan=300,
                                         flower_lifespan_visit_impact=10
                                         )
