
import uuid
import json

from TCP.Entities.client_data import Client_Data


class Client(object):
    """ Contains information to uniquely identify client, and hold client permissions """

    def __init__(self, address):
        self.address = address
        self.ip_address = address[0]
        self.port = address[1]
        

    def set_data(self, is_host, username):
        self.client_data = Client_Data(is_host, username)
