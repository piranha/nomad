import os, os.path as op
from datetime import datetime
from ConfigParser import ConfigParser, NoOptionError
from subprocess import call

from nomad.utils import cachedproperty, geturl


class Repository(object):
    DEFAULTS = {
        'nomad.table': 'nomad',
        }

    def __init__(self, confpath, overrides=None):
        self.conf = ConfigParser(defaults={
                'CONFPATH': op.abspath(confpath),
                'CONFDIR': op.dirname(op.abspath(confpath)),
                })
        if not self.conf.read(confpath):
            raise IOError('configuration file %r not found' % confpath)

        for k, v in (overrides or {}).iteritems():
            section, key = k.split('.')
            self.conf.set(section, key, v)

        self.path = self.get('nomad.path', op.dirname(confpath) or '.')

        enginepath = self['nomad.engine']
        if not '.' in enginepath:
            enginepath = 'nomad.engine.' + enginepath
        enginemod = __import__(enginepath, {}, {}, [''])
        self.engine = getattr(enginemod, 'engine')(geturl(self))

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, self.path)

    def __getitem__(self, path):
        try:
            return self.conf.get(*path.split('.'))
        except NoOptionError:
            if path in self.DEFAULTS:
                return self.DEFAULTS[path]
            raise KeyError(path)

    def __contains__(self, path):
        return self.conf.has_option(*path.split('.'))

    def get(self, path, default=None):
        try:
            return self[path]
        except KeyError:
            return default

    # actual work done here

    def init_db(self):
        return self.engine.query('''CREATE TABLE %s (
            name varchar(255) NOT NULL,
            date datetime NOT NULL
        )''' % self['nomad.table'])

    @cachedproperty
    def available(self):
        migrations = [x for x in os.listdir(self.path) if
                      op.isdir(op.join(self.path, x))]
        return list(sorted(migrations))

    @cachedproperty
    def applied(self):
        return [x for x, in
                self.engine.query('SELECT name FROM %s ORDER BY date' %
                                  self['nomad.table'])]

    def up(self, name):
        m = Migration(self, name)
        m.up()

    def down(self, name):
        m = Migration(self, name)
        m.down()


class Migration(object):
    def __init__(self, repo, name):
        self.repo = repo
        self.name = name

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, str(self))

    def __str__(self):
        return self.name

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

    def up(self):
        self.execute('up')
        self.repo.engine.query('INSERT INTO %s (name, date) VALUES (?, ?)'
                               % self.repo['nomad.table'],
                               self.name, datetime.now())

    def down(self):
        self.execute('down')
        self.repo.engine.query('DELETE FROM %s WHERE name = ?'
                               % self.repo['nomad.table'],
                               self.name)
