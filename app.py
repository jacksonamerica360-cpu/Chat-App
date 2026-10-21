import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs_chat_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 1. Track active connected users
active_users = 0


@app.route('/')
def index():
  return render_template('index.html')


# 2. Triggered automatically when a user opens the app
@socketio.on('connect')
def handle_connect():
  global active_users
  active_users += 1
  emit('update_user_count', {'count': active_users}, broadcast=True)


# 3. Triggered automatically when a user closes or leaves the app
@socketio.on('disconnect')
def handle_disconnect():
  global active_users
  active_users = max(0, active_users - 1)
  emit('update_user_count', {'count': active_users}, broadcast=True)


# 4. Handle user joining chat room
@socketio.on('join_room')
def handle_join(data):
  username = data.get('username', 'Anonymous').strip()
  if username:
    emit('join_response', {'success': True, 'username': username})
    emit(
        'receive_message',
        {'user': 'System', 'msg': f'🎉 {username} joined the chat!'},
        broadcast=True,
    )


# 5. Handle live typing indicator
@socketio.on('typing')
def handle_typing(data):
  emit(
      'display_typing',
      {'user': data.get('user')},
      broadcast=True,
      include_self=False,
  )


# 6. Handle sending and receiving messages
@socketio.on('send_message')
def handle_message(data):
  emit(
      'receive_message',
      {'user': data.get('user'), 'msg': data.get('msg')},
      broadcast=True,
  )


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
