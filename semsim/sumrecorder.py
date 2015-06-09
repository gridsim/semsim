from gridsim.decorators import accepts
from gridsim.recorder import PlotRecorder


class SumRecorder(PlotRecorder):

    @accepts((1, str))
    def __init__(self, attribute_name, x_unit=None, y_unit=None):
        super(SumRecorder, self).__init__(attribute_name, x_unit, y_unit)

        self._x = []
        self._y = {}

        self._current_time = -1
        self._current_y = 0

    def on_simulation_reset(self, subjects):
        self._y = {self._attribute_name: []}
        self._current_y = 0

    def on_observed_value(self, subject, time, value):

        if time != self._current_time:
            self._y[self._attribute_name].append(self._current_y)
            self._current_y = 0

        self._current_y += value

        self._current_time = time
