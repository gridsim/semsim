import Queue

from scenario import ScenarioReader
from interpreter import JSONInterpreter

from gridsim.recorder import *
from gridsim.unit import units

from recorders import SumRecorder


recorders = Queue.Queue()


def run(arg):

    print "Loading file "+str(arg)

    reader = ScenarioReader(JSONInterpreter(arg))

    print "name: "+str(reader.name)

    # output_dir = "../output/"+reader.name+"/"
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    temp = PlotRecorder('temperature', units.hour, units.degC)
    recorders.put((temp, reader.name))
    reader.simulator.record(temp, reader.simulator.thermal.find(has_attribute='temperature'))

    # Create a plot recorder that records the power used by the electrical heater.
    power = SumRecorder('power', units.hour, units.kilowatt)
    recorders.put((power, reader.name))

    devices = reader.simulator.electrical.find(has_attribute='power')

    reader.simulator.record(power, devices)

    # # boiler
    #
    # boiler_name = 'boiler_'+str(reader.name)
    # boiler = reader.simulator.electrical.find(friendly_name=boiler_name)
    #
    # if boiler:
    #     c = PlotRecorder('power', units.hour, units.kilowatt)
    #     recorders.put(c)
    #     reader.simulator.record(c, boiler)
    #     t = PlotRecorder('temperature', units.hour, units.degC)
    #     recorders.put(t)
    #     reader.simulator.record(t, boiler)
    #
    # # heat pump
    #
    # heat_pump_name = 'heater_'+str(reader.name)
    # heat_pump = reader.simulator.electrical.find(friendly_name=heat_pump_name)
    #
    # if heat_pump:
    #     c_hp = PlotRecorder('power', units.hour, units.kilowatt)
    #     recorders.put(c_hp)
    #     reader.simulator.record(c_hp, heat_pump)

    print("Running simulation: "+str(reader.name))

    # Run the simulation for several days with a resolution of 1 minute.
    reader.simulator.reset()
    reader.simulator.run(reader.days*units.days, units.minute)

    reader.close()

    print("End of simulation of "+str(reader.name))
