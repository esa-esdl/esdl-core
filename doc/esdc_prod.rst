===============
ESDC Production
===============

Overview
========

This section explains how the ESDC is produced and how it can be extended by new variables.

Generating a Cube
=================

After installing ``cablab-core`` as described in section :ref:`data_access_py_inst` you can run the
``cube-gen`` command-line tool:

.. code-block:: tcsh

    $ cube-gen -h

    CAB-LAB command-line interface, version 0.2.1rc0+1
    usage: cube-gen [-h] [-l] [-G] [-c CONFIG] [TARGET] [SOURCE [SOURCE ...]]

    Generates a new CAB-LAB data cube or updates an existing one.

    positional arguments:
      TARGET                data cube root directory
      SOURCE                <provider name>:dir=<directory>, use -l to list source
                            provider names

    optional arguments:
      -h, --help            show this help message and exit
      -l, --list            list all available source providers
      -G, --dont-clear-cache
                            do not clear data cache before updating the cube
                            (faster)
      -c CONFIG, --cube-conf CONFIG
                            data cube configuration file



Writing a new Cube Data Provider
================================

Running the new Cub Data Provider
=================================


Python Cube API Reference
=========================

.. automodule:: cablab
    :members:
