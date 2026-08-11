"""
Room model for Daberna (Iranian 90-ball Bingo).
Fully independent from other games (per project rule).
Room capacity: 10, 20, or 30 players.
"""

from games.daberna.player import Player

VALID_ROOM_SIZES = [10, 20, 30]


class Room:
    def __init__(self, room_id: str, max_players: int):
        if max_players not in VALID_ROOM_SIZES:
            raise ValueError("max_players must be 10, 20, or 30")
        self.room_id = room_id
        self.max_players = max_players
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

    def all_ready(self) -> bool:
        if len(self.players) < 2:
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
            "current_players": len(self.players),
            "is_full": self.is_full(),
            "is_started": self.is_started,
            "players": [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "is_ready": p.is_ready,
                    "card_count": len(p.cards),
                }
                for p in self.players
            ],
        }
