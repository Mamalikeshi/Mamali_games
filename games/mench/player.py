"""
Player model for Mench (Ludo) - supports 2, 3, and 4 players.
Fully independent from other games (per project rule).
"""

from games.mench.piece import Piece

PIECES_PER_PLAYER = 4


class Player:
    def __init__(self, user_id: int, username: str, color: str):
        self.user_id = user_id
        self.username = username
        self.color = color
        self.is_ready: bool = False

        self.pieces: list[Piece] = [
            Piece(piece_id=f"{color}-{i}", color=color)
            for i in range(PIECES_PER_PLAYER)
        ]

    def all_finished(self) -> bool:
        return all(piece.is_finished() for piece in self.pieces)

    def pieces_in_yard(self) -> list[Piece]:
        return [p for p in self.pieces if p.is_in_yard()]

    def get_piece(self, piece_id: str) -> Piece | None:
        for piece in self.pieces:
            if piece.piece_id == piece_id:
                return piece
        return None

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "color": self.color,
            "is_ready": self.is_ready,
            "pieces": [piece.to_dict() for piece in self.pieces],
        }
