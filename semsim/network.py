import socket
import sys

import json

from gridsim.recorder import Recorder


class NetworkManager(object):

    def __init__(self, host, port, time_recorder):

        self._time_recorder = time_recorder
        self._time_recorder.network_manager = self

        self._recorders = []

        self._server = JSONBlockedServer(host, port)

    @property
    def recorders(self):
        return self._recorders

    @property
    def controllers(self):
        return self._server.controllers

    def start_server(self):
        self._server.start()

    def next_step(self, time):

        data = {}
        for recorder in self._recorders:
            for subject in recorder.subjects:
                data[subject] = []

        for recorder in self._recorders:
            for subject in recorder.subjects:
                data[subject].append({recorder.attribute_name:
                                      recorder.subjects[subject]})
        self._server.send({time: data})

    def close(self):
        self._server.close()


class ValueRecorder(Recorder):

    def __init__(self, attribute_name, x_unit=None, y_unit=None):

        super(ValueRecorder, self).__init__(attribute_name, x_unit, y_unit)
        self.subjects = {}

    def on_simulation_reset(self, subjects):
        for subject in subjects:
            self.subjects[subject] = None

    def on_simulation_step(self, time):
        pass

    def on_observed_value(self, subject, time, value):
        self.subjects[subject] = value


class TimeRecorder(Recorder):

    def __init__(self, attribute_name):

        super(TimeRecorder, self).__init__(attribute_name, None, None)

        self._network_manager = None
        self._old_time = None

    @property
    def network_manager(self):
        return self._network_manager

    @network_manager.setter
    def network_manager(self, nm):
        self._network_manager = nm

    def on_simulation_reset(self, subjects):
        self._old_time = None

    def on_simulation_step(self, time):
        res = self._old_time
        if self._old_time is not None:
            self._network_manager.next_step(self._old_time)

        self._old_time = time
        return res

    def on_observed_value(self, subject, time, value):
        pass


class BlockedServer(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._controllers = []

        self._connection = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._buffer = ''

    @property
    def controllers(self):
        return self._controllers

    def start(self):
        try:
            self._socket.bind((self._host, self._port))
        except socket.error:
            print "The socket binding to the address'" + \
                  self._host + ":" + str(self._port) + \
                  "' failed"
            sys.exit()

        print "Waiting for connection..."

        self._socket.listen(5)
        self._connection, address = self._socket.accept()

    def send(self, data):

        # send message
        message = self.encode(data)
        message += self.line_separator

        self._connection.send(message)

        # receive message...
        self._buffer += self._connection.recv(1024)
        while self.line_separator not in self._buffer:
            self._buffer += self._connection.recv(1024)

        # ... and process message
        reception, separator, self._buffer = self._buffer.partition(self.line_separator)
        receiver, decoded = self.decode(reception)

        # use self._controllers to manage local controllers
        for controller in self._controllers:
            if controller.friendly_name == receiver:
                controller.influence(decoded)
                break

    def close(self):

        # close connection
        self._connection.close()

    @property
    def line_separator(self):
        raise NotImplementedError('Pure abstract method!')

    def encode(self, data):
        raise NotImplementedError('Pure abstract method!')

    def decode(self, message):
        raise NotImplementedError('Pure abstract method!')


class JSONBlockedServer(BlockedServer):

    def __init__(self, host, port):
        super(JSONBlockedServer,self).__init__(host, port)

    @property
    def line_separator(self):
        return '#'

    def encode(self, data):
        return json.dumps(data)

    def decode(self, message):
        # message = message.replace("'", '"')
        data = json.loads(message)

        return data[u'receiver'], data[u'value']
