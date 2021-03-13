
import uuid

from client import Client

class UserPool(object):

    def __init__(self):
        self.server_uuid : [bytes] = uuid.uuid4().bytes

        self.sockets : [_] = []
        self.clients : {_, Client} = {}
    

    def set_server_socket(self, socket):
        self.server_socket = socket
        self.sockets.append(socket)



    def add_client(self, socket, client):
        self.sockets.append(socket)
        self.clients[socket] = client
        
    def remove_client(self, socket):
        username = self.clients[socket].username
        print(f"Close connection {username}")
        self.sockets.remove(socket)
        del self.clients[socket]

        

    def get_address(self, socket):
        if socket in self.sockets:
            return self.clients[socket].address



# Externally accessible instance of the UserPool class
user_pool = UserPool()