=================
 Nomad Changelog
=================

1.13
----

 - Fix bug when applying multiple migrations and one had some dependency, it
   could try to apply this dependency even in case when it was already applied
 - Unified codebase for both Python 2 & 3 (no more 2to3)

1.12
----

 - Handle trailing slashes (when you use shell completion and are lazy, you can
   get them in DB)
 - Pass all the configuration values from ``nomad.ini`` to executable migration
   scripts

1.11
----

 - Do not abort on migrations not on disk

1.10
----

- Can "fake" apply a migration
- Can parse urlencoded database urls
- Improvements in error reporting

1.9
---

- Postgresql urls can now use any of ``pgsql://``, ``postgresql://`` and ``postgres://``
- Improvements in error reporting

1.8
---

- `-p` option for `create` command to prefix name with current date
- Catch when migration scripts exit with non-zero status
- Improvements in error reporting

1.7
---

- Ability to pass additional environment to migration scripts
- Improvements in error reporting


1.6
---

- Ability to get DB url from environment
- `nomad.ini` is no more required for `version` command

Ancient history
---------------

Please research SCM logs. :)

