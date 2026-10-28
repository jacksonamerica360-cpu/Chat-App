import os

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "cs_chat_secret_key"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

connected_users = {}


@app.route("/")
def index():
    return render_template("index.html")


def send_user_count():
    socketio.emit(
        "update_user_count",
        {"count": len(connected_users)}
    )


@socketio.on("join_room")
def join_room(data):
    username = data.get("username", "").strip()

    if not username:
        return

    connected_users[request.sid] = username

    socketio.emit(
        "receive_message",
        {
            "user": "System",
            "msg": f"{username} connected",
            "message": f"{username} connected"
        }
    )

    send_user_count()


@socketio.on("send_message")
def send_message(data):
    username = connected_users.get(request.sid)

    message = data.get("message") or data.get("msg") or ""
    message = message.strip()

    if not username or not message:
        return

    socketio.emit(
        "receive_message",
        {
            "user": username,
            "msg": message,
            "message": message
        }
    )


@socketio.on("typing")
def typing(data):
    username = connected_users.get(request.sid)

    if username:
        emit(
            "display_typing",
            {"user": username},
            broadcast=True,
            include_self=False
        )


@socketio.on("disconnect")
def disconnect():
    username = connected_users.pop(request.sid, None)

    if username:
        socketio.emit(
            "receive_message",
            {
                "user": "System",
                "msg": f"{username} disconnected",
                "message": f"{username} disconnected"
            }
        )

        send_user_count()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
