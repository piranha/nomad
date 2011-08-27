#!/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'nomad',
    description = 'simple sql migration tool to not drive you mad',
    long_description = read('README.rst'),
    license = 'BSD',
    version = '0.1',
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
        'Topic :: Database'
        ],

    install_requires = ['opster>=3.0'],
    packages = find_packages(),
    entry_points = {'console_scripts': ['nomad=nomad:app.dispatch']},
    platforms='any',
    )
