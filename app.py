import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "cs_chat_secret_key"
socketio = SocketIO(app, cors_allowed_origins="*")

# Stores: connection ID -> username
connected_users = {}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("join_room")
def handle_join(data):
    username = data.get("username", "").strip()

    if not username:
        return

    # Remember the user's name on the server
    connected_users[request.sid] = username

    socketio.emit(
        "receive_message",
        {
            "user": "System",
            "msg": f"{username} connected"
        }
    )

    socketio.emit(
        "update_user_count",
        {"count": len(connected_users)}
    )


@socketio.on("typing")
def handle_typing(data):
    # Use the server's saved username, not the name sent by the browser
    username = connected_users.get(request.sid)

    if username:
        emit(
            "display_typing",
            {"user": username},
            broadcast=True,
            include_self=False
        )


@socketio.on("send_message")
def handle_message(data):
    username = connected_users.get(request.sid)
    message = data.get("msg", "").strip()

    if username and message:
        socketio.emit(
            "receive_message",
            {
                "user": username,
                "msg": message
            }
        )


@socketio.on("disconnect")
def handle_disconnect():
    username = connected_users.pop(request.sid, None)

    if username:
        socketio.emit(
            "receive_message",
            {
                "user": "System",
                "msg": f"{username} disconnected"
            }
        )

        socketio.emit(
            "update_user_count",
            {"count": len(connected_users)}
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=False,
        allow_unsafe_werkzeug=True
    )
