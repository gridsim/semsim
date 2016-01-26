import sys

from scenario import ScenarioReader
from interpreter import JSONInterpreter

from gridsim.recorder import *
from gridsim.unit import units
from gridsim.iodata.output import *

from recorders import SumPlotRecorder


def run(argv):

    for args in argv:

        print "Loading file "+str(args)

        reader = ScenarioReader(JSONInterpreter(args))

        print "name: "+str(reader.name)

        output_dir = "../output/"+reader.name+"/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        temp = PlotRecorder('temperature', units.hour, units.degC)
        reader.simulator.record(temp, reader.simulator.thermal.find(has_attribute='temperature'))

        # Create a plot recorder that records the power used by the electrical heater.
        power = SumPlotRecorder('power', units.hour, units.kilowatt)

        devices = reader.simulator.electrical.find(has_attribute='power')

        reader.simulator.record(power, devices)

        # boiler

        boiler_name = 'boiler_'+str(reader.name)
        boiler = reader.simulator.electrical.find(friendly_name=boiler_name)

        if boiler:
            c = PlotRecorder('power', units.hour, units.kilowatt)
            reader.simulator.record(c, boiler)
            t = PlotRecorder('temperature', units.hour, units.degC)
            reader.simulator.record(t, boiler)
        
        # heat pump

        heat_pump_name = 'heater_'+str(reader.name)
        heat_pump = reader.simulator.electrical.find(friendly_name=heat_pump_name)

        if heat_pump:
            c_hp = PlotRecorder('power', units.hour, units.kilowatt)
            reader.simulator.record(c_hp, heat_pump)

        print("Running simulation...")

        # Run the simulation for several days with a resolution of 1 minute.
        reader.simulator.reset()
        reader.simulator.run(reader.days*units.days, units.minute)

        reader.close()

        print("Saving data...")

        FigureSaver(temp, "Temperature").save(output_dir+'temp.pdf')
        FigureSaver(power, "Power").save(output_dir+'power.pdf')

        if boiler:
            boiler_dir = output_dir+'boiler/'
            if not os.path.exists(boiler_dir):
                os.makedirs(boiler_dir)

            FigureSaver(c, "Power").save(boiler_dir+'power.pdf')
            CSVSaver(c).save(boiler_dir+'power.csv')
            FigureSaver(t, "Temperature").save(boiler_dir+'temp.pdf')
            CSVSaver(t).save(boiler_dir+'temp.csv')

        if heat_pump:
            hp_dir = output_dir+'hp/'
            if not os.path.exists(hp_dir):
                os.makedirs(hp_dir)

            FigureSaver(c_hp, "Power").save(hp_dir+'power.pdf')
            CSVSaver(c_hp).save(hp_dir+'power.csv')


if __name__ == '__main__':

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    run(sys.argv[1:])
