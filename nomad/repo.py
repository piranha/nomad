import os, os.path as op
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation
from subprocess import call
from functools import wraps

from nomad.utils import cachedproperty, geturl


def tx(getrepo):
    def decorator(f):
        @wraps(f)
        def inner(self, *args, **kwargs):
            repo = getrepo(self)
            try:
                repo.engine.begin()
                f(self, *args, **kwargs)
                repo.engine.commit()
            except:
                repo.engine.rollback()
                raise
        return inner
    return decorator


class Repository(object):
    DEFAULTS = {
        'nomad': {'table': 'nomad'},
        }

    def __init__(self, confpath, overrides=None):
        self.conf = ConfigParser(interpolation=ExtendedInterpolation(),
                                 defaults={
                'confpath': op.abspath(confpath),
                'confdir': op.dirname(op.abspath(confpath)),
                })
        self.conf.read_dict(self.DEFAULTS)
        if not self.conf.read([confpath]):
            raise IOError('configuration file %r not found' % confpath)

        for k, v in (overrides or {}).iteritems():
            section, key = k.split('.')
            self.conf.set(section, key, v)

        self.path = self.conf.get('nomad', 'path',
                                  fallback=op.dirname(confpath) or '.')

        enginepath = self.conf['nomad']['engine']
        if not '.' in enginepath:
            enginepath = 'nomad.engine.' + enginepath
        enginemod = __import__(enginepath, {}, {}, [''])
        self.engine = getattr(enginemod, 'engine')(geturl(self))

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.path)

    def get(self, name):
        return Migration(self, name)

    # actual work done here
    @tx(lambda self: self)
    def init_db(self):
        self.engine.init(self.conf['nomad']['table'])

    @cachedproperty
    def available(self):
        migrations = [self.get(x) for x in os.listdir(self.path) if
                      op.isdir(op.join(self.path, x))]
        return list(sorted(migrations))

    @cachedproperty
    def applied(self):
        return [self.get(x) for (x, ) in
                self.engine.query('SELECT name FROM %s ORDER BY date' %
                                  self.conf['nomad']['table'])]


class Migration(object):
    SINGLETONS = {}

    def __new__(cls, repo, name):
        if (repo, name) not in cls.SINGLETONS:
            cls.SINGLETONS[(repo, name)] = object.__new__(cls, repo, name)
        return cls.SINGLETONS[(repo, name)]

    def __init__(self, repo, name):
        self.repo = repo
        self.name = name
        self.conf = ConfigParser(interpolation=ExtendedInterpolation())
        self.conf.read(op.join(repo.path, name, 'migration.ini'))
        self.dependecies = self.conf.get('nomad', 'dependecies', fallback=[])

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, str(self))

    def __str__(self):
        return self.name

    def __cmp__(self, other):
        if isinstance(other, Migration) and self.repo == other.repo:
            if self.name == other.name:
                return 0
            if self.name < other.name:
                return -1
            return 1
        return id(self) - id(other)

    @property
    def path(self):
        return op.join(self.repo.path, self.name)

    def execute(self, direction):
        print 'applying %sgrade %s:' % (direction, self)
        for fn in os.listdir(self.path):
            if fn.startswith(direction):
                path = op.join(self.path, fn)
                if fn.endswith('.sql'):
                    with file(path) as f:
                        self.repo.engine.query(f.read())
                    print '  sql migration applied: %s' % fn
                elif os.access(path, os.X_OK):
                    call(path)
                    print '  script migration applied: %s' % fn

    @tx(lambda self: self.repo)
    def up(self):
        self.execute('up')
        self.repo.engine.query('INSERT INTO %s (name, date) VALUES (?, ?)'
                               % self.repo.conf['nomad']['table'],
                               self.name, datetime.now())

    @tx(lambda self: self.repo)
    def down(self):
        self.execute('down')
        self.repo.engine.query('DELETE FROM %s WHERE name = ?'
                               % self.repo.conf['nomad']['table'],
                               self.name)
