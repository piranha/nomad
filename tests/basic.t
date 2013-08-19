.. -*- mode: rst -*-

Basic nomad tests
=================

.. highlight:: console

First, set up environment::

  $ NOMAD=${NOMAD:-nomad}
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url = sqlite:///test.db
  > EOF

First, initialize migrations repository::

  $ $NOMAD init
  Versioning table initialized successfully
  $ sqlite3 test.db '.schema'
  CREATE TABLE nomad (
              name varchar(255) NOT NULL,
              date datetime NOT NULL
          );

First migration::

  $ $NOMAD create 0-first
  $ echo "create table test (value varchar(10));" > 0-first/up.sql
  $ $NOMAD ls
  \x1b[32m0-first\x1b[0m (esc)

Upgrading::

  $ $NOMAD apply -a
  applying migration 0-first:
    sql migration applied: up.sql
  $ sqlite3 test.db '.schema test'
  CREATE TABLE test (value varchar(10));
  $ sqlite3 test.db 'select name from nomad'
  0-first

Dependencies::

  $ $NOMAD create 1-second
  $ $NOMAD create 2-third -d 1-second
  $ $NOMAD ls
  \x1b[32m1-second\x1b[0m (esc)
  \x1b[32m2-third\x1b[0m (1-second) (esc)
  $ $NOMAD apply 2-third
  applying migration 1-second:
    sql migration applied: up.sql
  applying migration 2-third:
    sql migration applied: up.sql
