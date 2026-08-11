"""
Round state for Mench (Ludo) - supports 2, 3, and 4 players.
Fully independent from other games (per project rule).
"""


class MenchState:
    def __init__(self):
        self.current_turn: int | None = None  # user_id بازیکنی که نوبتشه
        self.last_dice_value: int | None = None

        # وقتی بازیکنی تاس می‌زنه ولی هیچ حرکت مجازی نداره (نه می‌تونه
        # مهره‌ای رو از خونه دربیاره نه هیچ مهره‌ای رو حرکت بده)
        self.no_legal_move: bool = False

        # وقتی بازیکنی تازه ۶ آورده و باید یه مهره رو حرکت بده، بعدش
        # (چون ۶ آورده) دوباره باید تاس بزنه؛ این پرچم نشون می‌ده که
        # نوبت هنوز پیش همون بازیکنه
        self.awaiting_move_after_roll: bool = False

        self.game_over: bool = False
        self.winner_order: list[int] = []  # ترتیب user_id هایی که کارشون تموم شده

    def to_dict(self) -> dict:
        return {
            "current_turn": self.current_turn,
            "last_dice_value": self.last_dice_value,
            "no_legal_move": self.no_legal_move,
            "awaiting_move_after_roll": self.awaiting_move_after_roll,
            "game_over": self.game_over,
            "winner_order": self.winner_order,
        }
