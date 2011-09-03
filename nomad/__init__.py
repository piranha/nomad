#!/usr/bin/env python

import os, os.path as op

from opster import Dispatcher
from termcolor import cprint, colored

from nomad.repo import Repository
from nomad.engine import DBError
from nomad.utils import abort, NomadError


GLOBAL = [
    ('c', 'config', 'nomad.ini', 'path to config file'),
    ('D', 'define', {}, 'override config values'),
    ]

def getconfig(func):
    if func.__name__.startswith('help'):
        return func
    def inner(*args, **kwargs):
        try:
            repo = Repository(kwargs['config'], kwargs['define'])
        except (IOError, NomadError), e:
            abort(e)

        return func(repo=repo, *args, **kwargs)
    return inner

app = Dispatcher(globaloptions=GLOBAL, middleware=getconfig)


@app.command()
def init(**opts):
    '''Initialize database migration management
    '''
    opts['repo'].init_db()
    print 'Versioning table initialized successfully'


@app.command(aliases=('ls',))
def list(all=('a', False, 'show all migrations (default: only non-applied)'),
         **opts):
    '''List migrations
    '''
    repo = opts['repo']
    for m in repo.available:
        if m in repo.applied:
            if all:
                cprint(m, 'magenta')
        else:
            out = colored(m, 'green')
            deps = []
            for dep in m.dependencies:
                if dep not in repo.applied:
                    deps.append(dep)
            if deps:
                out += ' (%s)' % ', '.join(map(str, deps))
            print out


@app.command()
def create(name,
           dependencies=('d', [], 'migration dependencies'),
           **opts):
    '''Create new migration
    '''
    repo = opts['repo']
    try:
        deps = map(repo.get, dependencies)
    except NomadError, e:
        abort(e)

    path = op.join(repo.path, name)
    try:
        os.mkdir(path)
    except OSError, e:
        if e.errno == 17:
            abort('directory %s already exists' % path)
        raise

    with file(op.join(path, 'migration.ini'), 'w') as f:
        f.write('[nomad]\n')
        f.write('dependencies = %s\n' % ', '.join(d.name for d in deps))
    with file(op.join(path, 'up.sql'), 'w') as f:
        f.write('-- SQL ALTER statements for database migration\n')


@app.command()
def apply(all=('a', False, 'apply all available migrations'),
       *names,
       **opts):
    '''Apply migration and all of it dependencies
    '''
    repo = opts['repo']
    if names:
        migrations = map(repo.get, names)
    elif all:
        migrations = [x for x in repo.available if x not in repo.applied]
    else:
        abort('Supply names of migrations to apply')

    for m in migrations:
        if m in repo.applied:
            abort('migration %s is already applied' % m)
    for m in migrations:
        if not m.applied:
            m.apply()


@app.command()
def info(**opts):
    '''Show information about repository
    '''
    repo = opts['repo']
    print '%s:' % repo
    print '  %s' % repo.engine
    try:
        print '  %s applied' % len(repo.applied)
        print '  %s unapplied' % (len(repo.available) - len(repo.applied))
    except DBError:
        print '  Uninitialized repository'


if __name__ == '__main__':
    app.dispatch()
