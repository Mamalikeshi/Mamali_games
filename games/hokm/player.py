class Player:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username

        self.hand = []
        self.is_ready = False
        self.is_hokm = False
        self.tricks = 0

    def sort_hand(self):
        self.hand.sort(
            key=lambda card: (
                card.suit,
                card.rank_value,
            )
        )

    def play_card(self, card_index: int):
        if card_index < 0 or card_index >= len(self.hand):
            return None

        return self.hand.pop(card_index)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "is_ready": self.is_ready,
            "is_hokm": self.is_hokm,
            "hand": [
                card.to_dict()
                for card in self.hand
            ],
        }
