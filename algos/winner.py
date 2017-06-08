"""
This is the winning algo from the Man AHL Coder Prize 2017
Written by Matthew Ridley from the University of Oxford
"""
from hiveminder import algo_player
try:
    from time import perf_counter
except ImportError:
    from time import clock as perf_counter # work around for python 2, will not be high enough resolution on Windows
from copy import copy

TIME_LIMIT = 140000/1e6
PRUNING_FACTOR = 6
HIVE_THRESHOLD = 20
BEE_FACTOR = 1
NECTAR_FACTOR = 1
VISIT_FACTOR = 1
SPACE_THRESH = 0
H_SPACE_FACTOR = 1000
F_SPACE_FACTOR = 10
SABOTAGE_FACTOR = 500
EDGE_FACTOR = 1500
TRAP_EDGE_FACTOR = 100
SUPER_SAB_FACTOR = 1000

new_headings = {0: [60, -60],
                60: [120, 0],
                120: [180, 60],
                180: [-120, 120],
                - 120: [-60, 180],
                - 60: [0, -120], }

op_headings = {0: 180,
               60: -120,
               120: -60,
               180: 0,
               -60: 120,
               -120: 60}

doomed_pairs = [
    [[0, 0], -120],
    [[0, 7], -60],
    [[7, 7], 60],
    [[7, 0], -120],
    [[0, 7], 0],
    [[2, 7], 0],
    [[4, 7], 0],
    [[6, 7], 0],
    [[1, 0], 180],
    [[3, 0], 180],
    [[5, 0], 180],
    [[7, 0], 180],
]

cruel_pairs = [
    [[2,7], 0],
    [[4,7], 0],
    [[6,7], 0],
    [[1,0], 180],
    [[3,0], 180],
    [[5,0], 180],
]

def heading_to_delta(heading, even_col):
    if (heading % 180) == 0:  # North or South
        return (0, 1 - abs(heading) // 90)
    else:
        dx = -1 if heading < 0 else 1
        dy = (2 if even_col else 1) - abs(heading // 60)
        return dx, dy

class Node:
    def __init__(self, cmd, board_state, turn_num, board_hash, parent):
        self.cmd = cmd
        self.board_state = board_state
        self.turn_num = turn_num
        self.board_hash = board_hash
        self.parent = parent
        self.score = None
        self.children = []
        self.depth = 0
    def add_child(self, node):
        if not self.children:
            self.children.append(node)
        else:
            i = 0
            while (i < len(self.children)) and (node.score < self.children[i].score):
                i += 1
            self.children.insert(i, node)
    def add_layer(self, hash_tab, bhash_tab):
        poss_cmds = possible_moves(self.board_state, self.turn_num)
        if poss_cmds == [None]:
            return
        for cmd in poss_cmds:
            new_board_state = perform_move(self.board_state, cmd, self.turn_num)
            new_board_hash = (str(new_board_state["hives"]) +
                                  str(new_board_state["flowers"]) +
                                  str(new_board_state["inflight"]) +
                                  str(self.turn_num+1))
            child_node = Node(cmd, new_board_state, self.turn_num+1, new_board_hash, self)
            child_node.eval_score(hash_tab, bhash_tab)
            self.add_child(child_node)
    def eval_score(self, hash_tab, bhash_tab):
        if self.board_hash in hash_tab:
            self.score = hash_tab[self.board_hash][0]
        else:
            self.score = evaluate_board_score(self.board_state, bhash_tab)
            hash_tab[self.board_hash] = [self.score, 0]
    def update_score(self, hash_tab):
        if self.children == []:
            return
        self.depth = max([n.depth for n in self.children]) + 1
        if self.board_hash in hash_tab and hash_tab[self.board_hash][1] >= self.depth:
            self.score = hash_tab[self.board_hash][0]
        else:
            self.score = max([n.score for n in self.children])
            hash_tab[self.board_hash] = [self.score, self.depth]


class Tree:
    def __init__(self, board_json, turn_num, score_table, board_table):
        self.head_node = Node(None, board_json, turn_num, None, None)
        self.hash_tab = score_table
        self.bhash_tab = board_table
        self.update_queue = [self.head_node]
        self.update()
    def update(self):
        if self.update_queue == []:
            return
        current_node = self.update_queue.pop(0)
        current_node.add_layer(self.hash_tab, self.bhash_tab)
        self.update_queue += current_node.children[:PRUNING_FACTOR]
        while current_node:
            current_node.update_score(self.hash_tab)
            current_node = current_node.parent
    def best_cmd(self):
        best_cmd = self.head_node.children[0].cmd
        best_score = self.head_node.children[0].score
        for cn in self.head_node.children[1:]:
            if cn.score > best_score:
                best_score = cn.score
                best_cmd = cn.cmd
        return best_cmd

def find_num_spaces(h_ls):
    occupied = h_ls + [10*i + j for i in [-1, 8] for j in range(-1,9)] + [10*i + j for i in range(-1,9) for j in [-1, 8]]
    tiles = {10*i+j: (1 if 10*i + j not in occupied else 0) for i in range(-1, 9) for j in range(-1, 9)}
    queue1 = [t for t in tiles if tiles[t]]
    num_spaces = 0
    while queue1:
        start_tile = queue1.pop(0)
        if tiles[start_tile]:
            queue2 = [start_tile]
            size = 0
            while queue2:
                tile = queue2.pop(0)
                if not tiles[tile]:
                    continue
                tiles[tile] = 0
                size += 1
                i, j = tile // 10, tile % 10
                if tiles[10*i + j+1]:
                    queue2.append(10*i + j+1)
                if tiles[10*i + j-1]:
                    queue2.append(10*i + j-1)
                if tiles[10*(i+1) + j]:
                    queue2.append(10*(i+1) + j)
                if tiles[10*(i-1) + j]:
                    queue2.append(10*(i-1) + j)
                if i%2:
                    if tiles[10*(i-1) + j-1]:
                        queue2.append(10*(i-1) + j-1)
                    if tiles[10*(i+1) + j-1]:
                        queue2.append(10*(i+1) + j-1)
                else:
                    if tiles[10*(i-1) + j+1]:
                        queue2.append(10*(i-1) + j+1)
                    if tiles[10*(i+1) + j+1]:
                        queue2.append(10*(i+1) + j+1)
            if size:
                num_spaces += 1
    return num_spaces

def find_largest_space(h_ls):
    occupied = h_ls + [[i, j] for i in [-1, 8] for j in range(-1,9)] + [[i, j] for i in range(-1,9) for j in [-1, 8]]
    tiles = {10*i+j: (1 if [i, j] not in occupied else 0) for i in range(-1, 9) for j in range(-1, 9)}
    queue1 = [t for t in tiles if tiles[t]]
    largest = 0
    while queue1:
        start_tile = queue1.pop(0)
        if tiles[start_tile]:
            size = 0
            queue2 = [start_tile]
            while queue2:
                tile = queue2.pop(0)
                if not tiles[tile]:
                    continue
                tiles[tile] = 0
                size += 1
                i, j = tile // 10, tile % 10
                if tiles[10*i + j+1]:
                    queue2.append(10*i + j+1)
                if tiles[10*i + j-1]:
                    queue2.append(10*i + j-1)
                if tiles[10*(i+1) + j]:
                    queue2.append(10*(i+1) + j)
                if tiles[10*(i-1) + j]:
                    queue2.append(10*(i-1) + j)
                if i%2:
                    if tiles[10*(i-1) + j-1]:
                        queue2.append(10*(i-1) + j-1)
                    if tiles[10*(i+1) + j-1]:
                        queue2.append(10*(i+1) + j-1)
                else:
                    if tiles[10*(i-1) + j+1]:
                        queue2.append(10*(i-1) + j+1)
                    if tiles[10*(i+1) + j+1]:
                        queue2.append(10*(i+1) + j+1)
            largest = max(largest, size)
    return largest

def game_def_score(board_json):
    return (-3*board_json["deadbees"] +
            len(board_json["hives"]) * 200 + len([f for f in board_json["flowers"] if f[5] == "Flower"]) * 50 +
            sum(hive[2] for hive in board_json["hives"]) * 2) - len([f for f in board_json["flowers"] if f[5] == "VenusBeeTrap"]) * 50

def evaluate_board_score(board_json, space_hash_tab):
    score = 10*game_def_score(board_json)
    hive_locations = [h[:2] for h in board_json["hives"]]
    nectar_list = [bee[5] for bee in board_json["inflight"].values()
                    if bee[0] == "Bee"]
    score += BEE_FACTOR*len(nectar_list)
    score += NECTAR_FACTOR*sum(nectar_list)
    score += VISIT_FACTOR*sum([flower[3] for flower in board_json["flowers"] if flower[5] == "Flower"])
    score -= VISIT_FACTOR*sum([flower[3] for flower in board_json["flowers"] if flower[5] == "VenusBeeTrap"])
    trap_seeds = [v for _, v in board_json["inflight"].items() if v[0] == "TrapSeed"]
    if trap_seeds:
        for v in trap_seeds:
            if [v[1:3], v[3]] in cruel_pairs and v[4] in [1, 2]:
                score += SUPER_SAB_FACTOR
            elif about_to_leave(v[1:3], v[3]) and v[4] < 2:
                score += SABOTAGE_FACTOR
        edge_trap_seeds = [1 for f in trap_seeds if ((f[1] in [0,7]) or (f[2] in [0,7]))]
        score += TRAP_EDGE_FACTOR*len(edge_trap_seeds)
    edge_hives = [1 for h in hive_locations if h[0] in [0, 7] or h[1] in [0,7]]
    score -= EDGE_FACTOR*len(edge_hives)
    _hash = str(hive_locations)
    if _hash in space_hash_tab:
        score += space_hash_tab[_hash][0]
        score += space_hash_tab[_hash][1]
    else:
        hives = set(10*h[0]+h[1] for h in hive_locations)
        fullb = set(10*i + j for i in range(8) for  j in range(8))
        not_hives = list(fullb - hives)
        h_spaces = H_SPACE_FACTOR*find_num_spaces(not_hives)
        f_spaces = F_SPACE_FACTOR*find_largest_space(hive_locations)
        space_hash_tab[_hash] = [h_spaces, f_spaces]
        score += h_spaces + f_spaces
    return score

def about_to_leave(position, heading):
    if [position, heading] in [[[1, 1], -120], [[6, 6], 60]]:
        return True
    if position[1] == 6 and heading == 0 and position[0] in [2, 4, 6]:
        return True
    elif position[1] == 1 and heading == 180 and position[0] in [1, 3, 5]:
        return True
    dx, dy = heading_to_delta(heading, (position[0]+1)%2)
    return ((position[0]+dx) // 8) or ((position[1]+dy) // 8)

def saver_new_heading(position, heading):
    if not about_to_leave(position, new_headings[heading][0]):
        return new_headings[heading][0]
    return new_headings[heading][1]

def flower_placer(hive_locations, filled_tiles):
    next_to_hives = []
    for x,y in hive_locations:
        nearby = [[x, y+1], [x, y-1]]
        if x%2:
            nearby += [[x+i, y+j] for i in [-1, 1] for j in [-1, 0]]
        else:
            nearby += [[x+i, y+j] for i in [-1, 1] for j in [0, 1]]
        for xi, yj in nearby:
            if (not (xi//8)) and (not (yj//8)) and [xi, yj] not in filled_tiles + next_to_hives:
                next_to_hives.append([xi, yj])
    return next_to_hives

def possible_moves(board_json, turn_num):
    hive_locations = [hive[:2] for hive in board_json["hives"]]
    flower_locations = [flower[:2] for flower in board_json["flowers"] if flower[5] == "Flower"]
    trap_locations = [flower[:2] for flower in board_json["flowers"] if flower[5] == "VenusBeeTrap"]
    filled_tiles = hive_locations + flower_locations
    next_to_hives = []
    if "Seed" in [bee[0] for bee in board_json["inflight"].values()]:
        if len(trap_locations) > 0:
            next_to_hives = trap_locations
            if len(trap_locations) < 3 and (turn_num < 9800):
                if len(hive_locations) < HIVE_THRESHOLD:
                    next_to_hives += flower_placer(hive_locations, filled_tiles)
                else:
                    next_to_hives += flower_placer(flower_locations, filled_tiles)
        elif len(hive_locations) < HIVE_THRESHOLD:
            next_to_hives = flower_placer(hive_locations, filled_tiles)
        else:
            next_to_hives = flower_placer(flower_locations, filled_tiles)
    # create list of possible moves
    possible_moves = [None]
    for bee_id, bee in board_json["inflight"].items():
        if bee[0] == "QueenBee":
            if [bee[1:3], bee[3]] in doomed_pairs:
                cmd = dict(entity=bee_id, command="create_hive")
                possible_moves.append(cmd)
            elif about_to_leave(bee[1:3], bee[3]):
                cmd1 = dict(entity=bee_id, command=saver_new_heading(bee[1:3], bee[3]))
                cmd2 = dict(entity=bee_id, command="create_hive")
                possible_moves += [cmd1, cmd2]
            else:
                for new_heading in new_headings[bee[3]]:
                    cmd = dict(entity=bee_id, command=new_heading)
                    possible_moves.append(cmd)
                if bee[1:3] not in hive_locations:
                    cmd = dict(entity=bee_id, command="create_hive")
                    possible_moves.append(cmd)
        elif bee[0] == "Seed":
            if bee[1:3] in next_to_hives or next_to_hives == []:
                cmd = dict(entity=bee_id, command="flower")
                possible_moves.append(cmd)
            if [bee[1:3], bee[3]] in doomed_pairs:
                pass
            elif about_to_leave(bee[1:3], bee[3]):
                cmd = dict(entity=bee_id, command=saver_new_heading(bee[1:3], bee[3]))
                possible_moves.append(cmd)
            else:
                for new_heading in new_headings[bee[3]]:
                    cmd = dict(entity=bee_id, command=new_heading)
                    possible_moves.append(cmd)
        else:
            if bee[0] == "TrapSeed" and ((bee[4] == 0) or (bee[1:3] in trap_locations)):
                cmd = dict(entity=bee_id, command="flower")
                possible_moves.append(cmd)
            if [bee[1:3], bee[3]] in doomed_pairs:
                pass
            elif about_to_leave(bee[1:3], bee[3]):
                cmd = dict(entity=bee_id, command=saver_new_heading(bee[1:3], bee[3]))
                possible_moves.append(cmd)
            else:
                for new_heading in new_headings[bee[3]]:
                    cmd = dict(entity=bee_id, command=new_heading)
                    possible_moves.append(cmd)
    return possible_moves

def copy_board(board_state):
    return {
        "hives": [copy(h) for h in board_state["hives"]],
        "deadbees": board_state["deadbees"],
        "flowers": [copy(f) for f in board_state["flowers"]],
        "inflight": {k: copy(v) for k, v in board_state["inflight"].items()}}

def apply_command(board_state, cmd, turn_num):
    if cmd is not None:
        cmd_volant_id, cmd_heading = cmd['entity'], cmd['command']

        cmd_volant = board_state["inflight"][cmd_volant_id]

        if cmd_volant[0] == "Seed" and cmd_heading == "flower":
            # If there is already a hive or a flower on this tile remove it
            board_state["hives"] = [h for h in board_state["hives"] if h[:2] != cmd_volant[1:3]]
            board_state["flowers"] = [f for f in board_state["flowers"] if f[:2] != cmd_volant[1:3]]
            # Add new flower
            board_state["flowers"].append(cmd_volant[1:3] + [1, 0, turn_num+300, "Flower"])
            del board_state["inflight"][cmd_volant_id]
        if cmd_volant[0] == "TrapSeed" and cmd_heading == "flower":
            # If there is already a hive or a flower on this tile remove it
            board_state["hives"] = [h for h in board_state["hives"] if h[:2] != cmd_volant[1:3]]
            board_state["flowers"] = [f for f in board_state["flowers"] if f[:2] != cmd_volant[1:3]]
            # Add new flower
            board_state["flowers"].append(cmd_volant[1:3] + [1, 0, turn_num+300, "VenusBeeTrap"])
            del board_state["inflight"][cmd_volant_id]
        elif cmd_volant[0] == "QueenBee" and 'create_hive' == cmd_heading:
            # If there is a flower on this tile remove it
            board_state["flowers"] = [f for f in board_state["flowers"] if f[:2] != cmd_volant[1:3]]
            board_state["hives"] = [h for h in board_state["hives"] if h[:2] != cmd_volant[1:3]] + [cmd_volant[1:3] + [cmd_volant[5]]]
            del board_state["inflight"][cmd_volant_id]
        else:
            cmd_volant[3] = cmd_heading

def remove_dead_flowers(board_state, turn_num):
    unexpired_flowers = [f for f in board_state["flowers"] if f[4] > turn_num and f[5] == "Flower"]
    unexpired_traps = [f for f in board_state["flowers"] if f[4] > turn_num and f[5] == "VenusBeeTrap"]

    # If there are no flowers left on the board we need to keep at least one!
    if unexpired_flowers:
        board_state["flowers"] = unexpired_flowers + unexpired_traps
    elif board_state["flowers"]:
        board_state["flowers"] = board_state["flowers"][:1] + unexpired_traps

def move_volants(board_state):
    for volant_id, volant in board_state["inflight"].items():
        dx, dy = heading_to_delta(volant[3], (volant[1]+1)%2)
        volant[1] += dx
        volant[2] += dy
        if volant[0] in ["Bee", "QueenBee"]:
            volant[4] -= 1 if volant[5] < 5 else 2
        elif volant[0] == "TrapSeed":
            volant[4] -= 1
def send_volants(board_state):
    board_state["inflight"] = {k: v for k, v in board_state["inflight"].items()
                                if not ((v[1] // 8) or (v[2] // 8))}

def visit_flowers(board_state):
    flowers = {10*flower[0] + flower[1]: flower for flower in board_state["flowers"] if flower[5] == "Flower"}

    vists = {bee_id: flowers[10*bee[1] + bee[2]] for bee_id, bee in board_state["inflight"].items()
             if bee[0] in ["Bee", "QueenBee"] and 10*bee[1] +bee[2] in flowers}

    for bee_id, flower in vists.items():
        board_state["inflight"][bee_id][5] = min(5, board_state["inflight"][bee_id][5] + flower[2])
        board_state["inflight"][bee_id][4] += 25*flower[2]
        flower[3] += 1
        flower[2] = min(3, flower[3]//10 + 1)
        flower[4] += 10

def turn_trap_seeds_to_venus(board_state, turn_num):
    make_flowers = [volant_id for volant_id, volant in board_state["inflight"].items()
                         if volant[0] == "TrapSeed" and volant[4] < 0]
    for volant_id in make_flowers:
        apply_command(board_state, dict(entity=volant_id, command="flower"), turn_num)

def land_bees(board_state):
    hives = {(hive[0], hive[1]): hive for hive in board_state["hives"]}

    landed = {bee_id: hives[(bee[1], bee[2])] for bee_id, bee in board_state["inflight"].items()
              if bee[0] in ["Bee", "QueenBee"] and (bee[1], bee[2]) in hives}

    for bee_id, hive in landed.items():
        inflight_volant = board_state["inflight"][bee_id]
        if inflight_volant[0] == "QueenBee":
            board_state["deadbees"] += 1
        else:
            hive[2] += board_state["inflight"][bee_id][5]
        del board_state["inflight"][bee_id]

def detect_crashes(board_state):
    pos_head = {}
    for volant_id, volant in board_state["inflight"].items():
        if volant[0] in ["Bee", "QueenBee"]:
            volant_coords = 10*volant[1] + volant[2]
            if volant_coords in pos_head:
                pos_head[volant_coords].append(volant[3])
            else:
                pos_head[volant_coords] = [volant[3]]
    bee_occupied = {}
    seed_occupied = {}
    headons = []
    exhausted = []
    for volant_id, volant in board_state["inflight"].items():
        volant_coords = 10*volant[1] + volant[2]
        if volant[0] in ["Seed", "TrapSeed"]:
            if volant_coords in seed_occupied:
                seed_occupied[volant_coords].append(volant_id)
            else:
                seed_occupied[volant_coords] = [volant_id]
        else:
            if volant[4] < 0:
                exhausted.append(volant_id)
            if volant_coords in bee_occupied:
                bee_occupied[volant_coords].append(volant_id)
            else:
                bee_occupied[volant_coords] = [volant_id]
            if volant[3] in [0, 180]:
                dx, dy = heading_to_delta(volant[3], (volant[1]+1)%2)
            else:
                dx, dy = heading_to_delta(volant[3], (volant[1])%2)
            new_volant_coords = 10*(volant[1] - dx) + volant[2] - dy
            if new_volant_coords in pos_head:
                if op_headings[volant[3]] in pos_head[new_volant_coords]:
                    headons.append(volant_id)
    traps = [10*f[0]+f[1] for f in board_state["flowers"] if f[5] == "VenusBeeTrap"]
    gobbled = [v_id for v_id, v in board_state["inflight"].items() if v[0] in ["Bee", "QueenBee"] and 10*v[1]+v[2] in traps]
    for bee_id in gobbled:
        del board_state["inflight"][bee_id]
        board_state["deadbees"] += 1
    for _, bee_ids in bee_occupied.items():
        if len(bee_ids) > 1:
            for bee_id in bee_ids:
                if bee_id in board_state["inflight"]:
                    del board_state["inflight"][bee_id]
                    board_state["deadbees"] += 1
    for _, seed_ids in seed_occupied.items():
        if len(seed_ids) > 1:
            for seed_id in seed_ids:
                del board_state["inflight"][seed_id]
    for bee_id in headons:
        if bee_id in board_state["inflight"]:
            del board_state["inflight"][bee_id]
            board_state["deadbees"] += 1
    for bee_id in exhausted:
        if bee_id in board_state["inflight"]:
            del board_state["inflight"][bee_id]
            board_state["deadbees"] += 1

def perform_move(old_board_state, cmd, turn_num):
    board_state = copy_board(old_board_state)
    apply_command(board_state, cmd, turn_num)
    remove_dead_flowers(board_state, turn_num)
    move_volants(board_state)
    send_volants(board_state)
    visit_flowers(board_state)
    turn_trap_seeds_to_venus(board_state, turn_num)
    land_bees(board_state)
    detect_crashes(board_state)
    return board_state

def light_converter(board_json):
    return {"hives": board_json["hives"],
            "flowers": [f[:2]+f[3:] for f in board_json["flowers"]],
            "inflight": {k: (v[:5]+v[6:] if v[0] not in ["Seed", "TrapSeed"] else v) for k, v in board_json["inflight"].items()},
            "deadbees": board_json["deadbees"]}

@algo_player(name="WinningAlgo",
             description="By Matthew Ridley")
def template_algo(board_width, board_height, hives, flowers, inflight, crashed,
                  lost_volants, received_volants, landed, scores, player_id, game_id, turn_num):
    then = perf_counter()
    if inflight:
        board_json = light_converter({"hives": hives,
                                      "flowers": flowers,
                                      "inflight": inflight,
                                      "deadbees": 0})
        score_table = {}
        board_table = {}
        board_hash = (str(board_json["hives"]) +
                              str(board_json["flowers"]) +
                              str(board_json["inflight"]) +
                              str(turn_num))
        if start_game.score_table:
            if board_hash in start_game.score_table:
                score_table = start_game.score_table
            start_game.score_table = None
        if start_game.board_table:
            board_table = start_game.board_table
            start_game.board_table = None
        move_tree = Tree(board_json, turn_num, score_table, board_table)
        if move_tree.head_node.children == []:
            return None
        best_cmd = move_tree.best_cmd()
        # return best_cmd
        while (perf_counter() - then) < TIME_LIMIT:
            move_tree.update()
            best_cmd = move_tree.best_cmd()
        start_game.score_table = move_tree.hash_tab
        start_game.board_table = move_tree.bhash_tab
        return best_cmd
    # Otherwise, do nothing
    return None



@template_algo.on_start_game
def start_game(board_width, board_height, hives, flowers, players, player_id, game_id, game_params):
    start_game.score_table = None
    start_game.board_table = None


@template_algo.on_game_over
def game_over(board_width, board_height, hives, flowers, inflight, crashed,
              lost_volants, received_volants, landed, scores, player_id, game_id, turns):
    """
    Called at the end of the game to inform the algorithm with the result of the final turn

    Parameters
    ----------
    board_width: int
        The number of tiles in each row of the board
    board_height: int
        The number of tiles in each column of the board
    hives: tuple[`Hive`+]
        Hives present on player's board
    flowers: tuple[`Flower`+]
        Flowers present on player's board
    inflight: dict [str, `Volant`]
        A dictionary of volant identifiers to volant
    crashed: dict [str, list[`Volant`]]
        A dictionary of causes to Volants which have been removed
    landed: dict [str, `Bee`]
        A dictionary of `Bee` identifiers to `Bee` which have landed back on a hive and no longer active on the board
    scores: list [int]
        The final scores of each player in the game indexed by the player_id
    player_id: int
        The player id assigned to this algorithm
    game_id: str
        Unique identifier for the game which has ended
    turn_num: int
        Turn number of the final round"""
    pass

