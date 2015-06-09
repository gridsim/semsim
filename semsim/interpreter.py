import json


class JSONInterpreter(object):

    def __init__(self, readable):
        super(JSONInterpreter, self).__init__()
        self._readable = readable

    def read(self):

        with open(self._readable, 'r') as json_file:
            return json.load(json_file)
