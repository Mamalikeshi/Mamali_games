class GameState:
    def __init__(self, room_id: str):
        self.room_id = room_id

        self.current_turn = None
        self.trump = None

        self.trick_cards = []
        self.completed_tricks = 0

        self.trick_wins = {}

        # امتیاز کلی بازی: تعداد دست‌هایی که هر بازیکن برده
        self.hand_wins = {}
        self.hand_number = 1

        self.winner = None

    def set_turn(self, user_id: int):
        self.current_turn = user_id

    def set_trump(self, suit: str):
        self.trump = suit

    def add_card_to_trick(self, user_id: int, card):
        self.trick_cards.append(
            (user_id, card)
        )

    def is_trick_complete(self) -> bool:
        return len(self.trick_cards) == 2

    def add_trick_win(self, user_id: int):
        self.completed_tricks += 1

        self.trick_wins[user_id] = (
            self.trick_wins.get(user_id, 0) + 1
        )

    def clear_trick(self):
        self.trick_cards = []

    def start_new_hand(self):
        self.trump = None
        self.trick_cards = []
        self.completed_tricks = 0
        self.trick_wins = {}
        self.hand_number += 1

    def set_winner(self, user_id: int):
        self.winner = user_id

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "current_turn": self.current_turn,
            "trump": self.trump,
            "completed_tricks": self.completed_tricks,
            "trick_wins": self.trick_wins,
            "hand_wins": self.hand_wins,
            "hand_number": self.hand_number,
            "winner": self.winner,
            "trick_cards": [
                {
                    "user_id": user_id,
                    "card": card.to_dict(),
                }
                for user_id, card in self.trick_cards
            ],
        }
