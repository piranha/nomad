from __future__ import print_function
import os
import os.path as op
from copy import copy
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation
from subprocess import call
from functools import wraps

from nomad.utils import (cachedproperty, geturl, NomadError, NomadIniNotFound,
                         clean_sql, abort, humankey)
from nomad.engine import DBError


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


def get_engine(conf):
    try:
        enginepath = conf['nomad']['engine']
        if '.' not in enginepath:
            enginepath = 'nomad.engine.' + enginepath
    except KeyError:
        raise NomadError('nomad.engine is not defined in config file')

    try:
        enginemod = __import__(enginepath, {}, {}, [''])
    except ImportError as e:
        raise NomadError('cannot use engine %s: %s' % (enginepath, e))

    try:
        url = geturl(conf['nomad']['url'])
    except KeyError:
        abort('database url was not found in the nomad Configuration')

    engine = getattr(enginemod, 'engine')(url)
    try:
        engine.connection
    except DBError as e:
        abort(e)

    return engine, url


class Repository(object):
    DEFAULTS = {
        'nomad': {'table': 'nomad'},
    }

    def __init__(self, confpath, overrides=None):
        self.conf = ConfigParser(interpolation=ExtendedInterpolation())
        self.conf.read_dict(self.DEFAULTS)
        self.conf.set('nomad', 'confpath', op.abspath(confpath))
        self.conf.set('nomad', 'confdir',  op.dirname(op.abspath(confpath)))
        if not self.conf.read([confpath]):
            raise NomadIniNotFound(confpath)

        for k, v in (overrides or {}).iteritems():
            section, key = k.split('.')
            self.conf.set(section, key, v)

        self.confpath = confpath
        self.path = self.conf.get('nomad', 'path',
                                  fallback=op.dirname(confpath) or '.')
        self.engine, self.url = get_engine(self.conf)

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.path)

    def get(self, name):
        if name.endswith('/'):
            name = name[:-1]
        return Migration(self, name)

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
        q = 'SELECT name FROM %s ORDER BY date' % self.conf['nomad']['table']
        return [x for (x, ) in self.engine.query(q)]

    @property
    def applied(self):
        return [self.get(x) for x in self.appliednames]


class Migration(object):
    SINGLETONS = {}

    def __new__(cls, repo, name, **kwargs):
        key = (repo, name)
        if key not in cls.SINGLETONS:
            cls.SINGLETONS[key] = object.__new__(cls)
        return cls.SINGLETONS[key]

    def __init__(self, repo, name):
        self.repo = repo
        self.name = name
        self.conf = copy(self.repo.conf)
        self.conf.read([op.join(repo.path, name, 'migration.ini')])
        self.conf.set('nomad', 'dir', op.abspath(op.join(self.repo.path, name)))
        deps = self.repo.conf.get('nomad', 'dependencies', fallback='').split(',')
        self._deps = [x.strip() for x in deps if x.strip()]

        self.exists = op.exists(op.join(repo.path, name))

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, str(self))

    def __str__(self):
        return self.name

    def __lt__(self, other):
        if isinstance(other, Migration) and self.repo == other.repo:
            return humankey(self.name) < humankey(other.name)
        raise TypeError('Migrations can be compared only with other migrations')

    def get_config_dict(self):
        return dict((k, dict(self.conf.items(k))) for k in self.conf.sections())

    def get_env(self):
        envs = {}
        for k, d in self.get_config_dict().items():
            for i, v in d.items():
                envs['%s_%s' % (k.upper(), i.upper())] = v
        return envs

    @property
    def path(self):
        return op.join(self.repo.path, self.name)

    @cachedproperty
    def dependencies(self):
        return map(self.repo.get, self._deps)

    @property
    def applied(self):
        return self.name in self.repo.appliednames

    def _apply(self, env=None):
        '''The real work for applying a migration
        '''
        filenames = sorted(os.listdir(self.path), key=humankey)

        for fn in filenames:
            if fn == 'migration.ini':
                continue
            path = op.join(self.path, fn)

            if fn.endswith('.sql'):
                with open(path) as f:
                    self.repo.engine.query(clean_sql(f.read()), escape=True)
                print('  sql migration applied: %s' % fn)

            elif fn.endswith('.j2'):
                import jinja2
                j2_env = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(os.path.dirname(path))
                )
                j2_sql = j2_env.get_template(fn).render(self.get_config_dict())
                self.repo.engine.query(clean_sql(j2_sql), escape=True)
                print('  sql template migration applied: %s' % fn)

            elif os.access(path, os.X_OK) and not op.isdir(path):
                callenv = dict(os.environ,
                               # for backward compatibility
                               NOMAD_DBURL=self.repo.url,
                               **self.get_env())
                if env:
                    callenv.update(env)
                retcode = call(path, env=callenv)
                if retcode:
                    raise DBError('script failed: %s' % fn)
                print('  script migration applied: %s' % fn)

            else:
                print('  skipping file: %s' % fn)

    @tx(lambda self: self.repo)
    def apply(self, env=None, fake=False):
        '''Apply a migration
        '''
        for dep in self.dependencies:
            if not dep.applied:
                dep.apply(env=env, fake=fake)

        if not fake:
            print('applying migration %s:' % self)
            self._apply(env=env)
        else:
            print('applying "fake" migration %s' % self)

        self.repo.engine.query('INSERT INTO %s (name, date) VALUES (?, ?)'
                               % self.repo.conf['nomad']['table'],
                               self.name, str(datetime.now()))
        self.repo._property_cache = {}
