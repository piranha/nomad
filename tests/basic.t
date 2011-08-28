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

  $ nomad create 0-init
  $ echo "create table test (value varchar(10));" > 0-init/up.sql
  $ echo "drop table test" > 0-init/down.sql
  $ nomad ls
  \x1b[32m0-init\x1b[0m (esc)

Upgrading::

  $ nomad up -a
  applying upgrade 0-init:
    sql migration applied: up.sql
  $ sqlite3 test.db '.schema test'
  CREATE TABLE test (value varchar(10));
  $ sqlite3 test.db 'select name from nomad'
  0-init

Downgrading::

  $ nomad ls -a
  \x1b[35m0-init\x1b[0m (esc)
  $ nomad down 0-init
  applying downgrade 0-init:
    sql migration applied: down.sql
  $ sqlite3 test.db '.schema test'
  $ nomad ls
  \x1b[32m0-init\x1b[0m (esc)
