import sys
import re
import os

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


if __name__ == '__main__':
    import doctest
    doctest.testmod()
