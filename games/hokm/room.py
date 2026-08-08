from dataclasses import dataclass, field
from typing import Optional

from .player import Player


MAX_PLAYERS = 2


@dataclass
class Room:
    room_id: str

    players: list[Player] = field(default_factory=list)

    is_started: bool = False

    def add_player(self, player: Player) -> bool:
        if self.is_started:
            return False

        if len(self.players) >= MAX_PLAYERS:
            return False

        if any(p.user_id == player.user_id for p in self.players):
            return False

        self.players.append(player)
        return True

    def remove_player(self, user_id: int) -> bool:
        for index, player in enumerate(self.players):
            if player.user_id == user_id:
                self.players.pop(index)
                return True

        return False

    def get_player(self, user_id: int) -> Optional[Player]:
        for player in self.players:
            if player.user_id == user_id:
                return player

        return None

    def is_full(self) -> bool:
        return len(self.players) == MAX_PLAYERS

    def both_ready(self) -> bool:
        return (
            self.is_full()
            and all(player.is_ready for player in self.players)
        )

    def start(self) -> bool:
        if not self.both_ready():
            return False

        self.is_started = True
        return True

    def reset(self):
        self.is_started = False

        for player in self.players:
            player.reset()

    def player_count(self) -> int:
        return len(self.players)
