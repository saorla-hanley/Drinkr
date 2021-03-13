
import pickle

class Client_Data(object):

    def __init__(self, is_host, username):
        self.is_host = is_host
        self.username = username

    def to_bytes(self):
        return pickle.dumps(self)

    def from_bytes(self, data):
        return pickle.loads(data)
