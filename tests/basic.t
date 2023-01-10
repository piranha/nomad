.. -*- mode: rst -*-

Basic nomad tests
=================

.. highlight:: console

First, set up environment::

  $ export FORCE_COLOR=1
  $ NOMAD=${NOMAD:-nomad}
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url = sqlite:///test.db
  > [foo]
  > bar = zeta
  > EOF

First, initialize migrations repository::

  $ $NOMAD init
  Versioning table initialized successfully
  $ sqlite3 -noheader -list test.db '.schema'
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
  $ sqlite3 -noheader -list test.db '.schema test'
  CREATE TABLE test (value varchar(10));
  $ sqlite3 -noheader -list test.db 'select name from nomad'
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

Dependencies should not break when applying all migrations::

  $ $NOMAD create 11-twelfth -d 10-eleventh
  $ $NOMAD apply -a
  applying migration 10-eleventh:
    sql migration applied: up.sql
  applying migration 11-twelfth:
    sql migration applied: up.sql

It's possible to insert % into a db::
  $ $NOMAD create 12-thirteen
  $ echo "insert into test values ('test%');" > 12-thirteen/up.sql
  $ $NOMAD apply -a
  applying migration 12-thirteen:
    sql migration applied: up.sql
  $ sqlite3 -noheader -list test.db 'select * from test'
  test%

Using configuration templates
  $ $NOMAD create 13-fourteen
  $ mv 13-fourteen/up.sql 13-fourteen/up.sql.j2
  $ echo "create table {{ foo.bar }} (value varchar(10));" > 13-fourteen/up.sql.j2
  $ $NOMAD create 14-fifteen
  $ mv 14-fifteen/up.sql 14-fifteen/up.sql.j2
  $ echo "insert into {{ foo.bar }} values ('test');" >> 14-fifteen/up.sql.j2
  $ $NOMAD apply -a
  applying migration 13-fourteen:
    sql template migration applied: up.sql.j2
  applying migration 14-fifteen:
    sql template migration applied: up.sql.j2
  $ sqlite3 -noheader -list test.db 'select value from zeta'
  test
