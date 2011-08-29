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

  $ sed -i '' -e 's/url.*/url-python = somemod:dburl/' nomad.ini
  $ PYTHONPATH=. nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from Python object using path::

  $ sed -i '' -e 's/somemod/${confdir}\/somemod.py/' nomad.ini
  $ nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from Python package::

  $ mkdir package
  $ mv somemod.py package/__init__.py
  $ sed -i '' -e 's/somemod.py/package\//' nomad.ini
  $ nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-py.db>
    Uninitialized repository


URL from a file::

  $ echo 'sqlite:///test-file.db' > url
  $ sed -i '' -e 's/url.*/url-file = url/' nomad.ini
  $ nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository


URL from a command::

  $ sed -i '' -e 's/url.*/url-command = cat url/' nomad.ini
  $ nomad info
  <Repository: .>:
    <SAEngine: sqlite:///test-file.db>
    Uninitialized repository


Nothing defined::

  $ echo '[nomad]\nengine=sqla' > nomad.ini
  $ nomad info
  \x1b[31mError: cannot find an url in <Repository: .>\x1b[0m (esc)
  [1]
