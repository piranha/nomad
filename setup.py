#!/usr/bin/env python

import sys, os, re
from setuptools import setup, find_packages


DEPS = ['opster>=4.0', 'termcolor']

if sys.version_info[0] < 3:
    DEPS.append('configparser')


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as handler:
        return handler.read()

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
    platforms='any')


if __name__ == '__main__':
    setup(**config)
