import sys

from scenario import ScenarioReader
from interpreter import JSONInterpreter

from gridsim.recorder import *
from gridsim.unit import units
from gridsim.iodata.output import *

from sumrecorder import SumRecorder

if __name__ == '__main__':

    for args in sys.argv[1:]:

        print "Loading file "+str(args)

        reader = ScenarioReader(JSONInterpreter(args))

        print "name: "+str(reader.name)

        output_dir = "../output/"+reader.name+"/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        temp = PlotRecorder('temperature', y_unit=units.degC)
        reader.simulator.record(temp, reader.simulator.thermal.find(has_attribute='temperature'))

        # Create a plot recorder that records the power used by the electrical heater.
        power = SumRecorder('power')

        devices = reader.simulator.electrical.find(has_attribute='power')
        devices = [x for x in devices if not x.friendly_name.startswith('boiler')]
        devices = [x for x in devices if not x.friendly_name.startswith('heater')]

        reader.simulator.record(power, devices)

        # boiler

        c = PlotRecorder('power')
        reader.simulator.record(c, reader.simulator.electrical.find(friendly_name='boiler_'+str(reader.name)))
        t = PlotRecorder('temperature')
        reader.simulator.record(t, reader.simulator.electrical.find(friendly_name='boiler_'+str(reader.name)))
        on = PlotRecorder('on')
        reader.simulator.record(on, reader.simulator.electrical.find(friendly_name='boiler_'+str(reader.name)))
        
        # heat pump
        
        c_hp = PlotRecorder('power')
        reader.simulator.record(c_hp, reader.simulator.electrical.find(friendly_name='heater_'+str(reader.name)))
        on_hp = PlotRecorder('on')
        reader.simulator.record(on_hp, reader.simulator.electrical.find(friendly_name='heater_'+str(reader.name)))

        print("Running simulation...")

        # Run the simulation for several days with a resolution of 1 minute.
        reader.simulator.reset()
        reader.simulator.run(reader.days*units.days, units.minute)

        print("Saving data...")

        FigureSaver(temp, "Temperature").save(output_dir+'temp.pdf')
        FigureSaver(power, "Power").save(output_dir+'power.pdf')

        boiler_dir = output_dir+'boiler/'
        if not os.path.exists(boiler_dir):
            os.makedirs(boiler_dir)

        FigureSaver(c, "Power").save(boiler_dir+'power.pdf')
        CSVSaver(c).save(boiler_dir+'power.csv')
        FigureSaver(t, "Temperature").save(boiler_dir+'temp.pdf')
        CSVSaver(t).save(boiler_dir+'temp.csv')
        FigureSaver(on, "Control").save(boiler_dir+'control.pdf')
        CSVSaver(on).save(boiler_dir+'control.csv')

        hp_dir = output_dir+'hp/'
        if not os.path.exists(hp_dir):
            os.makedirs(hp_dir)

        FigureSaver(on_hp, "Control").save(hp_dir+'control.pdf')
        CSVSaver(on_hp).save(hp_dir+'control.csv')
        FigureSaver(c_hp, "Power").save(hp_dir+'power.pdf')
        CSVSaver(c_hp).save(hp_dir+'power.csv')
