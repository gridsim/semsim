from gridsim.decorators import accepts, returns
from gridsim.iodata.input import Reader


class DBReader(Reader):

    def __init__(self, db, table, obj, column, begin, end):
        """
        __init__(self)

        This class is the based class of all readers/loaders.
        """
        super(Reader, self).__init__()

        self._db = db
        self._table = table
        self._obj = obj
        self._column = column
        self._begin = begin
        self._end = end

    def clear(self):
        """
        clear(self)

        Empties the data of the Reader.
        """
        pass

    @accepts((1, str))
    @returns(dict)
    def load(self, data_type=float):
        """
        load(self, data_type=float)

        This method MUST returns formatted data following this format
        ``[(label1, data1], (label2, data2), ...]``

        with:

        * ``labelX``: a str
        * ``dataX``: a list of ``data_type``

        :param data_type: the type of stored data (always float).
        :type data_type: type (always float)

        :return: a dict of values
        :rtype: dict
        """
        return self._db.query(self._table, self._obj, self._column,
                              self._begin, self._end)


