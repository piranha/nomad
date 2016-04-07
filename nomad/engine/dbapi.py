import urlparse
import urllib

from nomad.engine import BaseEngine, DBError


def unq(s):
    if isinstance(s, str):
        return urllib.unquote(s)
    return s


class Connection(object):
    exc = None

    def __init__(self):
        self.connection = self.connect()

    def connect(self):
        raise NotImplementedError()

    def prepare(self, statement):
        return statement

    def fetch(self, cursor):
        return cursor.fetchall()

    def query(self, statement, *args):
        statement = self.prepare(statement)
        c = self.connection.cursor()
        try:
            c.execute(statement, args)
        except self.exc as e:
            raise DBError(e)

        data = self.fetch(c)
        c.close()
        return data

    def begin(self):
        pass

    def commit(self):
        return self.connection.commit()

    def rollback(self):
        return self.connection.rollback()


class Sqlite(Connection):
    _conn = None

    def __init__(self, path):
        # [1:] strips first leading slash here
        self.path = path.path[1:]
        import sqlite3
        self.module = sqlite3
        self.exc = sqlite3.Error
        Connection.__init__(self)

    def connect(self):
        return self.module.connect(self.path)


class Mysql(Connection):
    _conn = None

    def __init__(self, url):
        self.parameters = {'host':   unq(url.hostname),
                           'port':   url.port,
                           'db':     unq(url.path.lstrip('/')),
                           'user':   unq(url.username),
                           'passwd': unq(url.password)}
        for k, v in self.parameters.items():
            if not v:
                del self.parameters[k]
        import MySQLdb
        self.module = MySQLdb
        self.exc = MySQLdb.MySQLError
        Connection.__init__(self)

    def connect(self):
        return self.module.connect(**self.parameters)

    def prepare(self, statement):
        return statement.replace('?', '%s')

    def begin(self):
        return self.query('BEGIN')

    def commit(self):
        return self.query('COMMIT')

    def rollback(self):
        return self.query('ROLLBACK')


class Pgsql(Connection):
    _conn = None

    def __init__(self, url):
        self.parameters = {'host':     unq(url.hostname),
                           'port':     url.port,
                           'database': unq(url.path.lstrip('/')),
                           'user':     unq(url.username),
                           'password': unq(url.password)}
        if url.query:
            self.options = url.query.split('&')
        else:
            self.options = ['statement_timeout=1000', 'lock_timeout=500']

        import psycopg2
        self.module = psycopg2
        self.exc = psycopg2.Error
        Connection.__init__(self)

    def connect(self):
        try:
            return self.module.connect(**self.parameters)
        except self.module.OperationalError as e:
            raise DBError('psycopg2: %s' % e)

    def prepare(self, statement):
        return statement.replace('?', '%s')

    def fetch(self, cursor):
        if cursor.rowcount == -1:
            return []
        try:
            return cursor.fetchall()
        except self.module.ProgrammingError:
            return []

    def begin(self):
        c = self.connection.cursor()
        c.executemany(['BEGIN'] + ['set ' + x for x in self.options], [])
        c.close()

CONNECTORS = {'sqlite': Sqlite, 'mysql': Mysql,
              'pgsql': Pgsql, 'postgresql': Pgsql, 'postgres': Pgsql}


class DBEngine(BaseEngine):
    def connect(self):
        p = urlparse.urlparse(self.url)
        if p.scheme not in CONNECTORS:
            raise DBError('scheme "%s" not supported' % p.scheme)
        return CONNECTORS[p.scheme](p)

    def query(self, statement, *args, **kwargs):
        return self.connection.query(statement, *args)


engine = DBEngine
