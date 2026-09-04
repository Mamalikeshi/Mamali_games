"""
Game state model for Mench (Ludo).

State is responsible only for storing the current game state.

Game rules belong to rules.py.
Game flow belongs to game.py.
Room management belongs to room.py.
"""

from __future__ import annotations

from games.mench.player import Player


class MenchState:
    """
    Complete runtime state of a Mench game.
    """

    def __init__(
        self,
        room_id: str,
    ):
        self.room_id = room_id

        # Players in turn order.
        self.players: list[Player] = []

        # Index of the player whose turn it currently is.
        self.current_player_index: int = 0

        # User ID of current player.
        self.current_player_id: int | None = None

        # Last dice result.
        self.dice_value: int | None = None

        # Whether the current player has already rolled.
        self.dice_rolled: bool = False

        # Whether the current player must choose a piece.
        self.waiting_for_piece: bool = False

        # Number of completed turns.
        self.turn_number: int = 0

        # Last movement information.
        self.last_move: dict | None = None

        # Pieces captured by the last movement.
        self.last_captured_pieces: list[str] = []

        # Whether the game has finished.
        self.game_finished: bool = False

        # Winner's user ID.
        self.winner_id: int | None = None

    # ========================================================
    # Player management
    # ========================================================

    def add_player(self, player: Player) -> None:
        """Add a player to the state."""
        if any(
            existing.user_id == player.user_id
            for existing in self.players
        ):
            raise ValueError(
                "Player already exists in Mench state."
            )

        self.players.append(player)

        if len(self.players) == 1:
            self.current_player_index = 0
            self.current_player_id = player.user_id

    def get_player(
        self,
        user_id: int,
    ) -> Player | None:
        """Return a player by user ID."""
        for player in self.players:
            if player.user_id == user_id:
                return player

        return None

    def current_player(self) -> Player | None:
        """Return the player whose turn it is."""
        if not self.players:
            return None

        if not (
            0 <= self.current_player_index < len(self.players)
        ):
            return None

        return self.players[
            self.current_player_index
        ]

    # ========================================================
    # Turn management
    # ========================================================

    def set_current_player(
        self,
        user_id: int,
    ) -> None:
        """Set the current player by user ID."""

        for index, player in enumerate(self.players):
            if player.user_id == user_id:
                self.current_player_index = index
                self.current_player_id = user_id
                return

        raise ValueError(
            "Player does not exist in Mench state."
        )

    def advance_turn(self) -> None:
        """
        Move the turn to the next player.

        This method only changes state.
        Decisions about whether the player gets another turn
        belong to game.py.
        """

        if not self.players:
            raise ValueError(
                "Cannot advance turn without players."
            )

        self.current_player_index = (
            self.current_player_index + 1
        ) % len(self.players)

        self.current_player_id = (
            self.players[
                self.current_player_index
            ].user_id
        )

        self.turn_number += 1

        self.reset_dice_state()

    # ========================================================
    # Dice state
    # ========================================================

    def set_dice(
        self,
        dice_value: int,
    ) -> None:
        """Store the latest dice value."""

        if not 1 <= dice_value <= 6:
            raise ValueError(
                "Dice value must be between 1 and 6."
            )

        self.dice_value = dice_value
        self.dice_rolled = True
        self.waiting_for_piece = False

    def require_piece_selection(self) -> None:
        """Mark that a piece must now be selected."""
        if not self.dice_rolled:
            raise ValueError(
                "Dice has not been rolled."
            )

        self.waiting_for_piece = True

    def reset_dice_state(self) -> None:
        """Clear the current turn's dice-selection state."""
        self.dice_value = None
        self.dice_rolled = False
        self.waiting_for_piece = False

    # ========================================================
    # Move state
    # ========================================================

    def set_last_move(
        self,
        move: dict,
    ) -> None:
        """Store information about the last move."""
        self.last_move = move

    def set_captured_pieces(
        self,
        piece_ids: list[str],
    ) -> None:
        """Store IDs of pieces captured by the last move."""
        self.last_captured_pieces = piece_ids.copy()

    def clear_move_result(self) -> None:
        """Clear the previous move result."""
        self.last_move = None
        self.last_captured_pieces = []

    # ========================================================
    # Game completion
    # ========================================================

    def set_winner(
        self,
        user_id: int,
    ) -> None:
        """Mark the game as finished and set its winner."""

        if self.get_player(user_id) is None:
            raise ValueError(
                "Winner must be a player in the game."
            )

        self.game_finished = True
        self.winner_id = user_id
        self.waiting_for_piece = False

    # ========================================================
    # State helpers
    # ========================================================

    def player_count(self) -> int:
        """Return the number of players."""
        return len(self.players)

    def is_ready_to_start(self) -> bool:
        """
        Return True when there are 2, 3, or 4 players and all
        players are ready.
        """

        if len(self.players) not in (2, 3, 4):
            return False

        return all(
            player.is_ready
            for player in self.players
        )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> dict:
        """Serialize the complete state."""

        current_player = self.current_player()

        return {
            "room_id": self.room_id,
            "players": [
                player.to_dict()
                for player in self.players
            ],
            "current_player_index": (
                self.current_player_index
            ),
            "current_player_id": (
                self.current_player_id
            ),
            "current_player": (
                current_player.to_dict()
                if current_player is not None
                else None
            ),
            "dice_value": self.dice_value,
            "dice_rolled": self.dice_rolled,
            "waiting_for_piece": (
                self.waiting_for_piece
            ),
            "turn_number": self.turn_number,
            "last_move": self.last_move,
            "last_captured_pieces": (
                self.last_captured_pieces.copy()
            ),
            "game_finished": self.game_finished,
            "winner_id": self.winner_id,
        }
