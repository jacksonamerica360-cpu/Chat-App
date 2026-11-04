import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs_chat_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Store connected users as sid -> username
connected_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    username = data.get('username', 'Anonymous').strip()
    if not username:
        return

    # Add user to active users list
    connected_users[request.sid] = username

    # Send join confirmation to the user who joined
    emit('join_response', {'success': True, 'username': username})

    # Notify all users that a new user joined
    emit('receive_message', {'user': 'System', 'msg': f'{username} joined the chat! 🎉'}, broadcast=True)

    # Update active user count for all users
    emit('update_user_count', {'count': len(connected_users)}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    user = data.get('user', 'Anonymous')
    msg = data.get('msg', data.get('message', '')).strip()
    if msg:
        print(f"Message from {user}: {msg}")
        emit('receive_message', {'user': user, 'msg': msg}, broadcast=True, include_self=True)

@socketio.on('typing')
def handle_typing(data):
    user = data.get('user', data.get('username', 'Someone'))
    # Frontend listens for display_typing event
    emit('display_typing', {'user': user}, broadcast=True, include_self=False)

@socketio.on('disconnect')
def handle_disconnect():
    username = connected_users.pop(request.sid, None)
    if username:
        emit('receive_message', {'user': 'System', 'msg': f'{username} left the chat! 👋'}, broadcast=True)
        emit('update_user_count', {'count': len(connected_users)}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
