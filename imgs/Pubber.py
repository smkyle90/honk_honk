import json
import zmq

class Pubber:
    def __init__(self, addr, port):
        self.socket = zmq.Context().socket(zmq.PUB)
        self.socket.bind("tcp://{}:{}".format(addr, port))

    def pub(self, msg):
        json_msg = json.dumps(msg)
        self.socket.send_json(json_msg)
        