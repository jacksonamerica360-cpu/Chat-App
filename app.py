from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs_chat_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join_room')
def handle_join(data):
    username = data.get('username', 'Anonymous').strip()
    if username:
        emit('join_response', {'success': True, 'username': username})
        # send to everyone
        emit('receive_message', {'user': 'System', 'msg': f'{username} joined the chat!'}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    print(f"Message from {data['user']}: {data['msg']}") # to check in terminal
    emit('receive_message', {'user': data['user'], 'msg': data['msg']}, broadcast=True, include_self=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
