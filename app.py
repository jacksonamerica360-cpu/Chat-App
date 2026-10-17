import os
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_12345'

# SocketIO initialize kar rahe hain
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = 0


@app.route('/')
def index():
  return render_template('index.html')


@socketio.on('connect')
def handle_connect():
  global online_users
  online_users += 1
  emit('update_user_count', online_users, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
  global online_users
  online_users -= 1
  emit('update_user_count', online_users, broadcast=True)


# Custom Socket.IO Events
@socketio.on('message')
def handle_message(data):
  emit('message', data, broadcast=True)


@socketio.on('typing')
def handle_typing(data):
  emit('typing', data, broadcast=True)


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  socketio.run(app, host='0.0.0.0', port=port)
