import sys
import imp
from importlib import import_module

import gridsim.electrical
import gridsim.thermal
import gridsim.controller

from gridsim.unit import units
from gridsim.iodata.input import *


class ScenarioDecoder(object):

    SCENARIO_NAME_KEY = u"name"
    SCENARIO_DAYS_KEY = u"days"

    IMPORT_KEY = u"module"
    CLASS_KEY = u"type"
    PARAMETERS_KEY = u"params"
    NAME_KEY = u"friendly_name"

    TIME_SERIES_KEY = u"time_series"

    ELECTRICAL_KEY = u"electrical"
    THERMAL_KEY = u"thermal"
    CONTROLLERS_KEY = u"controllers"

    BUSES_KEY = u"buses"
    BRANCHES_KEY = u"branches"
    DEVICES_KEY = u"devices"
    ATTACH_KEY = u"attach"

    def __init__(self, simulator):
        super(ScenarioDecoder, self).__init__()

        self._name = ""
        self._days = 1

        self._simulator = simulator
        self._devices = list()
        self._time_series = dict()

    @property
    def name(self):
        return self._name

    @property
    def days(self):
        return self._days

    def decode_container(self, data, key):

        res = list()
        try:
            process_data = data.pop(key)

            for pd in process_data:
                res.append(self.detect(pd))

        except KeyError as e:
            warnings.warn(str(e.message)+" is empty")

        return res

    def isvalid_module(self, data):
        try:
            imp.find_module(data)
            return True
        except ImportError:
            return False

    def decode_module(self, data):
        import_module(data)
        return data

    def isvalid_class(self, data, modul):
        return hasattr(sys.modules[modul], data)

    def decode_class(self, data, modul):
        return getattr(sys.modules[modul], data)

    def isvalid_string(self, data):
        return True

    def decode_string(self, data):
        return str(data)

    def isvalid_reference(self, data):
        return isinstance(data, (str, unicode)) and data.startswith('#')

    def decode_reference(self, data):
        if data.startswith('#'):
            ref = str(data[1:])
            insim = self._simulator.find(friendly_name=ref)
            if not insim:
                for device in self._devices:
                    if device.friendly_name == ref:
                        return device
                return self._time_series.get(ref, None)
            return insim[0]
        else:
            raise SyntaxError(str(data)+" is not a reference")

    def isvalid_function(self, data):
        return isinstance(data, (str, unicode)) and data.startswith('lambda ')

    def decode_function(self, data):
        # FIXME: eval is a dangerous method!!!
        return eval(data)

    def isvalid_number(self, data):
        if unicode(data).isdecimal():
            return True
        else:
            try:
                complex(data)
                return True
            except ValueError:
                return False

    def decode_number(self, data):
        if unicode(data).isdecimal():
            return float(data)
        else:
            return complex(data)

    def isvalid_unit(self, data):
        try:
            units(data)
            return True
        except:
            return False

    def decode_unit(self, data):
        return units(data)

    def decode_params(self, data):

        res = dict()
        try:
            for key in data:
                res[key] = self.detect(data[key])

        except KeyError as e:
            warnings.warn(str(e.message)+" is empty")

        return res

    def decode_electrical_devices(self, data):

        for d in data:

            modul = self.decode_module(d[ScenarioDecoder.IMPORT_KEY])

            clazz = self.decode_class(d[ScenarioDecoder.CLASS_KEY], modul)

            params = self.decode_params(d[ScenarioDecoder.PARAMETERS_KEY])

            self._devices.append(clazz(**params))

    def decode_buses(self, data):

        for d in data:

            modul = self.decode_module(d[ScenarioDecoder.IMPORT_KEY])

            clazz = self.decode_class(d[ScenarioDecoder.CLASS_KEY], modul)

            name = self.decode_string(d[ScenarioDecoder.PARAMETERS_KEY][ScenarioDecoder.NAME_KEY])

            self._simulator.electrical.add(clazz(name))

    def decode_attach(self, data):

        for d in data:

            bus = self.decode_string(d["bus"])

            device = self.decode_reference(d["device"])

            self._simulator.electrical.attach(bus, device)

    def decode_branches(self, data):

        esim = self._simulator.electrical

        for d in data:

            name = self.decode_string(d[ScenarioDecoder.NAME_KEY])

            bus_a = self.decode_string(d["bus_a"])
            bus_b = self.decode_string(d["bus_b"])

            two_port = self.decode_reference(d["two_port"])

            esim.connect(name, esim.bus(bus_a), esim.bus(bus_b), two_port)

    def decode_electrical(self, data):

        electrical_data = data[ScenarioDecoder.ELECTRICAL_KEY]

        if electrical_data:
            self.decode_electrical_devices(electrical_data[ScenarioDecoder.DEVICES_KEY])
            self.decode_buses(electrical_data[ScenarioDecoder.BUSES_KEY])
            self.decode_branches(electrical_data[ScenarioDecoder.BRANCHES_KEY])
            self.decode_attach(electrical_data[ScenarioDecoder.ATTACH_KEY])

    def decode_thermal_devices(self, data):

        for d in data:

            modul = self.decode_module(d[ScenarioDecoder.IMPORT_KEY])

            clazz = self.decode_class(d[ScenarioDecoder.CLASS_KEY], modul)

            params = self.decode_params(d[ScenarioDecoder.PARAMETERS_KEY])

            obj = clazz(**params)

            self._simulator.thermal.add(obj)
            self._devices.append(obj)

    def decode_thermal(self, data):

        thermal_data = data[ScenarioDecoder.THERMAL_KEY]

        self.decode_thermal_devices(thermal_data)

    def decode_time_series(self, data):

        for d in data[ScenarioDecoder.TIME_SERIES_KEY]:

            name = self.decode_string(d[ScenarioDecoder.NAME_KEY])
            modul = self.decode_module(d[ScenarioDecoder.IMPORT_KEY])
            clazz = self.decode_class(d[ScenarioDecoder.CLASS_KEY], modul)
            # FIXME: change hardcored module
            reader = self.decode_class(d["reader"], "gridsim.iodata.input")
            stream = self.decode_string(d["data"])

            self._time_series[name] = clazz(reader(stream))

    def decode_controllers(self, data):

        for d in data[ScenarioDecoder.CONTROLLERS_KEY]:

            modul = self.decode_module(d[ScenarioDecoder.IMPORT_KEY])

            clazz = self.decode_class(d[ScenarioDecoder.CLASS_KEY], modul)

            params = self.decode_params(d[ScenarioDecoder.PARAMETERS_KEY])

            self._simulator.controller.add(clazz(**params))

    def decode(self, data):

        self._name = self.decode_string(data[ScenarioDecoder.SCENARIO_NAME_KEY])

        if ScenarioDecoder.SCENARIO_DAYS_KEY in data:
            self._days = self.decode_number(data[ScenarioDecoder.SCENARIO_DAYS_KEY])

        self.decode_time_series(data)
        self.decode_thermal(data)
        self.decode_electrical(data)
        self.decode_controllers(data)

    def detect(self, data):
        if self.isvalid_reference(data):
            return self.decode_reference(data)
        elif self.isvalid_unit(data):
            return self.decode_unit(data)
        elif self.isvalid_number(data):
            return self.decode_number(data)
        elif self.isvalid_function(data):
            return self.decode_function(data)
        elif self.isvalid_string(data):
            return self.decode_string(data)
        else:
            return None
