import json
import ConfigParser


class NetworkDataProcessor(object):

    def __init__(self, filename="exchange.cfg"):

        # Create a config parser to homogenise data exchange between processes
        self._config_parser = ConfigParser.ConfigParser()
        self._config_parser.read(filename)

        self._type = self._config_parser.get('Key', 'type')
        self._name = self._config_parser.get('Key', 'name')
        self._content = self._config_parser.get('Key', 'content')
        self._separator = self._config_parser.get('Connection', 'separator')

        self._buffer = []
        self._message_buffer = ""

    def append(self, message):

        if message.isinstance((str, unicode)):

            self._message_buffer += message

            while self._separator in self._message_buffer:
                next_message, _, self._message_buffer = message.partition(self._separator)

                message_data = json.load(next_message)

                data_type = message_data.get(self._type)
                data_name = message_data.get(self._name)
                data_content = message_data.get(self._content)

                self._buffer.append((data_type, data_name, data_content))

        else:  # message is already a dict

            data_type = message.get(self._type)
            data_name = message.get(self._name)
            data_content = message.get(self._content)

            self._buffer.append((data_type, data_name, data_content))

    def __iter__(self):
        return self

    def next(self):
        if self._buffer:
            res = self._buffer.pop(0)
            return res
        else:
            raise StopIteration
