#!/usr/bin/env python

import os
from setuptools import setup
import nomad

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'nomad',
    description = 'simple sql migration application to not drive you mad',
    long_description = read('README'),
    license = 'BSD',
    version = nomad.__version__,
    author = nomad.__author__,
    author_email = nomad.__email__,
    url = 'http://github.com/piranha/nomad/',
    classifiers = [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Database'
        ],
    py_modules = ['nomad'],
    entry_points = {'console_scripts': ['nomad=nomad:main']},
    platforms='any',
    )
