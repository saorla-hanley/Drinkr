
import socket
import uuid

from .Entities.client_data import Client_Data
from .Message import Message

class Client(object):
    def __init__(self):
        self.id = uuid.uuid4()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def set_data(self, is_host, username):
        self.client_data = Client_Data(is_host, username)

    def connect(self, ip_address, port):
        self.socket.connect((ip_address, port))

    def send(self, message : Message):
        self.socket.sendall(message.to_bytes())

    def recv(self):

current_client = Client()