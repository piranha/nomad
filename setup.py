#!/usr/bin/env python

import sys, os
from setuptools import setup, find_packages

PY3 = sys.version_info[0] >= 3

if PY3:
    from distutils.command.build_py import build_py_2to3 as build_py
else:
    from distutils.command.build_py import build_py


DEPS = ['opster>=4.0', 'termcolor']
if not PY3:
    DEPS.append('configparser')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


config = dict(
    name = 'nomad',
    description = 'simple sql migration tool to save you from becoming mad',
    long_description = read('README.rst'),
    license = 'BSD',
    version = '1.2',
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
    cmdclass={'build_py': build_py}
    )

if __name__ == '__main__':
    setup(**config)
