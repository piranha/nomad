.. -*- mode: rst -*-

=======
 Nomad
=======

Nomad is a simple migration application, which specifically takes into account
properties of development with DVCS and is completely agnostic from ORM or
whatever you are using to access your database. It uses simple SQL scripts to
migrate and can run pre- and post-processing routines written in any language
(Python, Ruby or whatever do you use for your application).

Tests status: |travis|, `changelog <https://github.com/piranha/nomad/blob/master/CHANGELOG.rst>`_

.. |travis| image:: https://travis-ci.org/piranha/nomad.png
   :target: https://travis-ci.org/piranha/nomad

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
    2011-11-13-third-migration/
      migration.ini
      1-pre.py
      2-up.sql
      3-post.sql.j2

Nomad uses table called ``nomad`` to track what was applied already. It's just a
list of applied migrations and dates when they were applied.

Interface
---------

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

I guess it's time to create new migration::

  $ nomad create 1-next -d 0-initial

``-d 0-initial`` means you want your ``1-next`` to depend on ``0-initial``. This
means Nomad will never apply ``1-next`` without applying ``0-initial``
first. You usually want to depend on migrations which created tables you're
going to alter, or just to make it easier - on the latest available migration.

Usage
-----

There are three types of migration files that ``nomad`` supports:

1.  Plain SQL files with the extension ``.sql``. Just put SQL commands you need
    to execute in the migration folder and they will be executed.
2.  Executable files. All file extensions are supported as long as the file
    is executable. These files must contain everything necessary to migrate
    your data, including setting up a database connection. ``nomad`` will pass
    all of the `Configuration`_ variables as environmental variables, prefixed
    with their section.
3.  Template files with the extension ``.j2``. These templates will be
    passed through the Jinja2 templating library. You must install the
    ``jinja2`` library for this functionality. The entire `Configuration`_ is
    available to the template files as a single dictionary. These could be
    useful if you are distributing an application where the end user needs to
    control some aspects of the migrations (ie. additional database users and
    passwords, additonal database names, etc.).

    ::

      # nomad.ini
      [db]
      another_user = reader
      another_pass = pass

    ::

      # migrations/0001-initial/up.sql.j2
      CREATE ROLE {{ db.another_user }};
      ALTER ROLE {{ db.another_user }} WITH NOSUPERUSER LOGIN PASSWORD '{{ db.another_pass }}' VALID UNTIL 'infinity';


Files inside of each migration folder are executed in lexographical order.


Configuration
-------------

Nomad reads database connection information from the ``[nomad]`` section of the
``nomad.ini`` file.

::

  [nomad]
  engine = sqla
  url = pgsql://user:password@host:port/db

Possible configuration options:

- ``engine`` (required) - SQL engine to use, possible options:

  - ``sqla`` - use SQLAlchemy as an adapter, supports everything SQLAlchemy supports
  - ``dbapi`` - use regular DB API, supports ``sqlite``, ``mysql`` and ``pgsql``

- ``url`` (required) - URL to database, takes multiple options, see format below
- ``path`` - path to migrations (default: directory with ``nomad.ini``)

Each migration has its own ``migration.ini`` file, which, by default, has a
single configuration option, ``nomad.dependencies``, defining which migration
(or migrations) this one depends.

You may add your own configuration variables to either the ``nomad.ini`` or
``migration.ini`` files and they will be available in your jinja2 templates
as a single dictionary and your executable files as environmental
variables.

Note that ini-files are parsed with extended interpolation (use it like
``${var}`` or ``${section.var}``).

A few predefined variables are provided to every migration:

- ``confpath`` - path to ``nomad.ini``
- ``confdir`` - path to directory, containing ``nomad.ini``
- ``dir`` - path to directory of migration


Example configuration:

+------------------+---------------------------+------------------------------+
|   configration   |         executable        |          template            |
+==================+===========================+==============================+
| ::               | ::                        | ::                           |
|                  |                           |                              |
|   [nomad]        |   NOMAD_ENGINE = sqla     |   nomad.engine = sqla        |
|   engine = sqla  |   NOMAD_URL = someurl     |   nomad.url = someurl        |
|   url = someurl  |                           |                              |
|                  |   FOO_BAR = zeta          |   foo.bar = zeta             |
|   [foo]          |                           |                              |
|   bar = zeta     |   NOMAD_CONFPATH = path   |   nomad.confpath = path      |
|                  |   NOMAD_CONFDIR = dir1    |   nomad.confdir = dir1       |
|                  |   NOMAD_DIR = dir2        |   nomad.dir = dir2           |
+------------------+---------------------------+------------------------------+


URL format
~~~~~~~~~~

Nomad can read connection url to database in a few various ways. ``nomad.url``
configuration option is a space separated list of descriptions of how Nomad can
obtain database connection url.

The easiest one is simply an url (like in config example). The others are:

- ``file:<path-to-file>`` - a path to file containing connection url
- ``env:<var-name>`` - an environment variable (do not prefix with `$`)
- ``py:<python.mod>:<variable.name>`` - a Python path to a module,
  containing a variable with connection url
- ``cmd:<cmd-to-execute>`` - command to execute to get connection url
- ``json:<path-to-file>:key.0.key`` - path to file with JSON and then path
  to a connection url within JSON object
- ``yaml:<path-to-file>:key.0.key`` - path to file with YAML and then path
  to a connection url within YAML object
- ``ini:<path-to-file>:<section.key>`` - path to INI file (parsed by
  configparser with extended interpolation) and then path to a connection url
  within this file

An example::

  [nomad]
  url =
    ini:${confdir}/../settings.ini:db.url
    json:${confdir}/../settings.json:db.url
    sqlite:///${confdir}/../local.db

Notice that in all cases in the end you have to return URL to a database in
normal format, i.e. ``dbtype://user:pass@host:port/dbname?options``.

``options`` are supported only by pgsql right now, whatever you put there, nomad
will do ``set ...`` before every migration. Note that if you do not supply
anything there, nomad sets ``statement_timeout`` to 1000 ms and ``lock_timeout``
to 500 ms by default.

Main ideas
----------

- There are no downgrades - nobody ever tests them, and they are rarely
  necessary. Just write an upgrade if you need to cancel something.
- You can write migration in whatever language you want, Nomad only helps you
  track applied migrations and dependencies.
- ``.sql`` is treated differently and executed against database, configured in
  ``nomad.ini``.
- Only ``.sql``, ``.j2``, and executable files (sorry, Windows! - though I am eager to
  hear ideas how to support it) are executed. You can put READMEs, pieces of
  documentation, whatever you want alongside your migrations.
- Name matters - everything is executed in order. Order is determined by using
  human sort (so that ``x-1.sql`` is earlier than ``x-10.sql``, you can always
  check sorting with ``ls --sort=version``).

.. end-writeup
