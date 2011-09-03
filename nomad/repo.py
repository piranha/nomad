import os, os.path as op
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation
from subprocess import call
from functools import wraps

from nomad.utils import cachedproperty, geturl, NomadError


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

        try:
            enginepath = self.conf['nomad']['engine']
        except KeyError:
            raise NomadError('nomad.engine is not defined in config file')
        if not '.' in enginepath:
            enginepath = 'nomad.engine.' + enginepath
        try:
            enginemod = __import__(enginepath, {}, {}, [''])
        except ImportError:
            raise NomadError('engine %s is unknown' % enginepath)
        self.engine = getattr(enginemod, 'engine')(geturl(self))

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.path)

    def get(self, name):
        applied = name in self.appliednames
        return Migration(self, name, applied=applied)

    # actual work is done here
    @tx(lambda self: self)
    def init_db(self):
        self.engine.init(self.conf['nomad']['table'])

    @cachedproperty
    def available(self):
        migrations = [self.get(x) for x in os.listdir(self.path) if
                      op.isdir(op.join(self.path, x))]
        return list(sorted(migrations))

    @cachedproperty
    def appliednames(self):
        return [x for (x, ) in
                self.engine.query('SELECT name FROM %s ORDER BY date' %
                                  self.conf['nomad']['table'])]

    @property
    def applied(self):
        return [self.get(x) for x in self.appliednames]


class Migration(object):
    SINGLETONS = {}

    def __new__(cls, repo, name, **kwargs):
        if (repo, name) not in cls.SINGLETONS:
            cls.SINGLETONS[(repo, name)] = object.__new__(
                cls, repo, name, **kwargs)
        return cls.SINGLETONS[(repo, name)]

    def __init__(self, repo, name, force=False, applied=False):
        self.repo = repo
        self.name = name
        if not op.exists(op.join(repo.path, name)) and not force:
            raise NomadError('migration not found')
        self.conf = ConfigParser(interpolation=ExtendedInterpolation())
        self.conf.read([op.join(repo.path, name, 'migration.ini')])
        self._deps = [x.strip() for x in self.conf.get('nomad', 'dependencies',
                                                       fallback='').split(',')
                      if x.strip()]
        self.applied = applied

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

    @cachedproperty
    def dependencies(self):
        return map(self.repo.get, self._deps)

    @tx(lambda self: self.repo)
    def apply(self):
        for dep in self.dependencies:
            if not dep.applied:
                dep.apply()

        print 'applying migration %s:' % self

        for fn in os.listdir(self.path):
            if fn == 'migration.ini':
                continue
            path = op.join(self.path, fn)
            if fn.endswith('.sql'):
                with file(path) as f:
                    self.repo.engine.query(f.read())
                print '  sql migration applied: %s' % fn
            elif os.access(path, os.X_OK):
                call(path)
                print '  script migration applied: %s' % fn
            else:
                print '  skipping file: %s' % fn

        self.repo.engine.query('INSERT INTO %s (name, date) VALUES (?, ?)'
                               % self.repo.conf['nomad']['table'],
                               self.name, datetime.now())
        self.applied = True
