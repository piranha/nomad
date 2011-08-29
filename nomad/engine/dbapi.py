import urlparse

from nomad.engine import BaseEngine, DBError


def p2d(p, **renames):
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


def pgfetch(c):
    if c.rowcount == -1:
        return []
    from psycopg2 import ProgrammingError
    try:
        return c.fetchall()
    except ProgrammingError:
        return []


CONNECTORS = {
    'sqlite': [{'mod': 'sqlite3',
                'exc': lambda mod: mod.Error,
                # [1:] strips first leading slash here
                'connect': lambda m, p: m.connect(p.path[1:]),
                'begin': lambda c: None,
                'commit': lambda c: c.commit(),
                'rollback': lambda c: c.rollback()}],
    'mysql': [{'mod': 'MySQLdb',
               'exc': lambda mod: mod.MySQLError,
               'parameters': '%s',
               'connect': lambda m, p: m.connect(
                **p2d(p, hostname='host', password='passwd', path='db'))}],
    'pgsql': [{'mod': 'psycopg2',
               'exc': lambda mod: mod.Error,
               'parameters': '%s',
               'connect': lambda m, p: m.connect(
                **p2d(p, hostname='host', path='database')),
               'fetch': pgfetch,
                'begin': lambda c: None,
                'commit': lambda c: c.commit(),
                'rollback': lambda c: c.rollback()}],
    }


class DBEngine(BaseEngine):
    info = None

    def connect(self):
        p = urlparse.urlparse(self.url)
        if p.scheme not in CONNECTORS:
            raise Exception('scheme %s not supported' % p.scheme)

        for info in CONNECTORS[p.scheme]:
            try:
                mod = __import__(info['mod'])
                self._connection = info['connect'](mod, p)
                self.info = info
                self.exc_class = info['exc'](mod)
            except ImportError:
                pass

        if self._connection is None:
            raise Exception('qqq')

    def query(self, statement, *args):
        c = self.connection.cursor()
        if 'parameters' in self.info:
            statement = statement.replace('?', self.info['parameters'])

        try:
            c.execute(statement, args)
        except self.exc_class, e:
            raise DBError(e)

        if 'fetch' in self.info:
            data = self.info['fetch'](c)
        else:
            data = c.fetchall()

        c.close()
        return data

    def _transaction(self, state):
        self.connection # need info here
        if state in self.info:
            self.info[state](self.connection)
        else:
            self.query(state.upper())

    def begin(self):
        return self._transaction('begin')

    def commit(self):
        return self._transaction('commit')

    def rollback(self):
        return self._transaction('rollback')


engine = DBEngine
