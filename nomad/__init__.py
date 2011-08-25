#!/usr/bin/env python

import os.path as op
import sys

from opster import command, dispatch
from termcolor import cprint

from nomad.repo import Repository


@command()
def init(repo=None, **opts):
    '''Initialize database migration management
    '''
    repo.init_db()
    print 'Versioning table initialized successfully'

@command()
def list(repo=None,
         all=('a', False, 'show all migrations (default: only non-applied)'),
         **opts):
    '''List migrations
    '''
    for m in repo.available:
        if all and m in repo.applied:
            cprint(m, 'grey')
        else:
            cprint(m, 'green')

@command()
def create(name, repo=None, **opts):
    '''Create new migration
    '''
    pass

GLOBAL = [
    ('c', 'config', '', 'path to config file (default: $REPO/nomad.ini)'),
    ('D', 'define', {}, 'override config values'),
    ]

def getconfig(func):
    if func.__name__.startswith('help'):
        return func
    def inner(*args, **kwargs):
        if args:
            repopath = args[-1]
            args = args[:-1]
        else:
            repopath = ''

        if not kwargs.get('config'):
            kwargs['config'] = op.join(repopath, 'nomad.ini')

        try:
            repo = Repository(kwargs['config'], kwargs['define'])
        except IOError, e:
            print 'Error:', e
            sys.exit(1)

        kwargs['repo'] = repo
        return func(*args, **kwargs)
    return inner

def main():
    dispatch(globaloptions=GLOBAL, middleware=getconfig)

if __name__ == '__main__':
    main()
