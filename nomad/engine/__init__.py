class BaseEngine(object):
    _connection = None

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.url)

    def connect(self):
        raise NotImplementedError()

    def query(self, statement, *args, **kwargs):
        raise NotImplementedError()

    @property
    def connection(self):
        if not self._connection:
            self.connect()
        return self._connection

    def begin(self):
        self.query('BEGIN')

    def commit(self):
        self.query('COMMIT')

    def rollback(self):
        self.query('ROLLBACK')

    @property
    def datetime_type(self):
        if self.url.startswith('pgsql:'):
            return 'timestamp'
        return 'datetime'

    def init(self, tablename):
        self.query('''CREATE TABLE %s (
            name varchar(255) NOT NULL,
            date %s NOT NULL
        )''' % (tablename, self.datetime_type))


class DBError(Exception):
    '''Database exception in nomad'''
