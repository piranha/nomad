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

Natural sorting works::

  $ $NOMAD create 3-fourth
  $ $NOMAD create 10-eleventh
  $ $NOMAD ls
  \x1b[32m3-fourth\x1b[0m (esc)
  \x1b[32m10-eleventh\x1b[0m (esc)

No problems with trailing slash that can easily occur from autocomplete::

  $ $NOMAD apply 3-fourth/
  applying migration 3-fourth:
    sql migration applied: up.sql
  $ $NOMAD apply 3-fourth
  \x1b[31mError: migration 3-fourth is already applied\x1b[0m (esc)
  [1]

Dependencies have no sense when applying all migrations::

  $ $NOMAD create 11-twelfth -d 10-eleventh
  $ $NOMAD apply -a
  applying migration 10-eleventh:
    sql migration applied: up.sql
  applying migration 10-eleventh:
    sql migration applied: up.sql
  applying migration 11-twelfth:
    sql migration applied: up.sql
