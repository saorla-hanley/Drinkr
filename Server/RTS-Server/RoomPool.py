
import base64
from Room import Room

class RoomPool(object):
    def __init__(self):
        self.room_key_current = 0
        self.rooms : {str, Room} = {}

    def get_next_key(self):
        self.room_key_current += 1
        return base64.b64encode(self.room_key_current)

    def add(self, new_room : Room):
        self.rooms[self.get_next_key()] = new_room

# Externally accessible instance of the RoomPool class
room_pool = RoomPool()