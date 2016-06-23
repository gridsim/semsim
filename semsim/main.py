import os
import sys
import multiprocessing
import time
import socket
import ConfigParser
import argparse

import distsim

from gridsim import __version__
from gridsim.decorators import timed


class SimulationParser(argparse.ArgumentParser):
    def __init__(self):
        super(SimulationParser, self).__init__()

        self.add_argument('files', nargs='*', type=file,
                          help='The list of the file to process. Each file will be managed by its own process and Gridsim simulator.')
        self.add_argument('--port', '-p', type=int, default=10600, help='The listen port. Default 10600.')
        self.add_argument('--version', '-V', action='version', version='The simulation use Gridsim v%s\n'
                                                                       'Copyright (C) 2014-2016 The Gridsim Team.\n'
                                                                       'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.\n'
                                                                       'This is free software: you are free to change and redistribute it.\n' % __version__)
        self.add_argument('--file', '-f', action='store_true',
                          help='Allow given one file containing a list of files to simplify the cammand line.')

        self.add_argument('--day', '-d', type=int, default=1,
                          help='Define the number of day of the simulation. Default 1 day.')
        self.add_argument('--step', '-s', type=int, default=60,
                          help='Define the number of second of a time step simulation. Default 60 seconds.')


class Runner(object):
    CONNECTION = 'Connection'
    TYPE = 'Type'

    SEPARATOR = 'separator'
    LOAD = 'load'
    STOP = 'stop'

    def __init__(self, args=sys.argv):
        super(Runner, self).__init__()

        self._is_ready = False
        self._constructed = False

        # Process the arguments from argv

        self._config_parser = ConfigParser.ConfigParser('')
        self._config_parser.read('exchange.cfg')

        self.LINE_SEPARATOR = self._config_parser.get(Runner.CONNECTION, Runner.SEPARATOR)

        # Store the list of process [process: connection] to communicate with the process
        self._processes = {}

        try:
            # Create a TCP/IP socket
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Bind the socket to the port
            server_address = ('localhost', args.port)
            self._socket.bind(server_address)
            # Listen for incoming connections
            self._socket.listen(1)

            # Wait for a connection
            print 'Waiting for a connection...'
            self._connection, client_address = self._socket.accept()
            # A client is connected
            print 'client ' + str(client_address) + ' connected.'
        except socket.error as se:
            print se

        # Define files to read
        files = []
        if args.file:  # if the -f arg is used
            # Give a list of files. One file per line
            # Parse the given file to find the simulation files to load
            for s in args.files[0]:
                s = s.rstrip()
                files.append(open(s, 'r'))
        else:  # if -f is not used
            # The simulation files are directly given
            files = args.files

        # Launch each simulation in its own thread
        for arg in files:
            parent_conn, child_conn = multiprocessing.Pipe()
            process = multiprocessing.Process(target=distsim.run, args=(arg, child_conn, args.step))
            self._processes[process] = parent_conn
            process.start()

        # Initialise a new buffer to store messages from sub-processes
        self._message_buffer = []
        # Initialise a new buffer to store data from client
        self._recv_data = self.LINE_SEPARATOR

        print "end of construction"
        self._constructed = True

    def init(self):

        if self._constructed:

            # wait for simulator initialisation
            counter = 0
            while counter is not len(self._processes.keys()):
                for p in self._processes.keys():
                    # Retrieve the connection associated to the current process
                    c = self._processes[p]
                    while c.poll():  # While the connection has data
                        self._message_buffer.append(c.recv())
                        for b in self._message_buffer[:]:
                            if b == self._config_parser.get(Runner.TYPE, Runner.LOAD):
                                counter += 1
                                self._message_buffer.remove(b)

            print "simulations loaded..."
            self._is_ready = True
        else:
            print "simulation are not well constructed"

    def run(self):

        if self._is_ready:
            print "start simulation"

            # While at least one simulation is still running
            while self._processes:
                # Delay execution
                time.sleep(0.01)

                # Check data from sub-processes
                for p in self._processes.keys():
                    if p.is_alive():  # If the process is alive
                        # Retrieve the connection associated to the current process
                        c = self._processes[p]
                        while c.poll():  # While the connection has data
                            self._message_buffer.append(c.recv())
                    else:  # If the process is finished
                        # Close properly the connection
                        self._processes[p].close()
                        # Remove the process from the list
                        del self._processes[p]

                # Loop to send data to processes
                while self._message_buffer:
                    # Get the first data store in the buffer
                    current_data = self._message_buffer.pop(0)
                    # Send data to the client
                    self._connection.sendall(str(current_data) + self.LINE_SEPARATOR)

                # While a data can be processed
                if self.LINE_SEPARATOR in self._recv_data:
                    one_data, _, self._recv_data = self._recv_data.partition(self.LINE_SEPARATOR)
                    if one_data:
                        # Send it to all the sub-processes
                        for p in self._processes.keys():
                            c = self._processes[p]
                            c.send(one_data)
                else:
                    # Receive data from socket and forward to the simulators
                    self._recv_data += self._connection.recv(4096)
        else:
            print "simulation is not ready"

    def close(self):
        for p in self._processes.keys():
            c = self._processes[p]
            c.send(self._config_parser.get(Runner.TYPE, Runner.STOP))

        if self._connection is not None:
            self._connection.close()
        self._socket.close()

        for p in self._processes.keys():
            if not p.is_alive():
                # Close properly the connection
                self._processes[p].close()
                # Remove the process from the list
                del self._processes[p]

        print "End of simulations"


if __name__ == '__main__':

    # Add the folder where this file is to the path
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Create the argument parser
    simulation_parser = SimulationParser()

    if len(sys.argv[1:]) == 0:
        simulation_parser.print_help()
        # parser.print_usage() # for just the usage line
        simulation_parser.exit()
    args = simulation_parser.parse_args()

    runner = Runner(args)

    try:
        runner.init()

        runner.run()
    except socket.error as se:
        print se

    runner.close()
