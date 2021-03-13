
import uuid
import pickle

from constants import server_command_types
from TCP.Entities.client_data import Client_Data

from UserPool import user_pool, UserPool
from client import Client

from RoomPool import room_pool, RoomPool
from Room import Room


class Message(object):

    def __init__(self):

        return

    def receive_incoming(self, sender_socket, sender_addr=None):
        # Get the address if none provided, otherwise use the one provided
        self.sender_socket = sender_socket
        self.sender_addr = sender_addr
        if not sender_addr:
            sender_addr = user_pool.get_address(sender_socket)

        try:
            # Get length of message
            self.length = int.from_bytes(sender_socket.recv(2), "little")
            self.command = server_command_types(int.from_bytes(sender_socket.recv(2), "little"))
            
            # Read message bytes
            self.bytes = sender_socket.recv(self.length)
            return True

        except:
            print("No message to read")
            return False

    def process_message(self):
        print(str(self.command) + "(" + str(self.length) + ")")

        switcher = {
            server_command_types.Log_Rooms: self.log_rooms,
            server_command_types.Log_Users: self.log_users,
            server_command_types.Welcome:   self.process_welcome_message,
        }

        func = switcher.get(self.command)
        func()

    def log_rooms(self):
        for r in room_pool.rooms.values:
            print(r.room_key)

        return
        
    def log_users(self):
        for c in user_pool.clients.values:
            print(c.client_data.username)

        return

    def process_welcome_message(self):
        client_data : Client_Data = pickle.loads(self.bytes)
        print(client_data.is_host)
        print(client_data.username)