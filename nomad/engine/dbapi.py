import urlparse

from nomad.engine import BaseEngine, DBError


def path2dict(p, **renames):
    '''Convert urlparse result to dict
    '''
    result = {}
    for k in 'hostname port path user password'.split():
        value = getattr(p, k, None)
        if not value:
            continue
        if k == 'path':
            value = value.lstrip('/')
        result[renames.get(k, k)] = value
    return result


class Connection(object):
    exc = None

    @property
    def connection(self):
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
        except self.exc, e:
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

    @property
    def connection(self):
        if not self._conn:
            self._conn = self.module.connect(self.path)
        return self._conn


class Mysql(Connection):
    _conn = None
    def __init__(self, path):
        self.parameters = path2dict(path, hostname='host',
                                    password='passwd', path='db')
        import MySQLdb
        self.module = MySQLdb
        self.exc = MySQLdb.MySQLError

    @property
    def connection(self):
        if not self._conn:
            self._conn = self.module.connect(**self.parameters)
        return self._conn

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
    def __init__(self, path):
        self.parameters = path2dict(path, hostname='host', path='database')
        import psycopg2
        self.module = psycopg2
        self.exc = psycopg2.Error

    @property
    def connection(self):
        if not self._conn:
            self._conn = self.module.connect(**self.parameters)
        return self._conn

    def prepare(self, statement):
        return statement.replace('?', '%s')

    def fetch(self, cursor):
        if cursor.rowcount == -1:
            return []
        try:
            return cursor.fetchall()
        except self.module.ProgrammingError:
            return []


CONNECTORS = {'sqlite': Sqlite, 'mysql': Mysql, 'pgsql': Pgsql}


class DBEngine(BaseEngine):
    def connect(self):
        p = urlparse.urlparse(self.url)
        if p.scheme not in CONNECTORS:
            raise DBError('scheme %s not supported' % p.scheme)
        return CONNECTORS[p.scheme](p)

    def query(self, statement, *args):
        return self.connection.query(statement, *args)


engine = DBEngine
