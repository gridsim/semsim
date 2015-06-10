import types
import math

from gridsim.decorators import accepts
from gridsim.unit import units
from gridsim.util import Position, Material, Water
from gridsim.electrical.core import AbstractElectricalCPSElement
from gridsim.timeseries import TimeSeries

from gridsim.controller import AbstractControllerElement


class Thermostat(AbstractControllerElement):

    def __init__(self, friendly_name, target_temperature, hysteresis,
                 thermal_process, subject, attribute,
                 on_value=True, off_value=False, position=Position()):
        """
        A thermostat controller. This class measures the temperature of a
        thermal process (typically a room) and controls ANY attribute of any
        AbstractSimulationElement depending the measured temperature, the given
        target_temperature and the hysteresis.

        :param: friendly_name: User friendly name to give to the element.
        :type friendly_name: str

        :param: target_temperature: The temperature to try to maintain inside
            the target ThermalProcess.
        :type: target_temperature: temperature see :mod:`gridsim.unit`

        :param: hysteresis: The +- hysteresis in order to avoid to fast on/off
            switching.
        :type: hysteresis: delta temperature see :mod:`gridsim.unit`

        :param: thermal_process: The reference to the thermal process to
            observe.
        :type: thermal_process: :class:`.ThermalProcess`

        :param: subject: Reference to the object of which is attribute has to be
            changed depending on the temperature.
        :type: object

        :param: attribute: The name of the attribute to control as string.
        :type: str

        :param: on_value: The value to set for the attribute in order to turn
            the device "on".
        :type: on_value: any

        :param: off_on_value: The value to set for the attribute in order to
            turn the device "off".
        :type: off_value: any

        :param position: The position of the thermal element.
            Defaults to [0,0,0].
        :type position: :class:`Position`
        """
        super(Thermostat, self).__init__(friendly_name, position)
        self.target_temperature = units.value(target_temperature, units.kelvin)
        """
        The temperature to try to retain inside the observer thermal process by
        conducting an electrothermal element.
        """

        self.hysteresis = units.value(hysteresis, units.kelvin)
        """
        The +- hysteresis applied to the temperature measure in order to avoid
        to fast on/off switching.
        """

        if not hasattr(thermal_process, 'temperature'):
            raise TypeError('thermal_process')
        self.thermal_process = thermal_process
        """
        The reference to the thermal process to observe and read the
        temperature from.
        """

        self.subject = subject
        """
        The reference to the element to control.
        """

        self.attribute = attribute
        """
        Name of the attribute to control.
        """

        self.on_value = on_value
        """
        Value to set in order to turn the element on.
        """

        self.off_value = off_value
        """
        Value to set in order to turn the element off.
        """

        self._output_value = off_value

        self.calculate(0, 0)

    # AbstractSimulationElement implementation.
    def reset(self):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.reset`.
        """
        pass

    def calculate(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.calculate`.
        """
        actual_temperature = self.thermal_process.temperature

        if actual_temperature < (self.target_temperature-self.hysteresis/2.):
            self._output_value = self.on_value
        elif actual_temperature > (self.target_temperature+self.hysteresis/2.):
            self._output_value = self.off_value

    def update(self, time, delta_time):
        """
        AbstractSimulationElement implementation

        .. seealso:: :func:`gridsim.core.AbstractSimulationElement.update`.
        """
        setattr(self.subject, self.attribute, self._output_value)


class ElectroThermalHeaterCooler(AbstractElectricalCPSElement):
    def __init__(self, friendly_name, pwr, efficiency_factor, thermal_process):

        super(ElectroThermalHeaterCooler, self).__init__(friendly_name)

        self._efficiency_factor = units.value(efficiency_factor)

        self._thermal_process = thermal_process

        self._power = units.value(pwr, units.watt)

        self._on = False
        """
        Controls the heater/cooler. If this is True, the heater/cooler is active
        and takes energy from the electrical
        network to actually heat or cool the thermal process associated.
        """

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, on_off):
        self._on = on_off

    @property
    def power(self):
        if self.on:
            return self._power
        else:
            return 0

    # AbstractSimulationElement implementation.
    def reset(self):
        super(ElectroThermalHeaterCooler, self).reset()
        self.on = False

    def calculate(self, time, delta_time):
        self._internal_delta_energy = self._power * delta_time
        if not self.on:
            self._internal_delta_energy = 0

    def update(self, time, delta_time):
        super(ElectroThermalHeaterCooler, self).update(time, delta_time)
        self._thermal_process.add_energy(
            self._delta_energy * self._efficiency_factor)


class BoilerMaterial(Material):
    def __init__(self):
        """
        Implementation of steel:

        * Thermal capacity: ``unknown (None)``
        * Weight: ``unknown (None)``
        * Thermal conductivity ``0.04 W/Km``

        """
        super(BoilerMaterial, self).__init__(None, None, 0.04)


class Boiler(AbstractElectricalCPSElement):

    @accepts((1, str),
             (9, TimeSeries),
             (10, (types.FunctionType, types.NoneType)))
    @units.wraps(None, (None, None, units.metre, units.metre, units.metre, units.kelvin, units.watt/(units.kelvin*(units.meter**2)), units.watt, units.kelvin, None))
    def __init__(self, friendly_name, height, radius, thickness,
                 initial_temperature, heat_transfer_coeff, power,
                 temperature_in,
                 time_series,
                 time_converter=None):
        """

        :param friendly_name:Friendly name to give to the process.
        :type friendly_name: str, unicode
        :param height: the height of the boiler
        :type height: units.metre
        :param radius: the radius of the boiler
        :type radius: units.metre
        :param thickness: the thickness of the boiler
        :type thickness: units.metre
        :param initial_temperature: the initial temperature of the water
                                    in the boiler.
        :type initial_temperature: units.kelvin
        :param heat_transfer_coeff: the heat transfer coefficient
        :type heat_transfer_coeff: units.watt/(units.kelvin*(units.meter**2)
        :param power: the electrical power to heat the boiler
        :type power: units.watt
        :param temperature_in: the temperature of the input water
        :type temperature_in: units.kelvin
        :param time_series: the time_series to load the stream
        :type time_series: class:`gridsim.timeseries.TimeSeries`
        :param time_converter:
        :type time_converter: types.FunctionType or ``None``
        :return:
        """

        # HACK: when object is constructed with *args or **kwargs
        if not isinstance(height, (int, float)):
            height = units.value(units.to_si(height))
        if not isinstance(radius, (int, float)):
            radius = units.value(units.to_si(radius))
        if not isinstance(thickness, (int, float)):
            thickness = units.value(units.to_si(thickness))
        if not isinstance(initial_temperature, (int, float)):
            initial_temperature = units.value(units.to_si(initial_temperature))
        if not isinstance(heat_transfer_coeff, (int, float)):
            heat_transfer_coeff = units.value(units.to_si(heat_transfer_coeff))
        if not isinstance(temperature_in, (int, float)):
            temperature_in = units.value(units.to_si(temperature_in))
        if not isinstance(power, (int, float)):
            power = units.value(units.to_si(power))

        super(Boiler, self).\
            __init__(friendly_name)

        self._time_converter = time_converter

        self._time_series = time_series
        self._time_series.load(time_converter=time_converter)

        self._height = height
        self._radius = radius
        self._thickness = thickness

        self._initial_temperature = initial_temperature
        self._temperature = self._initial_temperature

        self._heat_transfer_coeff = heat_transfer_coeff

        self._power = power
        self.old_power = 0

        self._temperature_in = temperature_in

        # potential energy [J/K]
        self._cb = units.value(Water().thermal_capacity) * \
            units.value(Water().weight)*math.pi*self._height*(self._radius**2)

        # global loss factor [W/K.m2]
        self._ub = 1/((1/self._heat_transfer_coeff) +
                      (self._thickness/units.value(BoilerMaterial().thermal_conductivity)))

        # thermal losses when off [W/K]
        self._off_losses = self._ub * ((2.*math.pi*(self._radius**2)) +
                                       (2*math.pi*self._height*self._radius))

        self._on = False

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, t):
        self._temperature = t

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, on_off):
        self._on = on_off

    @property
    def power(self):
        if self.on:
            return self._power
        else:
            return 0

    def reset(self):
        """
        reset(self)

        Sets the time to default (``0``).

        .. seealso:: :func:`gridsim.timeseries.TimeSeriesObject.set_time`
        """
        self._temperature = self._initial_temperature
        self._time_series.set_time()

    @accepts(((1, 2), (int, float)))
    def calculate(self, time, delta_time):

        self._time_series.set_time(time)

        unit_delta_time = delta_time

        volume = units.to_si(units(self._time_series.volume, units.litre))*delta_time/units.value(self._time_converter(1), units.second)

        # thermal losses when used [W/K]
        on_losses = units.value(volume)*units.value(Water().weight)*units.value(Water().thermal_capacity)/unit_delta_time

        # total thermal losses [W/K]
        losses = self._off_losses + on_losses

        self._temperature = self._temperature + \
            ((unit_delta_time*losses/self._cb)*(self._temperature_in-self._temperature)) +\
            (unit_delta_time/self._cb)*self.power
