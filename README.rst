.. -*- mode: rst -*-

=======
 Nomad
=======

Nomad is a simple migration application, which specifically takes into account
properties of development with DVCS and is completely agnostic from ORM or
whatever you are using to access your database. It uses simple SQL scripts to
migrate and can run pre- and post-processing routines written in any language
(Python, Ruby or whatever do you use for your application).

.. image:: https://github.com/piranha/nomad/raw/master/docs/nomad.jpg

.. begin-writeup

Concept
-------

Nomad's migration store is a directory with ``nomad.ini`` and a other
directories inside. Each directory in it containing ``migration.ini`` is a
single migration and name of this child directory is an unique identifier of a
migration.

It looks like this::

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

And a `nomad.ini` could look like this::

  [nomad]
  engine = sqla
  url = pgsql://user:password@host:port/db

Possible options for ``engine``:

- ``sqla`` - use SQLAlchemy as an adapter, supports everything SQLAlchemy supports
- ``dbapi`` - use regular DB API, supports ``sqlite``, ``mysql`` and ``pgsql``

``url`` can be defined in a few various ways:

- ``url = <your-url-to-db>`` - just a static connection url
- ``url-file = <path-to-file>`` - a path to file containing connection url
- ``url-python = <python.mod.variable>`` - a Python path to a module, containing
  a variable with connection url
- ``url-command = <cmd-to-execute>`` - command line to execute to get connection
  url
- ``url-json = <path-to-file>:key.0.key`` - path to file with JSON and then path
  to a connection url inside JSON object


Main properties
---------------

- There is no downgrades - nobody ever tests them, they are rarely necessary
- You can write migration in whatever language you want, tool only helps you
  track applied migrations and dependencies
- ``.sql`` is treated differently and executed against database, configured in
  ``nomad.ini``
- Only ``.sql`` and executable files (sorry, Windows!) are executed. You can put
  READMEs, pieces of documentation, whatever you want alongside your migrations.
- Name matters - everything is executed in order. Order is determined by using
  human sort (so that ``x-1.sql`` is earlier than ``x-10.sql``, you can always
  check sorting with ``ls --sort=version``).

.. end-writeup
