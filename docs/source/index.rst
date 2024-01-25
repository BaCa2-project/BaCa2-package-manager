BaCa2 Package Manager technical documentation
---------------------------------------------

BaCa2 package manager is a part of `BaCa2 Project <https://github.com/BaCa2-project>`_. This package is used to
manage files and directories in which packages data is stored. It gives high-level interface to
interfere with programing tasks definitions. Package manager is prepared to work with BaCa2 web app,
but is also given as pip package, and makes file operations related with BaCa2 workflow much easier.

Possibilities of package manager can be grouped into 4 categories:

1. `Manager` - main module, responsible for files management.
2. `Judge manager` - module responsible for judging workflows definitions.
3. `Zipper` - module responsible for safe package unzipping.
4. `Broker communication` - definition of communication agreement between BaCa2 and brokers.

.. note::

      In actual version of BaCa2 ``judge manager`` is not used. It will change in the future.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
