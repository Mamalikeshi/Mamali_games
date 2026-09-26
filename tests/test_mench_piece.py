from games.mench.piece import Piece


def test_piece_starts_in_yard():
    piece = Piece("red-0", "red")

    assert piece.is_in_yard()
    assert not piece.is_on_track()
    assert not piece.is_in_home_column()
    assert not piece.is_finished()
    assert piece.relative_step == -1


def test_piece_enters_board():
    piece = Piece("red-0", "red")

    piece.enter_board()

    assert piece.is_on_track()
    assert piece.relative_step == 0
    assert piece.status == "track"


def test_piece_moves_on_track():
    piece = Piece("red-0", "red")

    piece.move_to_track(25)

    assert piece.is_on_track()
    assert piece.relative_step == 25


def test_piece_moves_to_home_column():
    piece = Piece("red-0", "red")

    piece.move_to_home_column(52)

    assert piece.is_in_home_column()
    assert piece.relative_step == 52


def test_piece_finishes():
    piece = Piece("red-0", "red")

    piece.finish()

    assert piece.is_finished()
    assert piece.relative_step == 57
    assert piece.status == "finished"


def test_captured_piece_returns_to_yard():
    piece = Piece("red-0", "red")

    piece.move_to_track(20)
    assert piece.is_on_track()

    piece.send_home()

    assert piece.is_in_yard()
    assert piece.relative_step == -1
    assert piece.status == "yard"


def test_piece_to_dict():
    piece = Piece("red-0", "red")

    data = piece.to_dict()

    assert data == {
        "piece_id": "red-0",
        "color": "red",
        "status": "yard",
        "relative_step": -1,
    }
