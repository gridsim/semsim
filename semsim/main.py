from scenario import ScenarioReader
from interpreter import JSONInterpreter

from gridsim.recorder import *
from gridsim.unit import units
from gridsim.iodata.output import *

from sumrecorder import SumRecorder

if __name__ == '__main__':

    for i in range(1, 2):

        house_type = '%03d' % i
        house_type = "all"

        f = '../resources/demo/init/home_'+house_type+'.json'

        output_dir = "../output/"+house_type+"/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print "Loading file "+str(f)

        reader = ScenarioReader(JSONInterpreter(f))

        temp = PlotRecorder('temperature', y_unit=units.degC)
        reader.simulator.record(temp, reader.simulator.thermal.find(has_attribute='temperature'))

        # Create a plot recorder that records the power used by the electrical heater.
        power = SumRecorder('power')

        devices = reader.simulator.electrical.find(has_attribute='power')
        devices = [x for x in devices if not x.friendly_name.startswith('boiler')]
        devices = [x for x in devices if not x.friendly_name.startswith('heater')]

        print devices

        reader.simulator.record(power, devices)

        # boiler

        c = PlotRecorder('power')
        reader.simulator.record(c, reader.simulator.electrical.find(friendly_name='boiler_%03d' % i))
        t = PlotRecorder('temperature')
        reader.simulator.record(t, reader.simulator.electrical.find(friendly_name='boiler_%03d' % i))
        on = PlotRecorder('on')
        reader.simulator.record(on, reader.simulator.electrical.find(friendly_name='boiler_%03d' % i))

        # heat pump

        c_hp = PlotRecorder('power')
        reader.simulator.record(c_hp, reader.simulator.electrical.find(friendly_name='heater_%03d' % i))
        on_hp = PlotRecorder('on')
        reader.simulator.record(on_hp, reader.simulator.electrical.find(friendly_name='heater_%03d' % i))

        print("Running simulation...")

        # Run the simulation for an hour with a resolution of 1 second.
        reader.simulator.reset()
        reader.simulator.run(units.days, units.minute)

        print("Saving data...")

        # Create a PD document, add the two figures of the plot recorder to the
        # document and close the document.
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
