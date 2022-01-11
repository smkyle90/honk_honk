import json
import zmq

class Subber:
    def __init__(self, addr, port):
        self.socket = zmq.Context().socket(zmq.SUB)
        self.socket.connect("tcp://{}:{}".format(addr, port))
        self.socket.subscribe("")

    def sub(self):
        json_data = self.socket.recv_json()
        data = json.loads(json_data)
        return data
