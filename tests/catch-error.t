.. -*- mode: rst -*-

Check that SQL errors are catched
=================================

Check that if SQL has an error, it's correctly rolled back and no information
about migration is inserted into a DB.

.. highlight:: console

Set up environment::

  $ NOMAD=${NOMAD:-nomad}
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url = sqlite:///test.db
  > EOF
  $ $NOMAD init
  Versioning table initialized successfully

Check that wrong migration is not applied::

  $ $NOMAD create 0-first
  $ echo "create table create (value qqq);" > 0-first/up.sql
  $ $NOMAD apply -a
  \x1b[31mError: cannot apply migration 0-first: (sqlite3.OperationalError) near "create": syntax error (esc)
  [SQL: create table create (value qqq);
  ]
  (Background on this error at: http://sqlalche.me/e/e3q8)\x1b[0m (esc)
  applying migration 0-first:
  [1]
  $ sqlite3 test.db 'select name from nomad'

Check that callable migrations are also checked for error::

  $ rm 0-first/up.sql
  $ cat > 0-first/up.sh <<EOF
  > #!/bin/sh
  > sqlite3 test.db 'create table create (value qqq);'
  > EOF
  $ chmod +x 0-first/up.sh
  $ $NOMAD apply -a
  Error: near "create": syntax error
  \x1b[31mError: cannot apply migration 0-first: script failed: up.sh\x1b[0m (esc)
  applying migration 0-first:
  [1]
  $ sqlite3 test.db 'select name from nomad'
