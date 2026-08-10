"""
Room model for Mench (Ludo) - supports 2, 3, and 4 players.
Fully independent from other games (per project rule).
"""

from games.mench.player import Player
from games.mench.board import MODE_COLORS

VALID_PLAYER_COUNTS = [2, 3, 4]


class Room:
    def __init__(self, room_id: str, max_players: int):
        if max_players not in VALID_PLAYER_COUNTS:
            raise ValueError("max_players must be 2, 3, or 4")
        self.room_id = room_id
        self.max_players = max_players
        self.players: list[Player] = []
        self.is_started: bool = False

    def add_player(self, user_id: int, username: str) -> Player | None:
        if self.is_full():
            return None
        if self.get_player(user_id) is not None:
            return None

        available_colors = MODE_COLORS[self.max_players]
        used_colors = {p.color for p in self.players}
        next_color = None
        for color in available_colors:
            if color not in used_colors:
                next_color = color
                break
        if next_color is None:
            return None

        player = Player(user_id=user_id, username=username, color=next_color)
        self.players.append(player)
        return player

    def get_player(self, user_id: int) -> Player | None:
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None

    def is_full(self) -> bool:
        return len(self.players) >= self.max_players

    def all_ready(self) -> bool:
        if not self.is_full():
            return False
        return all(player.is_ready for player in self.players)

    def start(self) -> bool:
        if not self.all_ready():
            return False
        self.is_started = True
        return True

    def to_dict(self) -> dict:
        return {
            "room_id": self.room_id,
            "max_players": self.max_players,
            "is_full": self.is_full(),
            "is_started": self.is_started,
            "players": [player.to_dict() for player in self.players],
        }
