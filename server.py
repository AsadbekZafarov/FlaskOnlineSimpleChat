import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, send, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

users = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        logger.info(f"User '{username}' has joined the chat.")
        return redirect(url_for('chat', username=username))
    return render_template('index.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    logger.info(f"User '{username}' has entered the chat room.")
    return render_template('chat.html', username=username)

@socketio.on('join')
def handle_join(username):
    users[username] = request.sid
    emit('onlineUsers', list(users.keys()), broadcast=True)
    logger.info(f"User '{username}' has joined. Users online: {list(users.keys())}")

@socketio.on('disconnect')
def handle_disconnect():
    for username, sid in list(users.items()):
        if sid == request.sid:
            del users[username]
            break
    emit('onlineUsers', list(users.keys()), broadcast=True)
    logger.info(f"User '{username}' has disconnected. Users online: {list(users.keys())}")

@socketio.on('message')
def handle_message(data):
    username = data.get('username', 'Unknown')
    message = data.get('message', '')
    full_message = f'{username}: {message}'
    logger.info(full_message)
    send({'username': username, 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
