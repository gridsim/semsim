from gridsim.simulation import Simulator
from gridsim.electrical.loadflow import DirectLoadFlowCalculator

from decoder import ScenarioDecoder


class ScenarioReader(object):

    def __init__(self, interpreter):

        self._simulator = Simulator()
        self._simulator.electrical.load_flow_calculator = DirectLoadFlowCalculator()

        content = interpreter.read()

        self._decoder = ScenarioDecoder(self.simulator)
        self._decoder.decode(content)

        self._decoder.network.start_server()

    @property
    def simulator(self):
        return self._simulator

    @property
    def name(self):
        return self._decoder.name

    @property
    def days(self):
        return self._decoder.days

    def close(self):
        self._decoder.network.close()
