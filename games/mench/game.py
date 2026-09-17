"""
Main game engine for Mench (Ludo).

Responsibilities:
- Starting a Mench game
- Managing turns
- Rolling dice
- Finding legal moves
- Moving pieces
- Entering pieces from the yard
- Moving through the home column
- Finishing pieces
- Capturing opponent pieces
- Handling extra turns after rolling 6
- Detecting finished players
- Detecting game completion
- Exposing the current game state

Game rules belong to rules.py.
State storage belongs to state.py.
Room management belongs to room.py.
"""

from __future__ import annotations

import random

from games.mench.board import (
    FINISH_STEP,
    global_cell_for_step,
    is_home_column,
    is_on_track,
    is_safe_track_cell,
)
from games.mench.piece import Piece
from games.mench.player import Player
from games.mench.rules import (
    can_enter_from_yard,
    can_piece_move,
    destination_global_cell,
    is_destination_safe,
)
from games.mench.state import MenchState


class MenchGame:
    """
    Main runtime engine for Mench.

    Supports:
    - 2 players
    - 3 players
    - 4 players
    """

    MIN_PLAYERS = 2
    MAX_PLAYERS = 4

    DICE_MIN = 1
    DICE_MAX = 6

    EXTRA_TURN_ROLL = 6

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.state = MenchState(room_id)

    # ========================================================
    # Player management
    # ========================================================

    def add_player(self, player: Player) -> None:
        """Add a player to the game."""

        if self.state.game_finished:
            raise ValueError(
                "Cannot add player after the game has finished."
            )

        if self.state.player_count() >= self.MAX_PLAYERS:
            raise ValueError(
                "Mench game cannot have more than 4 players."
            )

        self.state.add_player(player)

    def get_player(self, user_id: int) -> Player | None:
        """Return a player by user ID."""

        return self.state.get_player(user_id)

    # ========================================================
    # Game start
    # ========================================================

    def start(self) -> None:
        """
        Start the game.

        Requirements:
        - 2, 3 or 4 players
        - all players ready
        """

        if self.state.game_finished:
            raise ValueError(
                "Game has already finished."
            )

        player_count = self.state.player_count()

        if player_count not in (2, 3, 4):
            raise ValueError(
                "Mench requires 2, 3, or 4 players."
            )

        if not self.state.is_ready_to_start():
            raise ValueError(
                "All players must be ready before starting."
            )

        first_player = self.state.current_player()

        if first_player is None:
            raise ValueError(
                "Cannot start Mench without a current player."
            )

        self.state.set_current_player(
            first_player.user_id
        )

        self.state.reset_dice_state()
        self.state.clear_move_result()

    # ========================================================
    # Turn helpers
    # ========================================================

    def current_player(self) -> Player | None:
        """Return the player whose turn it is."""

        return self.state.current_player()

    def is_player_turn(self, user_id: int) -> bool:
        """Return True when user owns the current turn."""

        return self.state.current_player_id == user_id

    def advance_turn(self) -> None:
        """
        Move to the next player.

        Does nothing when the game has already finished.
        """

        if self.state.game_finished:
            return

        self.state.advance_turn()
        self.state.clear_move_result()

    # ========================================================
    # Dice
    # ========================================================

    @classmethod
    def _validate_dice(cls, dice_value: int) -> None:
        """Validate a dice value."""

        if not isinstance(dice_value, int):
            raise ValueError(
                "Dice value must be an integer."
            )

        if not (
            cls.DICE_MIN
            <= dice_value
            <= cls.DICE_MAX
        ):
            raise ValueError(
                "Dice value must be between 1 and 6."
            )

    def roll_dice(
        self,
        user_id: int,
        dice_value: int | None = None,
    ) -> int:
        """
        Roll the dice.

        dice_value may be supplied by tests for deterministic
        gameplay.

        In production, leave dice_value as None.
        """

        if self.state.game_finished:
            raise ValueError(
                "Cannot roll dice after game has finished."
            )

        if not self.is_player_turn(user_id):
            raise ValueError(
                "It is not this player's turn."
            )

        if self.state.dice_rolled:
            raise ValueError(
                "Dice has already been rolled for this turn."
            )

        if dice_value is None:
            dice_value = random.randint(
                self.DICE_MIN,
                self.DICE_MAX,
            )

        self._validate_dice(dice_value)

        player = self.get_player(user_id)

        if player is None:
            raise ValueError(
                "Player does not exist."
            )

        self.state.set_dice(dice_value)

        legal_pieces = self.get_movable_pieces(
            user_id,
            dice_value,
        )

        if legal_pieces:
            self.state.require_piece_selection()
        else:
            self.state.waiting_for_piece = False

        return dice_value

    # ========================================================
    # Legal moves
    # ========================================================

    def get_movable_pieces(
        self,
        user_id: int,
        dice_value: int | None = None,
    ) -> list[Piece]:
        """
        Return all pieces that can legally move.
        """

        player = self.get_player(user_id)

        if player is None:
            raise ValueError(
                "Player does not exist."
            )

        if dice_value is None:
            dice_value = self.state.dice_value

        if dice_value is None:
            raise ValueError(
                "Dice has not been rolled."
            )

        self._validate_dice(dice_value)

        return [
            piece
            for piece in player.pieces
            if can_piece_move(
                piece,
                dice_value,
            )
        ]

    def has_legal_move(
        self,
        user_id: int,
    ) -> bool:
        """Return True when at least one piece can move."""

        if self.state.dice_value is None:
            return False

        return bool(
            self.get_movable_pieces(
                user_id,
                self.state.dice_value,
            )
        )

    # ========================================================
    # Piece movement
    # ========================================================

    def _get_current_piece(
        self,
        user_id: int,
        piece_id: str,
    ) -> tuple[Player, Piece]:
        """Validate turn and return selected piece."""

        if self.state.game_finished:
            raise ValueError(
                "Game has finished."
            )

        if not self.is_player_turn(user_id):
            raise ValueError(
                "It is not this player's turn."
            )

        player = self.get_player(user_id)

        if player is None:
            raise ValueError(
                "Player does not exist."
            )

        piece = player.get_piece(piece_id)

        if piece is None:
            raise ValueError(
                "Piece does not belong to this player."
            )

        return player, piece

    def _move_piece_from_yard(
        self,
        piece: Piece,
    ) -> None:
        """Move a yard piece onto its starting cell."""

        piece.enter_board()

    def _move_piece_on_board(
        self,
        piece: Piece,
        dice_value: int,
    ) -> None:
        """Move an already-entered piece."""

        destination = (
            piece.relative_step
            + dice_value
        )

        if destination > FINISH_STEP:
            raise ValueError(
                "Piece cannot move beyond the finish."
            )

        if destination == FINISH_STEP:
            piece.finish()
            return

        if is_home_column(destination):
            piece.move_to_home_column(
                destination
            )
            return

        if is_on_track(destination):
            piece.move_to_track(
                destination
            )
            return

        raise ValueError(
            "Invalid piece destination."
        )

    def _move_piece(
        self,
        piece: Piece,
        dice_value: int,
    ) -> None:
        """Apply actual movement to a piece."""

        if not can_piece_move(
            piece,
            dice_value,
        ):
            raise ValueError(
                "This piece cannot move with this dice value."
            )

        if piece.is_in_yard():
            piece.enter_board()
            return

        self._move_piece_on_board(
            piece,
            dice_value,
        )

    # ========================================================
    # Capturing
    # ========================================================

    def _capture_opponents(
        self,
        attacker: Piece,
    ) -> list[str]:
        """
        Capture opponent pieces occupying the same unsafe
        shared-track cell.
        """

        if not attacker.is_on_track():
            return []

        attacker_cell = global_cell_for_step(
            attacker.color,
            attacker.relative_step,
        )

        if attacker_cell is None:
            return []

        if is_safe_track_cell(attacker_cell):
            return []

        captured: list[str] = []

        for player in self.state.players:

            if player.color == attacker.color:
                continue

            for victim in player.pieces:

                if not victim.is_on_track():
                    continue

                victim_cell = global_cell_for_step(
                    victim.color,
                    victim.relative_step,
                )

                if victim_cell != attacker_cell:
                    continue

                victim.send_home()

                captured.append(
                    victim.piece_id
                )

        return captured

    # ========================================================
    # Move API
    # ========================================================

    def move_piece(
        self,
        user_id: int,
        piece_id: str,
    ) -> dict:
        """
        Move one selected piece.

        Returns a complete movement result.
        """

        player, piece = self._get_current_piece(
            user_id,
            piece_id,
        )

        if not self.state.dice_rolled:
            raise ValueError(
                "Dice has not been rolled."
            )

        dice_value = self.state.dice_value

        if dice_value is None:
            raise ValueError(
                "Dice value is missing."
            )

        legal_pieces = self.get_movable_pieces(
            user_id,
            dice_value,
        )

        if piece not in legal_pieces:
            raise ValueError(
                "Selected piece cannot move with this dice value."
            )

        old_status = piece.status
        old_step = piece.relative_step

        destination_cell = destination_global_cell(
            piece,
            dice_value,
        )

        destination_safe = is_destination_safe(
            piece,
            dice_value,
        )

        self.state.clear_move_result()

        self._move_piece(
            piece,
            dice_value,
        )

        captured_piece_ids = self._capture_opponents(
            piece
        )

        # If the piece entered the board from yard,
        # its destination is its starting global cell.
        if (
            destination_cell is None
            and piece.is_on_track()
        ):
            destination_cell = global_cell_for_step(
                piece.color,
                piece.relative_step,
            )

        move_result = {
            "user_id": user_id,
            "piece_id": piece.piece_id,
            "dice_value": dice_value,

            "old_status": old_status,
            "old_relative_step": old_step,

            "new_status": piece.status,
            "new_relative_step": piece.relative_step,

            "destination_global_cell": destination_cell,

            "destination_safe": destination_safe,

            "captured_pieces": captured_piece_ids.copy(),

            "finished": piece.is_finished(),

            "player_finished": False,

            "extra_turn": (
                dice_value == self.EXTRA_TURN_ROLL
            ),

            "next_player_id": None,
        }

        self.state.set_captured_pieces(
            captured_piece_ids
        )

        # ====================================================
        # Check player completion
        # ====================================================

        if player.all_finished():

            move_result["player_finished"] = True

            if user_id not in self.state.winner_order:
                self.state.winner_order.append(
                    user_id
                )

        # ====================================================
        # Check game completion
        # ====================================================

        unfinished_players = [
            p
            for p in self.state.players
            if not p.all_finished()
        ]

        if len(unfinished_players) <= 1:

            self.state.game_finished = True

            if self.state.winner_order:
                self.state.winner_id = (
                    self.state.winner_order[0]
                )

        # ====================================================
        # Extra turn after six
        # ====================================================

        if (
            not self.state.game_finished
            and dice_value == self.EXTRA_TURN_ROLL
        ):
            self.state.dice_value = None
            self.state.dice_rolled = False
            self.state.waiting_for_piece = False

            self.state.turn_number += 1

            move_result["extra_turn"] = True
            move_result["next_player_id"] = user_id

            self.state.set_last_move(
                move_result
            )

            return move_result

        # ====================================================
        # Normal turn
        # ====================================================

        self.state.waiting_for_piece = False

        if not self.state.game_finished:

            self.advance_turn()

            move_result["next_player_id"] = (
                self.state.current_player_id
            )

        self.state.set_last_move(
            move_result
        )

        return move_result

    # ========================================================
    # No legal move
    # ========================================================

    def finish_roll_without_move(
        self,
        user_id: int,
    ) -> dict:
        """
        Finish a roll when no legal piece exists.

        Roll 6:
            same player receives another roll.

        Other values:
            turn moves to next player.
        """

        if self.state.game_finished:
            raise ValueError(
                "Game has finished."
            )

        if not self.is_player_turn(user_id):
            raise ValueError(
                "It is not this player's turn."
            )

        if not self.state.dice_rolled:
            raise ValueError(
                "Dice has not been rolled."
            )

        dice_value = self.state.dice_value

        if dice_value is None:
            raise ValueError(
                "Dice value is missing."
            )

        if self.has_legal_move(user_id):
            raise ValueError(
                "Player still has a legal move."
            )

        result = {
            "user_id": user_id,
            "dice_value": dice_value,
            "moved": False,
            "extra_turn": (
                dice_value == self.EXTRA_TURN_ROLL
            ),
            "next_player_id": user_id,
        }

        self.state.waiting_for_piece = False

        # ====================================================
        # Six = extra roll
        # ====================================================

        if dice_value == self.EXTRA_TURN_ROLL:

            self.state.dice_value = None
            self.state.dice_rolled = False

            self.state.turn_number += 1

            self.state.set_last_move(
                result
            )

            return result

        # ====================================================
        # Normal next player
        # ====================================================

        self.advance_turn()

        result["next_player_id"] = (
            self.state.current_player_id
        )

        self.state.set_last_move(
            result
        )

        return result

    # ========================================================
    # Game completion
    # ========================================================

    def is_finished(self) -> bool:
        """Return True when the game is finished."""

        return self.state.game_finished

    def winner(self) -> Player | None:
        """Return the first player who finished."""

        winner_id = self.state.winner_id

        if winner_id is None:
            if not self.state.winner_order:
                return None

            winner_id = self.state.winner_order[0]

        return self.get_player(winner_id)

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> dict:
        """Return the complete game state."""

        return self.state.to_dict()
