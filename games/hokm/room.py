class Room:
    MAX_PLAYERS = 2

    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players = []
        self.is_started = False

    def add_player(self, player):
        if self.is_started:
            return False

        if len(self.players) >= self.MAX_PLAYERS:
            return False

        if self.get_player(player.user_id) is not None:
            return False

        self.players.append(player)

        return True

    def get_player(self, user_id: int):
        for player in self.players:
            if player.user_id == user_id:
                return player

        return None

    def is_full(self):
        return len(self.players) == self.MAX_PLAYERS

    def both_ready(self):
        return (
            self.is_full()
            and all(
                player.is_ready
                for player in self.players
            )
        )

    def start(self):
        if not self.both_ready():
            return False

        self.is_started = True

        return True

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "players": [
                player.to_dict()
                for player in self.players
            ],
            "is_full": self.is_full(),
            "is_started": self.is_started,
        }
