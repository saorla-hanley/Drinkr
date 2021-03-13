
import socket
import select

from Message import Message
from client import Client
from UserPool import *

ip_address = ''
port = 5555

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind((ip_address, port))
sock.listen()

# Add server socket to userpool
user_pool.set_server_socket(sock)


# Main loop
while True:
    read_sockets, _, exception_sockets = select.select(user_pool.sockets, [], user_pool.sockets)

    for notified_socket in read_sockets:
        # Scan through all sockets which have received some input

        if notified_socket == sock:
            # If the server socket received an input, a new connection must have been made
            # Accept new connection and parse message
            client_socket, client_addr = sock.accept()

            message = Message()
            if not message.receive_incoming(client_socket, client_addr):
                continue

            message.process_message()

        else:
            # If a client socket received an input, must be a message from them
            # Parse the message
            message = Message()
            if not message.receive_incoming(notified_socket):
                user_pool.remove_client(notified_socket)
                continue

            message.process_message()

    # If a socket receives an exception notification, remove it
    for notified_socket in exception_sockets:
        sock_list.remove(notified_socket)
        del clients[notified_socket]