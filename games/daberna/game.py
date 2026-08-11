"""
Main game engine for Daberna (Iranian 90-ball Bingo).
Fully independent from other games (per project rule).

منطق زمان‌بندی:
- چون سرور امکان اجرای دائمی در پس‌زمینه نداره، به‌جای اینکه خودش هر ۵
  ثانیه یه عدد "بفرسته"، هر بار که یکی از بازیکنان وضعیت بازی رو
  می‌پرسه (refresh)، بر اساس مدت‌زمانی که از شروع بازی گذشته، اعداد
  عقب‌افتاده رو یکی‌یکی اعلام می‌کنه. نتیجه برای کاربر همون حس "هر ۵
  ثانیه یه عدد جدید" رو داره.
- بعد از هر عدد جدید، فوراً چک می‌شه که آیا کارت کسی کامل شده یا نه.
  اگه بله، بازی همون‌جا تموم می‌شه و برنده(ها) اعلام می‌شن.
"""

import random
import time

from games.daberna.room import Room
from games.daberna.player import Player
from games.daberna.state import DabernaState

DRAW_INTERVAL_SECONDS = 5
NUMBER_POOL = list(range(1, 91))
LEADERBOARD_SIZE = 5


class DabernaGame:
    def __init__(self, room: Room):
        self.room = room
        self.players: list[Player] = room.players
        self.state = DabernaState()

        self.numbers_pool: list[int] = list(NUMBER_POOL)
        random.shuffle(self.numbers_pool)
        self.pool_index: int = 0

    def start_game(self) -> bool:
        if len(self.players) < 2:
            return False
        self.state = DabernaState()
        return True

    def get_player(self, user_id: int) -> Player | None:
        for player in self.players:
            if player.user_id == user_id:
                return player
        return None

    # ---------- زمان‌بندی و اعلام اعداد ----------

    def refresh(self):
        if self.state.is_finished:
            return

        elapsed = time.time() - self.state.start_time
        should_have_drawn = int(elapsed // DRAW_INTERVAL_SECONDS) + 1
        should_have_drawn = min(should_have_drawn, len(self.numbers_pool))

        while len(self.state.drawn_numbers) < should_have_drawn:
            next_number = self.numbers_pool[self.pool_index]
            self.pool_index += 1
            self.state.drawn_numbers.append(next_number)

            self._check_for_winners()
            if self.state.is_finished:
                break

        if (
            not self.state.is_finished
            and self.pool_index >= len(self.numbers_pool)
        ):
            # اعداد تموم شد و کسی برنده نشد (خیلی نادره ولی برای اطمینانه)
            self.state.is_finished = True

    def _check_for_winners(self):
        drawn = self.state.drawn_set
        winners = []
        for player in self.players:
            winning_card = player.has_winning_card(drawn)
            if winning_card is not None:
                winners.append({
                    "user_id": player.user_id,
                    "username": player.username,
                    "card_id": winning_card.card_id,
                })

        if winners:
            self.state.winners = winners
            self.state.is_finished = True

    # ---------- جدول رده‌بندی (برای هیجان بازی) ----------

    def get_leaderboard(self) -> list[dict]:
        drawn = self.state.drawn_set
        entries = []
        for player in self.players:
            for card in player.cards:
                entries.append({
                    "user_id": player.user_id,
                    "username": player.username,
                    "card_id": card.card_id,
                    "remaining_count": card.remaining_count(drawn),
                    "missing_numbers": card.missing_numbers(drawn),
                })
        entries.sort(key=lambda e: e["remaining_count"])
        return entries[:LEADERBOARD_SIZE]

    # ---------- خروجی برای فرانت‌اند ----------

    def get_state(self) -> dict:
        self.refresh()
        drawn = self.state.drawn_set
        return {
            "state": self.state.to_dict(),
            "leaderboard": self.get_leaderboard(),
            "players": [p.to_dict(drawn) for p in self.players],
            "seconds_until_next_number": self._seconds_until_next_number(),
        }

    def _seconds_until_next_number(self) -> float:
        if self.state.is_finished:
            return 0
        elapsed = time.time() - self.state.start_time
        remainder = elapsed % DRAW_INTERVAL_SECONDS
        return round(DRAW_INTERVAL_SECONDS - remainder, 1)

    def get_player_cards(self, user_id: int) -> list[dict] | None:
        player = self.get_player(user_id)
        if player is None:
            return None
        drawn = self.state.drawn_set
        return [card.to_dict(drawn) for card in player.cards]

    def is_finished(self) -> bool:
        self.refresh()
        return self.state.is_finished
