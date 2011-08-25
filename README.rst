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
    2011-11-11-my-beloved-migration/
      down.sql
      post-down.py
      pre-up.py
      up.sql

Those are main properties:

- extension is not important, except when it's ``.sql``. SQL scripts will be
  executed in context of your database, all other scripts will be executed just
  by starting them (shebang ``#!`` is your friend).
- you can have ``pre-`` and ``post-`` scripts.
