"""
Room model for Noghte Khat (Dots and Boxes) - 2 player mode.
Fully independent from other games (per project rule).
"""

from games.noghte_khat.player import Player

MAX_PLAYERS = 2


class Room:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.max_players = MAX_PLAYERS
        self.players: list[Player] = []
        self.is_started: bool = False

    def add_player(self, user_id: int, username: str) -> Player | None:
        if self.is_full():
            return None
        if self.get_player(user_id) is not None:
            return None
        player = Player(user_id=user_id, username=username)
        self.players.append(player)
        return player

    def get_player(self, user_id: int) -> Player | None:
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None

    def is_full(self) -> bool:
        return len(self.players) >= self.max_players

    def both_ready(self) -> bool:
        if not self.is_full():
            return False
        return all(player.is_ready for player in self.players)

    def start(self) -> bool:
        if not self.both_ready():
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
