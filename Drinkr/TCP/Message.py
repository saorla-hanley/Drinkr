
from .constants import server_command_types

class Message:
    def __init__(self, type : server_command_types, data : [bytes] = b''):
        self.length = len(data)
        self.type = type
        self.data = data

    def to_bytes(self):
        bytes = b''

        bytes += self.length.to_bytes(2, 'little')
        bytes += self.type.value.to_bytes(2, 'little')
        bytes += self.data

        return bytes


