
#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect

from text import *
from utilities import MAX_ATTEMPTS, random_room_key
from db_manager import add_room

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





@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.event
def my_broadcast_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


# -----------------------------------------------------------------------------------
@socketio.event
def join(message):
    print(message, rooms())

    if message['room_key'] not in rooms()[1:]:
        emit('room_join_response', {'success': False,
                                    'room_key': message['room_key'],
                                    'error_message': 'room could not be found',
                                    'rooms': rooms()})
    else:
        join_room(message['room_key'])
        session['receive_count'] = session.get('receive_count', 0) + 1
        
        emit('room_join_response', {'success': True,
                                    'room_key': message['room_key'],
                                    'rooms': rooms()})


@socketio.event
def host(message):
    attempts = 0
    room_key = random_room_key()
    while room_key in rooms() and attempts < MAX_ATTEMPTS:
        room_key = random_room_key()
        attempts += 1

    if attempts == MAX_ATTEMPTS:
        emit('room_host_response', {'success': False,
                                    'room_key': '',
                                    'error_message': 'Could not find an empty room',
                                    'rooms': rooms()})

    join_room(room_key)
    add_room(room_key)
    session['receive_count'] = session.get('receive_count', 0) + 1

    emit('room_host_response', {'success': True,
                                'room_key': room_key,
                                'rooms': rooms()})

# -----------------------------------------------------------------------------------




@socketio.event
def leave(message):
    leave_room(message['roomkey'])
    session['receive_count'] = session.get('receive_count', 0) + 1
#    emit('my_response',
#         {'data': 'In rooms: ' + ', '.join(rooms()),
#          'count': session['receive_count']})


@socketio.on('close_room')
def on_close_room(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         to=message['room'])
    close_room(message['room'])


@socketio.event
def my_room_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']},
         to=message['room'])


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
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
