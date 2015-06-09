from gridsim.simulation import Simulator
from gridsim.electrical.loadflow import DirectLoadFlowCalculator
import gridsim.thermal

from decoder import ScenarioDecoder

class ScenarioReader(object):

    def __init__(self, interpreter):

        self._simulator = Simulator()
        self._simulator.electrical.load_flow_calculator = DirectLoadFlowCalculator()

        content = interpreter.read()

        self._decoder = ScenarioDecoder(self.simulator)
        self._decoder.decode(content)

        # for device in self._decoder.devices[ScenarioDecoder.THERMAL_KEY][ScenarioDecoder.DEVICES_KEY]:
        #     self._simulator.thermal.add(device)
        # temp = PlotRecorder('temperature', units.day, units.degC)
        # reader.simulator.record(temp, reader.simulator.thermal.find(has_attribute='temperature'))
        #
        # powa = PlotRecorder('Pij', units.day, units.watt)
        # reader.simulator.record(powa, reader.simulator.electrical.find(element_class=ElectricalNetworkBranch))

    @property
    def simulator(self):
        return self._simulator
