from hiveminder import algo_player
from hiveminder.utils import is_on_course_with


new_headings = {0: [60, -60],
                60: [120, 0],
                120: [180, 60],
                180: [-120, 120],
                - 120: [-60, 180],
                - 60: [0, -120], }


@algo_player(name="HiveMinder",
             description="another example of an algo")
def example_algo(board_width, board_height, hives, flowers, inflight, crashed,
                         lost_volants, received_volants, landed, scores, player_id, game_id, turn_num):
    if inflight:

        hive_locations = [hive[:2] for hive in hives]
        flower_locations = [flower[:2] for flower in flowers]
        filled_tiles = hive_locations + flower_locations

        for bee_id, bee in inflight.items():
            if bee[0] == "QueenBee" and bee[1:3] not in filled_tiles:
                # We have a queen in an empty tile, make a new hive
                return dict(entity=bee_id, command="create_hive")
            elif bee[0] == "Seed" and bee[1:3] not in filled_tiles:
                # We have a seed in an empty tile, make a new flower
                return dict(entity=bee_id, command="flower")
            elif bee[0] == "Bee" and bee[6] > 0 and not is_on_course_with(bee[1:3], bee[3], hive_locations[0]):
                # We have a nectar laden bee that is not on course with our first hive, rotate it
                current_heading = inflight[bee_id][3]
                return dict(entity=bee_id, command=new_headings[current_heading][0])
            elif bee[0] == "Bee" and bee[6] == 0 and not is_on_course_with(bee[1:3], bee[3], flower_locations[0]):
                # We have a nectar-less bee that is not on course with our first flower, rotate it
                current_heading = inflight[bee_id][3]
                return dict(entity=bee_id, command=new_headings[current_heading][0])

        # Otherwise, do nothing
        return None
