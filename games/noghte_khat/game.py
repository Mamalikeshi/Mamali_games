"""
Main game engine for Noghte Khat (Dots and Boxes) - 2 player mode, 5x5 boxes.
Fully independent from other games (per project rule).

قوانین کلی:
- بازیکنان به‌نوبت یه خط (افقی یا عمودی) می‌کشن.
- اگه کشیدن یه خط باعث بشه یک یا دو خونه کامل بشه، اون خونه(ها) مال همون
  بازیکنه و بازیکن دوباره نوبتشه (باید یه خط دیگه بکشه).
- اگه خط کشیده‌شده هیچ خونه‌ای رو کامل نکنه، نوبت میره به نفر بعدی.
- وقتی همه‌ی خط‌ها کشیده بشن (۲۵ خونه پر بشه)، بازی تموم می‌شه.
- برنده کسی‌ست که خونه‌ی بیشتری گرفته باشه؛ در صورت تساوی، هیچ‌کس برنده
  نیست (هر دو بازنده حساب می‌شن).
"""

import random

from games.noghte_khat.room import Room
from games.noghte_khat.player import Player
from games.noghte_khat.state import NoghteKhatState
from games.noghte_khat.board import (
    is_valid_line_id,
    all_box_coords,
    box_sides,
)


class NoghteKhatGame:
    def __init__(self, room: Room):
        self.room = room
        self.player_a: Player = room.players[0]
        self.player_b: Player = room.players[1]
        self.state = NoghteKhatState()

    def start_game(self) -> bool:
        if len(self.room.players) != 2:
            return False
        starter = random.choice([self.player_a, self.player_b])
        self.state.current_turn = starter.user_id
        return True

    def get_player(self, user_id: int) -> Player | None:
        if self.player_a.user_id == user_id:
            return self.player_a
        if self.player_b.user_id == user_id:
            return self.player_b
        return None

    def _other_player(self, user_id: int) -> Player:
        if self.player_a.user_id == user_id:
            return self.player_b
        return self.player_a

    def _box_key(self, row: int, col: int) -> str:
        return f"{row}-{col}"

    def _is_box_complete(self, row: int, col: int) -> bool:
        return all(side in self.state.drawn_lines for side in box_sides(row, col))

    def draw_line(self, user_id: int, line_id: str) -> dict:
        if self.state.game_over:
            return {"success": False, "reason": "game_already_finished"}
        if self.state.current_turn != user_id:
            return {"success": False, "reason": "not_your_turn"}
        if not is_valid_line_id(line_id):
            return {"success": False, "reason": "invalid_line"}
        if line_id in self.state.drawn_lines:
            return {"success": False, "reason": "line_already_drawn"}

        self.state.drawn_lines[line_id] = user_id

        player = self.get_player(user_id)
        newly_completed_boxes = []

        for (row, col) in all_box_coords():
            box_key = self._box_key(row, col)
            if box_key in self.state.owned_boxes:
                continue
            if self._is_box_complete(row, col):
                self.state.owned_boxes[box_key] = user_id
                player.score += 1
                newly_completed_boxes.append(box_key)

        if len(self.state.owned_boxes) == self.state.total_boxes():
            self._finish_game()
            return {
                "success": True,
                "completed_boxes": newly_completed_boxes,
                "game_over": True,
                "current_turn": None,
            }

        if not newly_completed_boxes:
            # هیچ خونه‌ای کامل نشد، نوبت میره پیش نفر بعدی
            self.state.current_turn = self._other_player(user_id).user_id
        # اگه خونه‌ای کامل شد، نوبت پیش همین بازیکن می‌مونه (کاری نمی‌کنیم)

        return {
            "success": True,
            "completed_boxes": newly_completed_boxes,
            "game_over": False,
            "current_turn": self.state.current_turn,
        }

    def _finish_game(self):
        self.state.game_over = True
        if self.player_a.score > self.player_b.score:
            self.state.winner_user_id = self.player_a.user_id
        elif self.player_b.score > self.player_a.score:
            self.state.winner_user_id = self.player_b.user_id
        else:
            self.state.winner_user_id = None  #
