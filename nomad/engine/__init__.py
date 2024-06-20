class BaseEngine(object):
    _connection = None

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<%s: %s>" % (type(self).__name__, self.url)

    @property
    def connection(self):
        if not self._connection:
            self._connection = self.connect()
        return self._connection

    def connect(self):
        raise NotImplementedError()

    def set_isolation_level(self, isolation_level):
        self.connection.set_isolation_level(isolation_level)

    def query(self, statement, *args, **kwargs):
        raise NotImplementedError()

    def nobegin(self):
        self.connection.nobegin()

    def begin(self):
        self.connection.begin()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    @property
    def datetime_type(self):
        if self.url.startswith("pgsql") or self.url.startswith("postgresql"):
            return "timestamp"
        if self.url.startswith("mssql+pyodbc") or self.url.startswith("pyodbc"):
            return "datetime2"
        return "datetime"

    def init(self, tablename):
        self.query(
            """CREATE TABLE %s (
            name varchar(255) NOT NULL,
            date %s NOT NULL
        )"""
            % (tablename, self.datetime_type)
        )


class DBError(Exception):
    """Database exception in nomad"""
