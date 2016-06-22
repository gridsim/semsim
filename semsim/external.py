from gridsim.thermal.element import ThermalProcess
from gridsim.unit import units


class SolarGain(ThermalProcess):
    def __init__(self, friendly_name, thermal_process, time_series, time_converter=None,
                 power_calculator=lambda t: units.convert(t, units.watt),):
        super(SolarGain, self).__init__(friendly_name, float('inf') * units.heat_capacity,
                                        0 * units.kelvin, 1 * units.kilogram)

        self._thermal_process = thermal_process

        self._time_series = time_series
        self._time_series.load(time_converter=time_converter)

        self._power_calculator = power_calculator
        self._time_series.convert('power', self._power_calculator)
        self._power = 0

    @property
    def power(self):
        return self._power

    # AbstractSimulationElement implementation.
    def reset(self):
        self.calculate(0, 1)

    def calculate(self, time, delta_time):
        self._time_series.set_time(time)
        self._power = units.value(self._time_series.power)

    def update(self, time, delta_time):
        self._thermal_process.add_energy(delta_time * self._power)
