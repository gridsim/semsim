from scenario import ScenarioReader
from interpreter import JSONInterpreter

from gridsim.recorder import *
from gridsim.unit import units
from gridsim.iodata.output import *

from sumrecorder import SumRecorder

if __name__ == '__main__':

    for i in range(1, 101):

        f = '../resources/demo/init/home_%03d.json' % i
        # f = '../resources/demo/init/home_all.json'

        print "Loading file "+str(f)

        reader = ScenarioReader(JSONInterpreter(f))

        temp = PlotRecorder('temperature', units.hour, units.degC)
        reader.simulator.record(temp, reader.simulator.thermal.find(has_attribute='temperature'))

        # Create a plot recorder that records the power used by the electrical heater.
        power = SumRecorder('power', units.hours, units.kilowatt)
        reader.simulator.record(power, reader.simulator.electrical.find(has_attribute='power'))

        c = PlotRecorder('power', units.hour, units.watt)
        reader.simulator.record(c, reader.simulator.electrical.find(friendly_name='boiler_%03d' % i))
        t = PlotRecorder('temperature', units.hour, units.degC)
        reader.simulator.record(t, reader.simulator.electrical.find(friendly_name='boiler_%03d' % i))
        on = PlotRecorder('on', units.hour, bool)
        reader.simulator.record(on, reader.simulator.electrical.find(friendly_name='boiler_%03d' % i))

        print("Running simulation...")

        # Run the simulation for an hour with a resolution of 1 second.
        reader.simulator.reset()
        reader.simulator.run(units.days, units.minute)

        print("Saving data...")

        # Create a PD document, add the two figures of the plot recorder to the
        # document and close the document.
        FigureSaver(temp, "Temperature").save('../output/demo-temp_%03d.pdf' % i)
        FigureSaver(power, "Power").save('../output/demo-power_%03d.pdf' % i)

        FigureSaver(c, "Power").save('../output/demo-boiler-power_%03d.pdf' % i)
        CSVSaver(c).save('../output/demo-boiler-power_%03d.csv' % i)
        FigureSaver(t, "Temperature").save('../output/demo-boiler-temp_%03d.pdf' % i)
        CSVSaver(t).save('../output/demo-boiler-temp_%03d.csv' % i)
        FigureSaver(on, "Control").save('../output/demo-boiler-control_%03d.pdf' % i)
        CSVSaver(on).save('../output/demo-boiler-control_%03d.csv' % i)

        # FigureSaver(temp, "Temperature").save('../output/demo-temp_all.pdf')
        # FigureSaver(power, "Power").save('../output/demo-power_all.pdf')$
