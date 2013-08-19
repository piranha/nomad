.. -*- mode: rst -*-

URL acquiring test
==================

Test different methods to acquire URLs.

.. highlight:: console

Directly specified URL::

  $ NOMAD=${NOMAD:-nomad}
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url = sqlite:///test.db
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test.db>
    Uninitialized repository


Setup for Python object tests::

  $ cat > somemod.py <<EOF
  > dburl = 'sqlite:///test-py.db'
  > EOF


URL from Python object from ``sys.path``::

  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url-python = somemod:dburl
  > EOF
  $ PYTHONPATH=.:$PYTHONPATH $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from Python object using path::

  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url-python = \${confdir}/somemod.py:dburl
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from Python package::

  $ mkdir package
  $ mv somemod.py package/__init__.py
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url-python = \${confdir}/package:dburl
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from a file::

  $ echo 'sqlite:///test-file.db' > url
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url-file = url
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository


URL from a command::

  $ echo 'sqlite:///test-file.db' > url
  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url-command = cat url
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository

URL from JSON file::

  $ echo '{"db": [{"url": "sqlite:///test-file.db"}]}' > url.json
  $ cat > nomad.init <<EOF
  > [nomad]
  > engine = sqla
  > url-json = url.json:db.0.url
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository

URL from INI file::

  $ echo '[db]\nurl = sqlite:///test-file.db' > url.ini
  $ cat > nomad.init <<EOF
  > [nomad]
  > engine = sqla
  > url-ini = url.ini:db.url
  > EOF
  $ $NOMAD info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository


Nothing defined::

  $ echo '[nomad]\nengine=sqla' > nomad.ini
  $ $NOMAD info
  \x1b[31mError: database url in <Repository: .> is not found\x1b[0m (esc)
  [1]
