import sys
import re
import os, os.path as op
import shlex
import imp
from subprocess import Popen, PIPE

from termcolor import cprint


NUM_RE = re.compile('(\d+)')


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
    cprint('Error: %s' % msg, 'red')
    sys.exit(code)


def humankey(fn):
  '''Turn a string into a list of substrings and numbers.

  This can be used as a key function for ``sorted``::

    >>> s = lambda *x: list(sorted(x, key=humankey))
    >>> print s('up-1', 'up-5', 'up-15', 'up-50')
    ['up-1', 'up-5', 'up-15', 'up-50']
    >>> print s('up-1.sql', 'up.sql', 'up1.sql')
    ['up.sql', 'up1.sql', 'up-1.sql']
    >>> print s('up.rb', 'up.py') # check extension sorting
    ['up.py', 'up.rb']
  '''
  fn, ext = os.path.splitext(fn)
  return [int(s) if s.isdigit() else s for s in NUM_RE.split(fn)], ext


def humansort(l):
    return list(sorted(l, key=humankey))


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


def geturl(repo):
    if 'nomad.url' in repo:
        return repo['nomad.url']
    if 'nomad.url-python' in repo:
        pypath, attr = repo['nomad.url-python'].split(':')
        if '/' in pypath or pypath.endswith('.py'):
            # load from file
            mod = loadpath(pypath)
        else:
            # load from sys.path
            mod = __import__(pypath, {}, {}, [''])
        return reduce(lambda x, y: getattr(x, y), attr.split('.'), mod)
    if 'nomad.url-file' in repo:
        try:
            return file(repo['nomad.url-file']).read().strip()
        except IOError, e:
            abort(e)
    if 'nomad.url-command' in repo:
        try:
            p1 = Popen(shlex.split(repo['nomad.url-command']), stdout=PIPE)
        except OSError, e:
            abort(e)
        return p1.communicate()[0].strip()
    abort('cannot find an url in %s' % repo)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
