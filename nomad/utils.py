from __future__ import print_function
import sys
import re
import os
import os.path as op
import shlex
import imp
import json
from subprocess import Popen, PIPE
from configparser import ConfigParser, ExtendedInterpolation

from termcolor import cprint

if sys.version_info[0] == 3:
    shell_split = shlex.split
else:
    def shell_split(cmd):
        return shlex.split(cmd.encode('utf-8'))

NUM_RE = re.compile('(\d+)')


class NomadError(Exception):
    pass


class NomadIniNotFound(Exception):
    pass


def cachedproperty(f):
    """Returns a cached property that is calculated by function f
    """
    def get(self):
        try:
            return self._property_cache[f]
        except AttributeError:
            self._property_cache = {}
        except KeyError:
            pass
        x = self._property_cache[f] = f(self)
        return x

    return property(get)


def abort(msg, code=1):
    cprint('Error: %s' % msg, 'red', file=sys.stderr)
    sys.exit(code)


def shsplit(s):
    if not isinstance(s, str):
        s = s.encode('utf-8')
    return shlex.split(s)


def humankey(fn):
    '''Turn a string into a list of substrings and numbers.

    This can be used as a key function for ``sorted``::

        >>> s = lambda *x: list(sorted(x, key=humankey))
        >>> print(s('up-1', 'up-5', 'up-15', 'up-50'))
        ['up-1', 'up-5', 'up-15', 'up-50']
        >>> print(s('up-1.sql', 'up.sql', 'up1.sql'))
        ['up.sql', 'up1.sql', 'up-1.sql']
        >>> print(s('up.rb', 'up.py')) # check extension sorting
        ['up.py', 'up.rb']
    '''
    fn, ext = os.path.splitext(fn)
    return [int(s) if s.isdigit() else s for s in NUM_RE.split(fn)], ext


def loadpath(path):
    modname = 'nomad_url_%s' % path.replace('/', '_').replace('.', '_')
    path = op.expanduser(op.expandvars(path))
    if op.isdir(path):
        # path/__init__.py
        d, f = op.split(path.rstrip('/'))
        fd, fpath, desc = imp.find_module(f, [d])
        return imp.load_module(modname, fd, fpath, desc)
    else:
        return imp.load_source(modname, path)


def clean_sql(sql):
    return '\n'.join(x for x in sql.split('\n')
                     if not x.strip().startswith('--'))


# URL retrievers
def get_python(path):
    pypath, attr = path.split(':')
    if '/' in pypath or pypath.endswith('.py'):
        # load from file
        mod = loadpath(pypath)
    else:
        # load from sys.path
        mod = __import__(pypath, {}, {}, [''])
    try:
        return reduce(lambda x, y: getattr(x, y), attr.split('.'), mod)
    except AttributeError:
        raise AttributeError("No attr '%s' in module %s" % (attr, pypath))


def get_file(path):
    return open(path).read().strip()


def get_command(cmd):
    p1 = Popen(shell_split(cmd), stdout=PIPE)
    return p1.communicate()[0].strip().decode('utf-8')


def get_json(path):
    fn, path = path.split(':')
    obj = json.load(open(fn))
    path = map(lambda x: int(x) if x.isdigit() else x, path.split('.'))
    return reduce(lambda x, y: x[y], path, obj)


def get_ini(path):
    fn, path = path.split(':')
    section, key = path.split('.')
    cfg = ConfigParser(interpolation=ExtendedInterpolation())
    cfg.read([fn])
    try:
        return cfg[section][key]
    except KeyError:
        raise KeyError('%s not found in %s' % (path, fn))


def get_yaml(path):
    try:
        import yaml
    except ImportError:
        abort('Please, install PyYAML to parse YAML config.')
    fn, path = path.split(':')
    obj = yaml.load(open(fn))
    path = map(lambda x: int(x) if x.isdigit() else x, path.split('.'))
    return reduce(lambda x, y: x[y], path, obj)


def get_env(key):
    return os.environ[key]


URLTYPES = {
    'python': get_python,
    'py': get_python,
    'file': get_file,
    'command': get_command,
    'cmd': get_command,
    'json': get_json,
    'ini': get_ini,
    'yaml': get_yaml,
    'env': get_env,
    }


def geturl(urlspec):
    for url in shsplit(urlspec):
        bits = url.split(':', 1)
        if len(bits) > 1 and bits[0] in URLTYPES:
            try:
                url = URLTYPES[bits[0]](bits[1])
                if url:
                    return url
            except (IOError, OSError, KeyError):
                pass
        else:
            return url
    abort("could not read database url from spec '%s'" % urlspec)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
