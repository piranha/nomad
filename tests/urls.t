.. -*- mode: rst -*-

Test different methods to acquire URLs.

Directly specified URL::

  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url = sqlite:///test.db
  > EOF
  $ nomad info
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
  $ PYTHONPATH=. nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from Python object using path::

  $ cat > nomad.ini <<EOF
  > [nomad]
  > engine = sqla
  > url-python = \${confdir}/somemod.py:dburl
  > EOF
  $ nomad info
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
  $ nomad info
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
  $ nomad info
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
  $ nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository


Nothing defined::

  $ echo '[nomad]\nengine=sqla' > nomad.ini
  $ nomad info
  \x1b[31mError: database url in <Repository: .> is not found\x1b[0m (esc)
  [1]
