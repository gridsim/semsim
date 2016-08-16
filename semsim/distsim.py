import time
import json
import ConfigParser

from decoder import ScenarioDecoder

from gridsim.unit import units
from gridsim.simulation import Simulator
from gridsim.electrical.loadflow import DirectLoadFlowCalculator


def run(arg_files, connection, second, end):

    # Create a config parser to homogenise data exchange between processes
    config_parser = ConfigParser.ConfigParser()
    config_parser.read('exchange.cfg')

    simulator = Simulator()
    simulator.electrical.load_flow_calculator = DirectLoadFlowCalculator()  # TODO set to None

    for arg_file in arg_files:

        with open(arg_file, 'r') as json_file:

            print "Loading file "+arg_file

            decoder = ScenarioDecoder(simulator, connection, units.convert(end, units.day))
            decoder.decode(json.load(json_file))

    if simulator is not None:
        print("Running simulations: "+str(arg_files))

        # Run the simulation for several days with a resolution of 1 minute.
        simulator.reset()

        connection.send(config_parser.get('Type', 'load'))

        # First step to send data to client
        simulator.step(second*units.second)

        is_running = True
        while is_running:
            time.sleep(0.05)
            while connection.poll():
                data = connection.recv()
                if data == config_parser.get('Type', 'step'):
                    simulator.step(second*units.second)
                elif data == config_parser.get('Type', 'stop'):
                    is_running = False
                else:
                    data_list = data.split()
                    controllers = simulator.find(friendly_name=data_list[0])
                    for controller in controllers:
                        controller.influence(data_list[1])

        print("End of simulation of "+str(arg_files))
    else:
        print "simulation cannot be launched."
