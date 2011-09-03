.. -*- mode: rst -*-

=======
 Nomad
=======

Nomad is a simple migration application, which specifically takes into account
properties of development with DVCS and is completely agnostic from ORM or
whatever you are using to access your database. It uses simple SQL scripts to
migrate and can run pre- and post-processing routines written in any language
(Python, Ruby or whatever do you use for your application).

.. image:: https://github.com/piranha/nomad/raw/master/nomad.jpg

Concept
-------

Nomad's migration store is a directory with ``nomad.ini`` and a other
directories inside. Each directory in it containing ``migration.ini`` is a
single migration and name of child directory is an identifier of migration.

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

Main properties:

- There is no downgrades - nobody ever tests them, they are rarely necessary
- You can write migration in whatever language you want, tool only helps you
  track applied migrations and dependencies
- ``.sql`` is treated differently and executed against database, configured in
  ``nomad.ini``
- Only ``.sql`` and executable files are executed. You can put READMEs, pieces
  of documentation, whatever you want alongside your migrations.
- Name matters - everything is executed in order. Order is determined by using
  human sort (so that ``x-1.sql`` is earlier than ``x-10.sql``, you can always
  check sorting with ``ls --sort=version``).
