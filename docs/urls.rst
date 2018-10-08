================
 Acquiring URLs
================

Nomad supports few different ways of specification how it should connect to
database.

There are two parameters it has to acquire: ``engine`` and ``url``.

Engine is specified as a string. Supported engines right now consist of
``dbapi`` and ``sqla``. Both of them support SQLite, MySQL and PostgreSQL
databases, the first one requiring only db api modules and second one requiring
SQLAlchemy library.

URL can be specified in few different ways:

 - ``url`` - just a string, path like ``sqlite:///test.db`` (*relative* path) or ``sqlite:////path/to/test.db`` or ``mysql://user:pass@host/db``. Note how you end up with **4** slashes when using absolute path.

 - ``url-python`` - taking variable from Python module, has two approaches to
   fetching python module:

   - From ``sys.path``, when it looks like one: ``yourapp.settings:dburl``

   - From filesystem, when it looks like path to file: ``../settings.py:dburl``

 - ``url-file`` - taking contents of a file: ``../dburl.txt``

 - ``url-command`` - taking output of a command: ``grep mysql ../settings.txt``


.. note:: Look at :doc:`test-urls` to see how various options are used.
