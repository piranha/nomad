.. -*- mode: rst -*-

First, set up environment::

  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url = sqlite:///test.db
  > EOF

First, initialize migrations repository::

  $ nomad init
  Versioning table initialized successfully
  $ sqlite3 test.db '.schema'
  CREATE TABLE nomad (
              name varchar(255) NOT NULL,
              date datetime NOT NULL
          );

First migration::

  $ nomad create 0-first
  $ echo "create table test (value varchar(10));" > 0-first/up.sql
  $ nomad ls
  \x1b[32m0-first\x1b[0m (esc)

Upgrading::

  $ nomad apply -a
  applying migration 0-first:
    sql migration applied: up.sql
  $ sqlite3 test.db '.schema test'
  CREATE TABLE test (value varchar(10));
  $ sqlite3 test.db 'select name from nomad'
  0-first
