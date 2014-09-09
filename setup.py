#!/usr/bin/env python

import sys, os, re
from setuptools import setup, find_packages


DEPS = ['opster>=4.0', 'termcolor']
extra = {}

if sys.version_info[0] >= 3:
    extra.update(dict(
        use_2to3=True,
        convert_2to3_doctests=['nomad/utils.py'],
    ))
else:
    DEPS.append('configparser')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def find_version():
    val, = re.findall(r"__version__ = '([^']+)'",
                      read('nomad/__init__.py'))
    return val


config = dict(
    name = 'nomad',
    description = 'simple sql migration tool to save you from becoming mad',
    long_description = read('README.rst'),
    license = 'ISC',
    version = find_version(),
    author = 'Alexander Solovyov',
    author_email = 'alexander@solovyov.net',
    url = 'http://github.com/piranha/nomad/',
    classifiers = [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control',
        'Topic :: Database'
        ],

    install_requires = DEPS,
    packages = find_packages(),
    entry_points = {'console_scripts': ['nomad=nomad:app.dispatch']},
    platforms='any',
    **extra)

if __name__ == '__main__':
    setup(**config)
