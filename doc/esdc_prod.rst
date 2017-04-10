.. _cablab/providers/ozone.py: https://github.com/CAB-LAB/cablab-core/blob/master/cablab/providers/ozone.py
.. _cube-config: https://github.com/CAB-LAB/cube-config

===============
ESDC Generation
===============

This section explains how a ESDC is generated and how it can be extended by new variables.

Command-Line Tool
=================

To generate new data cubes or to update existing ones a dedicated command-line tool ``cube-gen`` is used.

After installing ``cablab-core`` as described in section :ref:`data_access_py_inst`, try:

.. code-block:: bash

    $ cube-gen --help

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

The ``list`` option lists all currently installed *source data providers*:

.. code-block:: bash

    $ cube-gen --list

    ozone -> cablab.providers.ozone.OzoneProvider
    net_ecosystem_exchange -> cablab.providers.mpi_bgc.MPIBGCProvider
    air_temperature -> cablab.providers.air_temperature.AirTemperatureProvider
    interception_loss -> cablab.providers.gleam.GleamProvider
    transpiration -> cablab.providers.gleam.GleamProvider
    open_water_evaporation -> cablab.providers.gleam.GleamProvider
    ...

Source data providers are the pluggable software components used by ``cube-gen`` to read data from a
source directory and transform it into a common data cube structure. The list above shows the mapping from
short names to be used by the ``cube-gen`` command-line to the actual Python code, e.g. for ``ozone``,
the ``OzoneProvider`` class of the `cablab/providers/ozone.py`_ module is used.

The common cube structure is established by a *cube configuration* file provided by the ``cube-config`` option.
Here is the configuration file that is used to produce the low-resolution ESDC. It will produce a 0.25 degrees global
cube that whose source data will aggregated/interpolated to match 8 day periods and then resampled to match
1440 x 720 spatial grid cells:

.. code-block:: text

    model_version = '0.2.4'
    spatial_res = 0.25
    temporal_res = 8
    grid_width = 1440
    grid_height = 720
    start_time = datetime.datetime(2001, 1, 1, 0, 0)
    end_time = datetime.datetime(2012, 1, 1, 0, 0)
    ref_time = datetime.datetime(2001, 1, 1, 0, 0)
    calendar = 'gregorian'
    file_format = 'NETCDF4_CLASSIC'
    compression = False

To create or update a cube call the ``cube-gen`` tool with the configuration and the cube data provider(s).
The cube data providers can have parameters on their own. All current providers have the ``dir`` parameter
indicating the source data directory but this is not a rule. Other providers which read from
multivariate sources also have a ``var`` parameter to indicate which variable of many possible should be used.

.. code-block:: bash

    $ cube-gen mycube -c mycube.config ozone:dir=/path/to/ozone/netcdfs

will create the cube ``mycube`` in current directory using the ``mycube.config`` configuration and add a single
variable ``ozone`` from source NetCDF files in  ``/path/to/ozone/netcdfs``.

Note, the GitHub repository `cube-config`_ is used to keep the configurations of individual ESDC versions.

Writing a new Provider
======================

In order to add new source data for which there is no source data provider yet, you can write your own.

Make sure ``cablab-core`` is installed as described in section :ref:`data_access_py_inst` above.

If your source data is NetCDF, writing a new provider is easy. Just copy one of the existing providers,
e.g. `cablab/providers/ozone.py`_ and start adopting the code to your needs.

For source data other than NetCDF, you will have to write a provider from scratch by implementing
the :py:class:`cablab.CubeSourceProvider` interface or by extending the :py:class:`cablab.BaseCubeSourceProvider`
which is usually easier. Make sure you adhere to the contract described in the documentation of the respective class.

To run your provider you will have to register it in the ``setup.py`` file. Assuming your provider is called
``sst`` and your provider class is ``SeaSurfaceTemperatureProvider`` located in
``myproviders.py``, then the ``entry_points`` section of the ``setup.py`` file should reflect this as follows:

.. code-block:: python

    entry_points={
        'cablab.source_providers': [
            'burnt_area = cablab.providers.burnt_area:BurntAreaProvider',
            'c_emissions = cablab.providers.c_emissions:CEmissionsProvider',
            'ozone = cablab.providers.ozone:OzoneProvider',
            ...
            'sst = myproviders:SeaSurfaceTemperatureProvider',

To run it:

.. code-block:: bash

    $ cube-gen mycube -c mycube.config sst:dir=/path/to/sst/netcdfs


Sharing a Provider
==================

If you plan to distribute and share your provider, you should create your own Python module separate
from ``cablab-core`` with a dedicated ``setup.py`` with only your providers listed in the ``entry_points`` section.
Other users may then install your module on top of an ``cablab-core`` to make use of your plugin.


Python Cube API Reference
=========================

.. automodule:: cablab
    :members:
