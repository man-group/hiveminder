from hiveminder import algo_player


@algo_player(name="Template",
             description="Only a basic template")
def template_algo(board_width, board_height, hives, flowers, inflight, crashed,
                  lost_volants, received_volants, landed, scores, player_id, game_id, turn_num):
    """
    This is a simple template from which to start.

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
    lost_volants: dict [str, `Volant`]
        A dictionary of `Volant` identifiers to `Volant` which moved off of an edge of algo's board to another board
    received_volants: dict [str, `Volant`]
        A dictionary of `Volant` identifiers to `Volant` which moved onto algo's board from another board
    landed: dict [str, `Bee`]
        A dictionary of `Bee` identifiers to `Bee` which have landed back on a hive and no longer active on the board
    scores: list [int]
        The scores of each player in the game indexed by the player_id
    player_id: int
        The player id assigned to this algorithm
    game_id: str
        Unique identifier for the current game
    turn_num: int
        Incrementing turn number

    Returns
    -------
    Dictionary of the command (key 'command') the algorithm wants to perform and the volant id (key 'entity') of the
      volent on which the command should be performed
    """
    pass


@template_algo.on_start_game
def start_game(board_width, board_height, hives, flowers, players, player_id, game_id, game_params):
    """
    Called once at the start of the game to inform the algorithm of the starting state of the game

    Parameters
    ----------
    board_width: int
        The number of tiles in each row of the board
    board_height: int
        The number of tiles in each column of the board
    hives: tuple[`Hive`+]
        Hives initially present on player's board
    flowers: tuple[`Flower`+]
        Flowers initially present on player's board
    players: int
        The number of players in the game
    player_id: int
        The player id assigned to this algorithm
    game_id: str
        The unique identifier for the game started by this call
    game_params: namedtuple
        A `namedtuple` of type `hiveminder.game_params.GameParameters` with the fixed parameters for the game,
        such as bee launch probability, score factors, etc."""
    pass


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
