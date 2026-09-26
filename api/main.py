import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from api.room import create_room, join_room, get_room
from api.hokm import start_hokm, choose_trump, play_card, get_game_state


HOST = "0.0.0.0"
PORT = 7860


class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status_code=200):
        response = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status_code)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(response))
        )

        self.end_headers()
        self.wfile.write(response)

    def read_json(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            if not body:
                return {}

            return json.loads(
                body.decode("utf-8")
            )

        except Exception:
            return None

    def do_GET(self):
        if self.path == "/":
            self.send_json({
                "status": "ok",
                "service": "Mamali Games API",
            })
            return

        if self.path.startswith("/room/"):
            room_id = self.path.split("/room/", 1)[1]

            room = get_room(room_id)

            if room is None:
                self.send_json(
                    {"error": "Room not found"},
                    404
                )
                return

            self.send_json(room.to_dict())
            return

        if self.path.startswith("/game/"):
            room_id = self.path.split("/game/", 1)[1]

            state = get_game_state(room_id)

            if state is None:
                self.send_json(
                    {"error": "Game not found"},
                    404
                )
                return

            self.send_json(state)
            return

        self.send_json(
            {"error": "Not found"},
            404
        )

    def do_POST(self):
        data = self.read_json()

        if data is None:
            self.send_json(
                {"error": "Invalid JSON"},
                400
            )
            return

        if self.path == "/room/create":
            room_id = data.get("room_id")

            if not room_id:
                self.send_json(
                    {"error": "room_id is required"},
                    400
                )
                return

            room = create_room(room_id)

            if room is None:
                self.send_json(
                    {"error": "Room already exists"},
                    409
                )
                return

            self.send_json(
                room.to_dict(),
                201
            )
            return

        if self.path == "/room/join":
            room_id = data.get("room_id")
            user_id = data.get("user_id")
            username = data.get("username")

            if room_id is None:
                self.send_json(
                    {"error": "room_id is required"},
                    400
                )
                return

            if user_id is None:
                self.send_json(
                    {"error": "user_id is required"},
                    400
                )
                return

            if username is None:
                self.send_json(
                    {"error": "username is required"},
                    400
                )
                return

            room = join_room(
                room_id,
                int(user_id),
                username,
            )

            if room is None:
                self.send_json(
                    {"error": "Cannot join room"},
                    400
                )
                return

            self.send_json(room.to_dict())
            return

        if self.path == "/game/start":
            room_id = data.get("room_id")

            if room_id is None:
                self.send_json(
                    {"error": "room_id is required"},
                    400
                )
                return

            game = start_hokm(room_id)

            if game is None:
                self.send_json(
                    {"error": "Cannot start game"},
                    400
                )
                return

            self.send_json(
                game.get_state()
            )
            return

        if self.path == "/game/trump":
            room_id = data.get("room_id")
            user_id = data.get("user_id")
            suit = data.get("suit")

            if room_id is None:
                self.send_json(
                    {"error": "room_id is required"},
                    400
                )
                return

            if user_id is None:
                self.send_json(
                    {"error": "user_id is required"},
                    400
                )
                return

            if suit is None:
                self.send_json(
                    {"error": "suit is required"},
                    400
                )
                return

            success = choose_trump(
                room_id,
                int(user_id),
                suit,
            )

            if not success:
                self.send_json(
                    {"error": "Cannot choose trump"},
                    400
                )
                return

            self.send_json(
                get_game_state(room_id)
            )
            return

        if self.path == "/game/play":
            room_id = data.get("room_id")
            user_id = data.get("user_id")
            card_index = data.get("card_index")

            if room_id is None:
                self.send_json(
                    {"error": "room_id is required"},
                    400
                )
                return

            if user_id is None:
                self.send_json(
                    {"error": "user_id is required"},
                    400
                )
                return

            if card_index is None:
                self.send_json(
                    {"error": "card_index is required"},
                    400
                )
                return

            success = play_card(
                room_id,
                int(user_id),
                int(card_index),
            )

            if not success:
                self.send_json(
                    {"error": "Invalid card move"},
                    400
                )
                return

            self.send_json(
                get_game_state(room_id)
            )
            return

        self.send_json(
            {"error": "Not found"},
            404
        )

    def log_message(self, format, *args):
        return


def run_server():
    server = HTTPServer(
        (HOST, PORT),
        APIHandler
    )

    print(
        f"Mamali Games API running on port {PORT}"
    )

    server.serve_forever()


if __name__ == "__main__":
    run_server()
