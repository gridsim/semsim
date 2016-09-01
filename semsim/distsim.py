import time
import json
import ConfigParser

from decoder import ScenarioDecoder

from gridsim.unit import units
from gridsim.simulation import Simulator


def run(arg_files, sender, recver, second, end):

    # Create a config parser to homogenise data exchange between processes
    config_parser = ConfigParser.ConfigParser()
    config_parser.read('exchange.cfg')

    simulator = Simulator()

    for arg_file in arg_files:

        with open(arg_file, 'r') as json_file:

            print "Loading file "+arg_file

            decoder = ScenarioDecoder(simulator, sender, units.convert(end, units.day))
            decoder.decode(json.load(json_file))

    if simulator is not None:
        print("Running simulations: "+str(arg_files))

        # Run the simulation for several days with a resolution of 1 minute.
        simulator.reset()

        sender.put(config_parser.get('Type', 'load'))

        # First step to send data to client
        simulator.step(second*units.second)

        is_running = True
        while is_running:
            time.sleep(0.05)
            while not recver.empty():
                data = recver.get()
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
