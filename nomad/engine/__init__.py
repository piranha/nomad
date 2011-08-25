class BaseEngine(object):
    _connection = None

    def __init__(self, url):
        self.url = url

    @property
    def connection(self):
        if not self._connection:
            self.connect()
        return self._connection

    def connect(self):
        raise NotImplementedError()

    def query(self, statement, *args, **kwargs):
        raise NotImplementedError()
