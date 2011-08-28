.. -*- mode: rst -*-

=======
 Nomad
=======

Nomad is a simple migration application, which specifically takes into account
properties of development with DVCS and is completely agnostic from ORM or
whatever you are using to access your database. It uses simple SQL scripts to
migrate and can run pre- and post-processing routines written in any language
(Python, Ruby or whatever do you use for your application).


Concept
-------

Nomad's migration store is a directory. Every directory in it represents a
single migration, with name of this directory used as an actual identificator of
this migration.

So directory structure looks like this::

  migrations/
    2011-11-11-first-migration/
      down.sql
      up.sql
    2011-11-12-second-migration/
      down-0.py
      down-1.sql
      up.sql
      up-1.py

Those are main properties:

- Extension is not important, except when it's ``.sql``. SQL scripts will be
  executed in context of your database, all other scripts will be executed just
  by starting them (shebang ``#!`` is your friend, and keep it executable).
- Name matters - it should start with ``up`` and ``down`` respectively for
  upgrade and downgrade, and everything is executed in order. Order is
  determined by using human sort (so that ``up-1.sql`` is earlier than
  ``up-10.sql``, you can always check sorting with ``ls --sort=version``).
