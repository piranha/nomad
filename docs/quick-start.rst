Quick Start
===========

To use nomad, you'll have to supply some basic configuration, in ``ini``
format::

    [nomad]
    engine = sqla
    url = sqlite:///test.db

.. note:: See :doc:`urls` about ways you can use to specify url of database.

Save this in a file named `nomad.ini`. The directory, containing this file, will
be your nomad environment. You can store file under any other name, but then
you'll have to supply it as an option to nomad calls (like ``nomad -c myconf.ini``).

Then initialize your database to be used with nomad::

    $ nomad init

This will create a table in your database with 2 fields - ``name`` and
``date``. This table is used then for tracking which migrations have been
applied already to this database.

And then you can create a migration::

    $ nomad create 2012-09-21-first

This will create directory with name ``2012-09-21-first`` and two files inside:
``migration.ini`` and ``up.sql``. Name of first file matters - it contains
information about dependencies of a migration (which can be passed as ``-d``
option to ``create`` command). Name of second file doesn't matter - any
``*.sql``, ``*.j2``, or executable files (file with executable bit set) will be
run. ``*.sql`` files are applied to database, ``*.j2`` files are applied to
the database after being passed through the ``jinja2`` template system, and
executable files (which can be your script to do something before or after
migration, or even migration itself) are just executed.

You can then list or apply migrations - just read help about them (``nomad help
ls`` or ``nomad help apply``). Also, reading :doc:`test-basic` can be helpful as
well.
