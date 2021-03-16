
from datetime import datetime

def room_u(room_name, password):
    return f"INSERT INTO rooms (id,dateModified,password) VALUES ('{str(room_name)}', '{str(datetime.today())}', '{str(password)}'); "

def room_f(room_name):
    return f"SELECT * FROM rooms WHERE id = '{room_name}';"


def player_u(id, room_name, username):
    return f"INSERT INTO players (id,room_id,username) VALUES ('{id}','{room_name}','{username}');"

def player_f_by_room(room_name):
    return f"SELECT * FROM players WHERE room_id = '{room_name}';"

def player_d_by_room(room_name):
    return f"DELETE FROM players WHERE room_id = '{room_name}';"