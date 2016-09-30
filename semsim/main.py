import os
import sys
import multiprocessing
import socket
import ConfigParser
import argparse

import distsim

from gridsim import __version__


class SimulationParser(argparse.ArgumentParser):
    def __init__(self):
        super(SimulationParser, self).__init__()

        self.add_argument('files', nargs='*',
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
        self.add_argument('--core', '-c', type=int, default=8, help='Define the number of core used by the simulation. Default 8.')


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
        self._connection = None

        # Process the arguments from argv

        self._config_parser = ConfigParser.ConfigParser('')
        self._config_parser.read('exchange.cfg')

        self.LINE_SEPARATOR = self._config_parser.get(Runner.CONNECTION, Runner.SEPARATOR)

        # Store the list of process [process: connection] to communicate with the process
        self._processes = {}

        # Initialise a new buffer to store messages from sub-processes
        self._message_buffer = []
        # Initialise a new buffer to store data from client
        self._recv_data = self.LINE_SEPARATOR

    def __enter__(self):
        return self

    def start(self, args=sys.argv):
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
            self._connection.setblocking(0)
            # A client is connected
            print 'client ' + str(client_address) + ' connected.'
        except :
            return

        # Define files to read
        files = []
        if args.file:  # if the -f arg is used
            # Give a list of files. One file per line
            # Parse the given file to find the simulation files to load
            with open(args.files[0]) as allfiles:
                for s in allfiles:
                    s = s.rstrip()
                    files.append(s)
        else:  # if -f is not used
            # The simulation files are directly given
            files = args.files

        # separate the files depending on the number of core used
        file_list = []
        for i in xrange(args.core):
            file_list.append([])

        file_list_pos = 0
        for f in files:
            file_list[file_list_pos % args.core].append(f)
            file_list_pos += 1

        # Launch each simulation in its own thread
        for arg in file_list:
            if arg:
                parent_conn = multiprocessing.Queue()
                child_conn = multiprocessing.Queue()
                process = multiprocessing.Process(target=distsim.run, args=(arg, child_conn, parent_conn, args.step, args.day))
                self._processes[process] = {"send": parent_conn, "recv": child_conn}
                process.start()

        print "end of construction"
        self._constructed = True

        if self._constructed:

            # wait for simulator initialisation
            counter = 0
            while not counter == len(self._processes.keys()):
                for p in self._processes.keys():
                    # Retrieve the connection associated to the current process
                    q = self._processes[p]["recv"]
                    while not q.empty():  # While the connection has data
                        message = q.get()
                        if message == self._config_parser.get(Runner.TYPE, Runner.LOAD):
                                counter += 1
                        else:
                            self._message_buffer.append(message)

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

                # Check data from sub-processes
                for p in self._processes.keys():
                    if p.is_alive():  # If the process is alive
                        # Retrieve the connection associated to the current process
                        q = self._processes[p]["recv"]
                        while not q.empty():  # While the connection has data
                            self._message_buffer.append(q.get())
                    else:  # If the process is finished
                        # Close properly the connection
                        self._processes[p]["recv"].close()
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
                            q = self._processes[p]["send"]
                            q.put(one_data)
                else:
                    # Receive data from socket and forward to the simulators
                    try:
                        self._recv_data += self._connection.recv(4096)
                    except:
                        continue
        else:
            print "simulation is not ready"

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Exit')
        for p in self._processes.keys():
            c = self._processes[p]['send']
            c.put(self._config_parser.get(Runner.TYPE, Runner.STOP))

        if self._connection is not None:
            self._connection.close()
        self._socket.close()

        for p in self._processes.keys():
            if not p.is_alive():
                # Close properly the connection
                self._processes[p]['send'].close()
                # Remove the process from the list
                del self._processes[p]

        if exc_val is not None:
            print exc_val

        print "End of simulations"


if __name__ == '__main__':

    import resource
    resource.getrlimit(resource.RLIMIT_NOFILE)

    # Add the folder where this file is to the path
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    # Create the argument parser
    simulation_parser = SimulationParser()

    if len(sys.argv[1:]) == 0:
        simulation_parser.print_help()
        # parser.print_usage() # for just the usage line
        simulation_parser.exit()
    args = simulation_parser.parse_args()

    with Runner() as runner:
        runner.start(args)

        runner.run()
