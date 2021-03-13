
from Message import Message
from Body import BodyElement
from client import Client
from message_types import server_command_types
from UserPool import UserPool, user_pool


def process_welcome_message(message : Message, element : BodyElement):
    print(f"welcome {message.sender_addr}")
    sender_client = Client(message.sender_addr)
    user_pool.add_client(message.sender_socket, sender_client)





def process_command_message(message : Message):
    switcher = {
        server_command_types.Welcome:       process_welcome_message
    }
    

    for element in message.body.contents:
        command_type = server_command_types(int.from_bytes(element.element_value[0 : 2], "little"))
        func = switcher.get(command_type)
        func(message, element)
