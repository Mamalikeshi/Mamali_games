"""
Main game engine for Mench (Ludo).

Responsibilities:
- Starting a Mench game
- Managing turns
- Rolling dice
- Finding legal moves
- Moving pieces
- Entering pieces from the yard
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
)
from games.mench.player import Player
from games.mench.piece import Piece
from games.mench.rules import (
    can_piece_move,
    can_enter_from_yard,
    destination_global_cell,
    is_destination_safe,
    movable_pieces,
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

    def __init__(
        self,
        room_id: str,
    ):
        self.room_id = room_id
        self.state = MenchState(room_id)

    # ========================================================
    # Player management
    # ========================================================

    def add_player(
        self,
        player: Player,
    ) -> None:
        """
        Add a player to the game state.
        """

        if self.state.game_finished:
            raise ValueError(
                "Cannot add player after the game has finished."
            )

        if self.state.player_count() >= self.MAX_PLAYERS:
            raise ValueError(
                "Mench game cannot have more than 4 players."
            )

        self.state.add_player(player)

    def get_player(
        self,
        user_id: int,
    ) -> Player | None:
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

        if self.state.player_count() not in (2, 3, 4):
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

    def current_player(
        self,
    ) -> Player | None:
        """Return the player whose turn it is."""

        return self.state.current_player()

    def is_player_turn(
        self,
        user_id: int,
    ) -> bool:
        """Return True when the given player owns the current turn."""

        return self.state.current_player_id == user_id

    def advance_turn(self) -> None:
        """
        Move to the next player.

        This should only be called when the current player
        does not receive another roll.
        """

        if self.state.game_finished:
            return

        self.state.advance_turn()
        self.state.clear_move_result()

    # ========================================================
    # Dice
    # ========================================================

    @staticmethod
    def _validate_dice(
        dice_value: int,
    ) -> None:
        """Validate a dice value."""

        if not (
            MenchGame.DICE_MIN
            <= dice_value
            <= MenchGame.DICE_MAX
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

        dice_value can be supplied by tests or trusted game
        logic to make the result deterministic.

        In production, leave it as None.
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

        self.state.set_dice(dice_value)

        player = self.get_player(user_id)

        if player is None:
            raise ValueError(
                "Player does not exist."
            )

        legal_pieces = self.get_movable_pieces(
            user_id,
            dice_value,
        )

        if legal_pieces:
            self.state.require_piece_selection()
        else:
            # No legal move.
            #
            # A roll of 6 still gives the player another roll.
            # For other values the turn moves to the next player.
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

        If dice_value is omitted, the currently rolled dice is used.
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

        result: list[Piece] = []

        for piece in player.pieces:
            if can_piece_move(
                piece,
                dice_value,
            ):
                result.append(piece)

        # A piece in the yard can only enter on a 6.
        for piece in player.pieces:
            if piece.is_in_yard():
                if can_enter_from_yard(
                    piece,
                    dice_value,
                ):
                    if piece not in result:
                        result.append(piece)

        return result

    def has_legal_move(
        self,
        user_id: int,
    ) -> bool:
        """Return True if the player has at least one legal move."""

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
        """Validate player turn and find the selected piece."""

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
        """
        Move a yard piece onto its starting track cell.

        The standard Mench/Ludo rule used here is:
        rolling 6 allows a piece to leave the yard.
        """

        piece.status = "track"
        piece.relative_step = 0

    def _move_piece_on_track(
        self,
        piece: Piece,
        dice_value: int,
    ) -> None:
        """Move a piece according to its relative step."""

        destination = piece.relative_step + dice_value

        if destination > FINISH_STEP:
            raise ValueError(
                "Piece cannot move beyond the finish."
            )

        piece.relative_step = destination

        if destination == FINISH_STEP:
            piece.status = "finished"

        elif is_home_column(destination):
            piece.status = "home_column"

        elif is_on_track(destination):
            piece.status = "track"

        else:
            raise ValueError(
                "Invalid piece destination."
            )

    def _move_piece(
        self,
        piece: Piece,
        dice_value: int,
    ) -> None:
        """Apply the actual movement to a piece."""

        if piece.is_in_yard():
            if not can_enter_from_yard(
                piece,
                dice_value,
            ):
                raise ValueError(
                    "This piece cannot leave the yard with this dice value."
                )

            self._move_piece_from_yard(piece)
            return

        self._move_piece_on_track(
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
        track cell.

        Pieces in the home column and finished pieces cannot
        be captured.
        """

        if attacker.status != "track":
            return []

        attacker_cell = global_cell_for_step(
            attacker.color,
            attacker.relative_step,
        )

        if attacker_cell is None:
            return []

        if is_destination_safe(
            attacker.color,
            attacker.relative_step,
        ):
            return []

        captured: list[str] = []

        for player in self.state.players:
            if player.color == attacker.color:
                continue

            for piece in player.pieces:
                if piece.status != "track":
                    continue

                victim_cell = global_cell_for_step(
                    piece.color,
                    piece.relative_step,
                )

                if victim_cell != attacker_cell:
                    continue

                piece.status = "yard"
                piece.relative_step = -1

                captured.append(piece.piece_id)

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

        self.state.clear_move_result()

        self._move_piece(
            piece,
            dice_value,
        )

        captured_piece_ids = self._capture_opponents(
            piece
        )

        destination_cell = None

        if piece.status == "track":
            destination_cell = global_cell_for_step(
                piece.color,
                piece.relative_step,
            )

        elif old_status == "yard" and piece.status == "track":
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
            "captured_pieces": captured_piece_ids.copy(),
            "finished": piece.is_finished(),
            "player_finished": False,
            "extra_turn": dice_value == self.EXTRA_TURN_ROLL,
        }

        self.state.set_last_move(
            move_result
        )
        self.state.set_captured_pieces(
            captured_piece_ids
        )

        # ----------------------------------------------------
        # Check whether this player has finished.
        # ----------------------------------------------------

        if player.all_finished():
            move_result["player_finished"] = True

            if user_id not in self.state.winner_order:
                self.state.winner_order.append(user_id)

        # ----------------------------------------------------
        # Check whether the entire game is finished.
        #
        # For 2 players, the first player finishing wins.
        # For 3/4 players, the game ends when only one player
        # remains unfinished.
        # ----------------------------------------------------

        unfinished_players = [
            p
            for p in self.state.players
            if not p.all_finished()
        ]

        if len(unfinished_players) <= 1:
            self.state.game_finished = True

        # ----------------------------------------------------
        # Six gives an extra roll, provided the game has not
        # finished.
        # ----------------------------------------------------

        if (
            not self.state.game_finished
            and dice_value == self.EXTRA_TURN_ROLL
        ):
            self.state.waiting_for_piece = False
            self.state.dice_rolled = False
            self.state.dice_value = None
            self.state.turn_number += 1

            move_result["next_player_id"] = user_id
            move_result["extra_turn"] = True

            self.state.set_last_move(
                move_result
            )

            return move_result

        # ----------------------------------------------------
        # Normal turn ends here.
        # ----------------------------------------------------

        self.state.waiting_for_piece = False

        if not self.state.game_finished:
            self.advance_turn()
            move_result["next_player_id"] = (
                self.state.current_player_id
            )
        else:
            move_result["next_player_id"] = None

        self.state.set_last_move(
            move_result
        )

        return move_result

    # ========================================================
    # No-legal-move handling
    # ========================================================

    def finish_roll_without_move(
        self,
        user_id: int,
    ) -> dict:
        """
        Finish a turn when the player has no legal move.

        A roll of 6 gives another roll.
        Other dice values move the turn to the next player.
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

        self.state.waiting_for_piece = False

        result = {
            "user_id": user_id,
            "dice_value": dice_value,
            "moved": False,
            "extra_turn": dice_value == self.EXTRA_TURN_ROLL,
            "next_player_id": user_id,
        }

        if dice_value == self.EXTRA_TURN_ROLL:
            self.state.dice_value = None
            self.state.dice_rolled = False
            self.state.waiting_for_piece = False

            self.state.turn_number += 1

            self.state.set_last_move(result)

            return result

        self.advance_turn()

        result["next_player_id"] = (
            self.state.current_player_id
        )

        self.state.set_last_move(result)

        return result

    # ========================================================
    # Game completion
    # ========================================================

    def is_finished(self) -> bool:
        """Return True when the game is finished."""

        return self.state.game_finished

    def winner(self) -> Player | None:
        """Return the winner when the game is finished."""

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
