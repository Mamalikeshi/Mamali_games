"""
Room model for Mench (Ludo).

Room responsibilities:
- Managing players
- Assigning colors
- Checking readiness
- Starting the game
- Connecting the room to MenchGame

Game rules belong to rules.py.
Game flow belongs to game.py.
Runtime state belongs to state.py.
"""

from __future__ import annotations

from games.mench.board import MODE_COLORS
from games.mench.game import MenchGame
from games.mench.player import Player


VALID_PLAYER_COUNTS = [2, 3, 4]


class Room:
    """
    Mench room.

    Supports:
    - 2 players
    - 3 players
    - 4 players
    """

    def __init__(
        self,
        room_id: str,
        max_players: int,
    ):
        if max_players not in VALID_PLAYER_COUNTS:
            raise ValueError(
                "max_players must be 2, 3, or 4"
            )

        self.room_id = room_id
        self.max_players = max_players

        self.players: list[Player] = []

        self.is_started: bool = False

        # Created when the room successfully starts.
        self.game: MenchGame | None = None

    # ========================================================
    # Player management
    # ========================================================

    def add_player(
        self,
        user_id: int,
        username: str,
    ) -> Player | None:
        """
        Add a player to the room.

        Returns:
        - Player when successful
        - None when the player cannot be added
        """

        if self.is_started:
            return None

        if self.is_full():
            return None

        if self.get_player(user_id) is not None:
            return None

        available_colors = MODE_COLORS[
            self.max_players
        ]

        used_colors = {
            player.color
            for player in self.players
        }

        next_color = None

        for color in available_colors:
            if color not in used_colors:
                next_color = color
                break

        if next_color is None:
            return None

        player = Player(
            user_id=user_id,
            username=username,
            color=next_color,
        )

        self.players.append(player)

        return player

    def get_player(
        self,
        user_id: int,
    ) -> Player | None:
        """Return a player by user ID."""

        for player in self.players:
            if player.user_id == user_id:
                return player

        return None

    def is_full(self) -> bool:
        """Return True when the room has reached its capacity."""

        return len(self.players) >= self.max_players

    # ========================================================
    # Readiness
    # ========================================================

    def all_ready(self) -> bool:
        """
        Return True when:
        - the room is full
        - every player is ready
        """

        if not self.is_full():
            return False

        return all(
            player.is_ready
            for player in self.players
        )

    # ========================================================
    # Game start
    # ========================================================

    def start(self) -> bool:
        """
        Start the Mench game.

        The same Player objects from the room are added to
        MenchGame, so player/game state stays synchronized.
        """

        if self.is_started:
            return False

        if not self.all_ready():
            return False

        game = MenchGame(
            room_id=self.room_id
        )

        for player in self.players:
            game.add_player(player)

        game.start()

        self.game = game
        self.is_started = True

        return True

    # ========================================================
    # Game access
    # ========================================================

    def get_game(self) -> MenchGame | None:
        """Return the active game, if one exists."""

        return self.game

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> dict:
        """Serialize the room."""

        return {
            "room_id": self.room_id,
            "max_players": self.max_players,
            "is_full": self.is_full(),
            "is_started": self.is_started,
            "players": [
                player.to_dict()
                for player in self.players
            ],
            "game": (
                self.game.to_dict()
                if self.game is not None
                else None
            ),
        }
