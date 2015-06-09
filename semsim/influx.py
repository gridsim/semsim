from influxdb.influxdb08.client import InfluxDBClient


class DBAccess(object):

    def __init__(self, host, port, username, password, database):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        self.db = InfluxDBClient(host, port, username, password, database)

    def tables(self):
        return self.db.query("SELECT * FROM "+str(self.database))

    def objects(self):
        return self.db.query("list series")

    def columns(self, table, obj):
        data = self.db.query("SELECT * FROM "+str(self.database)+'.'+str(table)+'.'+str(obj))

        if data:
            return data[0]['columns']
        else:
            raise ValueError("object not found")

    def query(self, table, obj, column,
              begin=None, end=None,
              data_name=None):

        if data_name is None:
            data_name = column

        query = "SELECT "+str(column)+" FROM "+str(self.database)+'.'+str(table)+"."+str(obj)

        if begin is not None:
            query += " WHERE time > '"+str(begin)+"'"

        if end is not None:
            if begin is None:
                query += " WHERE time < '"+str(end)+"'"
            else:
                query += " AND time < '"+str(end)+"'"

        query += ';'

        data = self.db.query(query)

        if data:
            res = {'time': [], data_name: []}
            for d in data[0]['points']:
                res['time'].append(float(d[0]))
                res[data_name].append(float(d[2]))

            return res

        else:
            raise ValueError("the table is empty")