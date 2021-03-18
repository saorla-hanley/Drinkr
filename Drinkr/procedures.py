
from datetime import datetime

def room_u(room_name, password):
    return f"INSERT INTO rooms (id,dateModified,password) VALUES ('{str(room_name)}', '{str(datetime.today())}', '{str(password)}'); "

def room_f(room_name):
    return f"SELECT * FROM rooms WHERE id = '{room_name}';"

def room_d(room_name):
    return f"DELETE FROM rooms WHERE id = '{room_name}';"



def player_u(id, room_name, username, is_host, sequence):
    return f"INSERT INTO players (id,room_id,username,is_host,sequence, current_tile) VALUES ('{id}','{room_name}','{username}',{1 if is_host else 0},'{sequence}', {0});"

def player_move(id, amount):
    return f"UPDATE players SET current_tile = current_tile + {amount} WHERE id = '{id}';"

def player_f_by_room(room_name):
    return f"SELECT * FROM players WHERE room_id = '{room_name}';"

def player_d_by_room(room_name):
    return f"DELETE FROM players WHERE room_id = '{room_name}';"

def player_d(id):
    return f"DELETE FROM players WHERE id = '{id}';"

def player_f_sequence_by_room(room_name):
    return f"SELECT max(sequence) + 1 AS next_seq FROM players WHERE room_id = '{room_name}';"



def turn_u(room_name, last_roller, last_roll, current_turn):
    return f"INSERT INTO turns (room_id,last_roller,last_roll,current_turn) VALUES ('{room_name}','{last_roller}','{last_roll}','{current_turn}');"

def turn_iter(room_name, last_roller, last_roll):
    return f"UPDATE turns SET current_turn = current_turn + 1, last_roller = '{last_roller}', last_roll = {last_roll} WHERE room_id = '{room_name}';"

def turn_f(room_name):
    return f"SELECT * FROM turns WHERE room_id = '{room_name}';"
