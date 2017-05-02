from hiveminder.game_state import GameState
from mock import Mock, patch, sentinel, call


def test_volants_move_ordering_correct():
    # Ensures all volants are moved and then reassigned to the neighbouring boards
    with patch('hiveminder.game_state.GameState.__init__', side_effect=lambda *args, **kwargs: None):
        gs = GameState(sentinel.game_id, sentinel.boards, sentinel.board_width, sentinel.board_height, sentinel.hives,
                       sentinel.flowers)

    b = Mock()
    b.send_volants.side_effect = [sentinel.b1_s, sentinel.b2_s]
    b.receive_volants.side_effect = [sentinel.b1_r, sentinel.b2_r]

    gs.boards = [b, b]
    sent_volants, received_volants = gs.move_volants()

    b.assert_has_calls([call.send_volants(), call.send_volants(), call.receive_volants(), call.receive_volants()])

    assert sent_volants == [sentinel.b1_s, sentinel.b2_s]
    assert received_volants == [sentinel.b1_r, sentinel.b2_r]
