from decoder import ScenarioDecoder
from interpreter import JSONInterpreter

from gridsim.unit import units
from gridsim.simulation import Simulator
from gridsim.electrical.loadflow import DirectLoadFlowCalculator


def run(arg, connection):

    print "Loading file "+str(arg)

    interpreter = JSONInterpreter(arg)

    simulator = Simulator()
    simulator.electrical.load_flow_calculator = DirectLoadFlowCalculator()  # TODO set to None

    decoder = ScenarioDecoder(simulator, connection)
    decoder.decode(interpreter.read())

    print("Running simulation: "+str(decoder.name))

    # Run the simulation for several days with a resolution of 1 minute.
    simulator.reset()
    simulator.run(decoder.days*units.days, units.minute)

    print("End of simulation of "+str(decoder.name))
