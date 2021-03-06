
#!/usr/bin/env python
import sqlite3
import uuid
from datetime import datetime
from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context, g, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

DATABASE = 'rooms.db'

from text import *
from utilities import MAX_ATTEMPTS, random_room_key, isNoneOrEmptyOrSpace, random_roll
from procedures import room_u, room_f, room_d, \
    player_u, player_f_by_room, player_d_by_room, player_f_sequence_by_room, player_d, player_move, \
    turn_u, turn_f, turn_iter

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['CACHE_TYPE'] = 'null'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()


# WEB SERVER
# -----------------------------------------------------------------------------------

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@app.route('/join', methods=['GET'])
def join():
    if request.method == 'GET':
        return render_template('enter.html', 
            async_mode=socketio.async_mode, 
            title=TITLE)


@app.route('/game', methods=['GET'])
def game():
    if request.method == 'GET':
        return render_template('game.html', 
            async_mode=socketio.async_mode, 
            title=TITLE)


# DATABASE
# -----------------------------------------------------------------------------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    print(f"QUERY - - [{datetime.now()}] \"{query}\"")
    cur = get_db().execute(query, args)
    g._database.commit()
    rv = cur.fetchall()
    dicts = (make_dicts(cur, rv[0] if rv else None) if one else list(make_dicts(cur, rv[i]) for i in range(len(rv))))
    cur.close()
    return dicts
    
def make_dicts(cursor, row):
    if row is None:
        return None

    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# SOCKETS
# -----------------------------------------------------------------------------------

@socketio.event
def join(message):
    # Validate username is input
    if isNoneOrEmptyOrSpace(message['username']):
        emit('room_join_response', {'success': False,
                                    'room_key': message['room_key'],
                                    'error_message': 'username requred',
                                    'players': {}})
        return

    # Search for the room
    room_key = message['room_key']
    room_data = query_db(room_f(room_key), one=True)
    
    # Check room found
    if room_data is None or len(room_data) == 0:
        emit('room_join_response', {'success': False,
                                    'room_key': message['room_key'],
                                    'error_message': 'room could not be found',
                                    'players': {}})
        return

    # Check password correct
    if room_data['password'] != message['password']:
        emit('room_join_response', {'success': False,
                                    'room_key': message['room_key'],
                                    'error_message': 'password incorrect',
                                    'players': {}})
        return

    # If all good, join the room
    join_room(room_key)

    next_seq = query_db(player_f_sequence_by_room(room_key), one=True)['next_seq']
    player_id = str(uuid.uuid4())

    query_db(player_u(player_id, room_key, message['username'], False, next_seq))
    players = query_db(player_f_by_room(room_key))

    emit('room_join_response', {'success': True,
                                'room_key': message['room_key'],
                                'id': player_id,
                                'players': players, 
                                'redirect': url_for('game')})
    return


@socketio.event
def host(message):
    print(str(message['username']) + ", " + str(isNoneOrEmptyOrSpace(message['username'])))
    # Check username is input
    if isNoneOrEmptyOrSpace(message['username']):
        emit('room_join_response', {'success': False,
                                    'room_key': '',
                                    'error_message': 'username requred',
                                    'players': {}})
        return

    # Try to find a new room with a random key                                                                              To Do: replace rooms() with a database lookup + search for one at least 1 day old
    attempts = 0
    room_key = random_room_key()
    while room_key in rooms() and attempts < MAX_ATTEMPTS:
        room_key = random_room_key()
        attempts += 1
    # If exceed max number of searches, throw an error
    if attempts == MAX_ATTEMPTS:
        emit('room_host_response', {'success': False,
                                    'room_key': '',
                                    'error_message': 'Could not find an empty room',
                                    'players': {}})
        return

    # If empty room found, join the room and clear out any old players in case some remain
    join_room(room_key)

    query_db(room_u(room_key, message['password']))
    query_db(turn_u(room_key, "", 0, 0))
    query_db(player_d_by_room(room_key))

    player_id = str(uuid.uuid4())

    query_db(player_u(player_id, room_key, message['username'], True, 0))
    players = query_db(player_f_by_room(room_key))
    
    emit('room_host_response', {'success': True,
                                'room_key': room_key,
                                'id': player_id,
                                'players': players, 
                                'redirect': url_for('game')}, room=room_key)
    return


@socketio.event
def request_game_data(message):
    room_key = message['room_key']
    join_room(room_key)

    # Get players in room, and the last roll
    players = query_db(player_f_by_room(room_key))
    turn = query_db(turn_f(room_key), one=True)
    emit('receive_game_data', {'room_key': room_key,
                               'players': players, 
                               'roll': turn}, room=room_key)


@socketio.event
def request_roll_data(message):
    room_key = message['room_key']
    rolling_id = message['rolling_id']

    # Roll a dice
    roll = random_roll()

    # Move the player by the roll amount + update the turn
    query_db(turn_iter(room_key, rolling_id, roll))
    query_db(player_move(rolling_id, roll))

    # Return new information about the turn
    turn = query_db(turn_f(room_key), one=True)
    emit('receive_roll_data', {'roll': turn}, room=room_key)


@socketio.event
def leave(message):
    room_key = message['room_key']
    leave_room(room_key)

    # Delete the player from the database + send new information about the current players and turn to all who are left
    query_db(player_d(message['leaving_id']))
    players = query_db(player_f_by_room(room_key))
    turn = query_db(turn_f(room_key), one=True)
    if len(players) == 0:
        close_room(room_key)
        query_db(room_d(room_key))
    else:
        emit('receive_game_data', {'room_key': room_key,
                                   'players': players,
                                   'roll': turn}, room=room_key)




@socketio.on('close_room')
def on_close_room(message):
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])

@socketio.event
def my_room_event(message):
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']},
         callback=can_disconnect)

@socketio.event
def my_ping():
    emit('my_pong')

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)




if __name__ == '__main__':
    socketio.run(app)
