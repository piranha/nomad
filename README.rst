.. -*- mode: rst -*-

=======
 Nomad
=======

Nomad is a simple migration application, which specifically takes into account
properties of development with DVCS and is completely agnostic from ORM or
whatever you are using to access your database. It uses simple SQL scripts to
migrate and can run pre- and post-processing routines written in any language
(Python, Ruby or whatever do you use for your application).

.. image:: https://travis-ci.org/piranha/nomad.png
   :target: https://travis-ci.org/piranha/nomad

.. image:: https://github.com/piranha/nomad/raw/master/docs/nomad.jpg

.. begin-writeup

Layout
-------

Nomad's migration store is a directory with ``nomad.ini`` and directories with
migrations inside. Each such directory must contain ``migration.ini`` to be
recognized as a migration and this directory name is an unique identifier of a
migration.

Your directory tree thus will look like this::

  migrations/
    nomad.ini
    2011-11-11-first-migration/
      migration.ini
      up.sql
    2011-11-12-second-migration/
      migration.ini
      1-pre.py
      2-up.sql
      3-post.py

Nomad uses table called ``nomad`` to track what was applied already. It's just a
list of applied migrations and dates when they were applied.

Usage
-----

To start working, create ``nomad.ini``, and initialize your database (I assume
it already exists)::

  $ nomad init

Then you can start creating your first migration::

  $ nomad create 0-initial

Put your ALTERs and CREATEs in ``0-initial/up.sql`` and apply a migration::

  $ nomad apply -a # or nomad apply 0-initial

Nomad should report which migrations it applied successfully, but you can check
status of that with ``nomad ls -a`` (or ``nomad ls`` to see only unapplied
migrations).

I guess it's time to create new migration:

  $ nomad create 1-next -d 0-initial

``-d 0-initial`` means you want your ``1-next`` to depend on ``0-initial``. This
means nomad will never apply ``1-next`` without applying ``0-initial``
first. You usually want to depend on migrations which created tables you're
going to alter, or just to make it easier - on the latest available migration.

Configuration
-------------

Nomad reads configuration from ``nomad.ini``, here is an example::

  [nomad]
  engine = sqla
  url = pgsql://user:password@host:port/db

Possible configuration options:

- ``engine`` (required) - SQL engine to use, possible options:
  - ``sqla`` - use SQLAlchemy as an adapter, supports everything SQLAlchemy supports
  - ``dbapi`` - use regular DB API, supports ``sqlite``, ``mysql`` and ``pgsql``
- ``url`` (required) - URL to database, takes multiple options, see format below
- ``path`` - path to migrations (default: directory with ``nomad.ini``)

Each migration has its own ``migration.ini`` file, which at the moment has
single configuration option, ``nomad.dependencies``, defining which migration
(or migrations) this one depends.

Note that ini-files are parsed with extended interpolation (use it like
``${var}`` or ``${section.var}``), two predefined variables are provided:

- ``confpath`` - path to ``nomad.ini``
- ``confdir`` - path to directory, containing ``nomad.ini``
- ``dir`` (migration only) - path to directory of migration

URL format
~~~~~~~~~~

Nomad can read connection url to database in a few various ways. ``nomad.url``
configuration option is a space separated list of descriptions of how nomad can
obtain database connection url.

The easiest one is simply an url (like in config example). The others are:

- ``file:<path-to-file>`` - a path to file containing connection url
- ``py:<python.mod>:<variable.name>`` - a Python path to a module,
  containing a variable with connection url
- ``cmd:<cmd-to-execute>`` - command line to execute to get connection
  url
- ``json:<path-to-file>:key.0.key`` - path to file with JSON and then path
  to a connection url within JSON object
- ``ini:<path-to-file>:<section.key>`` - path to INI file (parsed by
  configparser with extended interpolation) and then path to a connection url
  within this file

An example::

  [nomad]
  url =
    ini:${confdir}/../settings.ini:db.url
    json:${confdir}/../settings.json:db.url
    sqlite:///${confdir}/../local.db

Main properties
---------------

- There are no downgrades - nobody ever tests them, and they are rarely
  necessary. Just write an upgrade if you need to cancel something.
- You can write migration in whatever language you want, nomad only helps you
  track applied migrations and dependencies.
- ``.sql`` is treated differently and executed against database, configured in
  ``nomad.ini``.
- Only ``.sql`` and executable files (sorry, Windows! - I though am eager to
  ideas how to support it) are executed. You can put READMEs, pieces of
  documentation, whatever you want alongside your migrations.
- Name matters - everything is executed in order. Order is determined by using
  human sort (so that ``x-1.sql`` is earlier than ``x-10.sql``, you can always
  check sorting with ``ls --sort=version``).

.. end-writeup
