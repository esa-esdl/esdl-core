.. _NetCDF: https://www.unidata.ucar.edu/software/netcdf/docs/
.. _Web Coverage Service (WCS): http://www.opengeospatial.org/standards/wcs
.. _OPeNDAP: https://www.opendap.org/

.. _Jupyter: http://jupyter.org/about.html
.. _JupyterHub: https://jupyterhub.readthedocs.io/en/latest/
.. _Notebooks: https://jupyter.readthedocs.io/en/latest/index.html
.. _Conda: https://conda.io/docs/intro.html
.. _Anaconda: https://www.continuum.io/downloads
.. _Miniconda: https://conda.io/miniconda.html
.. _xarray.Dataset: http://xarray.pydata.org/en/stable/data-structures.html#dataset
.. _xarray.DataArray: http://xarray.pydata.org/en/stable/data-structures.html#dataarray
.. _Numpy ndarray: http://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html

.. _ESDC E-Laboratory: http://cablab.earthsystemdatacube.net/cablab-jupyterhub/
.. _ESDC THREDDS server: http://www.brockmann-consult.de/cablab-thredds/catalog.html
.. _ESDC FTP server: ftp://ftp.brockmann-consult.de/cablab02/cablab-datacube-0.2.4/
.. _ESDC community repository: https://github.com/CAB-LAB/cablab-shared
.. _ESDC community notebooks: https://github.com/CAB-LAB/cablab-shared/tree/master/notebooks


===========
ESDC Access
===========

As introduced in the last section, the ESDC physically consists of a set of NetCDF_ files on disk,
which can be accessed in a number of different ways which are described in this section.

Download ESDC Data
==================

The simplest approach to access the ESDC data is downloading it to you computer using the `ESDC FTP server`_.

Since the ESDC is basically a directory of NetCDF_ files, you can use a variety of software packages and programming
languages to access the data. In each cube directory, you find a text file ``cube.config`` which describes the overall
data cube layout.

Within the :ref:`esdc_project`, dedicated data access packages have been developed for the Python and Julia
programming languages. These packages "understand" the ESDC's ``cube.config`` files and represent the cube data
by a convenient data structures. The section :ref:`data_access_py` describes how to access the data from Python.

OPeNDAP and WCS Services
========================

The ESDC' data variables can also be accessed via a dedicated `ESDC THREDDS server`_.

The server supports the `OPeNDAP`_ and OGC-compliant `Web Coverage Service (WCS)`_ data access protocols.
You can use it for accessing subsets of the ESDC's data variables and also for visual exploration of the data,
and finally for downloading the data as a NetCDF_ file or of plain text.

Depending on the variable subsets, and the region and time period of interest, the transferred data volume
might be much lower than a complete download of the ESDC via FTP. However, the disadvantage of using OPeNDAP
and WCS is that the actual structure of the ESDC gets lost, so that it can't be accessed anymore using
the aforementioned ESDC Python/Julia data access packages.

E-Laboratory
============

A dedicated `ESDC E-Laboratory`_ has been developed to access the ESDC data via distributed
`Jupyter`_ `Notebooks`_ for Julia and Python. This is the most resource efficient and convenient
way of exploring the ESDC.

These notebooks have direct access to the ESDC data so there is no need to download it.
In addition they provide the ESDC Python and Julia APIs comprising
the Data Access API and the Data Analytics Toolkit.

The E-Laboratory provides some example notebooks in the shared `ESDC community repository`_.

The E-Laboratory is based on the JupyterHub_ platform and currently comprises three 16-core computers
running in a Cloud environment.

.. _data_access_py:

Using Python
============

.. _data_access_py_inst:

Installation
------------

Note: if you use the E-Laboratory you don't need to install any additional packages for accessing the data.
This section is only relevant if you've downloaded a ESDC instance to your local computer.

While in principle the NetCDF_ files comprising the ESDC can be used with any tool of choice, we
developed specifically tailored Data Access APIs for Python 3.X and Julia.
Furthermore, a set of high-level routines for data analysis, the Data Analytics Toolkit, greatly facilitates
standard operations on the large amount of data in the ESDC.
While in the E-laboratory, the Data Access API and the DAT are already pre-installed,
the user has to download and install the cube library when working on a local computer.

The ESDC Python package has been developed against latest Anaconda_ / Miniconda_ distributions and uses their
Conda_ package manager.

To get started on your local computer with Python, clone the `cablab-core`
repository from `<https://github.com/CAB-LAB>`_:

.. code-block:: bash

    git clone https://github.com/CAB-LAB/cablab-core

The following command will create a new Python 3.5 environment named ``esdc`` with all required dependencies, namely

    * dask >= 0.14
    * gridtools >= 0.1 (from Conda channel ``forman``)
    * h5netcdf >= 0.3
    * h5py >= 2.7
    * netcdf4 >= 1.2
    * scipy >= 0.16
    * scikit_image >= 0.11
    * matplotlib >= 2.0
    * xarray >= 0.9

.. code-block:: bash

    $ conda env create environment.yml

To active new Python environment named ``esdc`` you must source on Linux/Darwin

.. code-block:: bash

    $ source activate.sh esdc

on Windows:

.. code-block:: bat

    > activate esdc

Now change into new folder ``cablab-core`` and install the ``cablab`` Python package using the ``develop`` target:

.. code-block:: bash

    $ cd cablab-core
    $ python setup.py develop

After download of a ESDC including the corresponding ``cube.config`` file and successful installation of the ESDC,
you are ready to explore the data in the ESDC using the :ref:`data_access_py`.

.. data_access_py

Usage
-----

The following example code demonstrates how to access a locally stored ESDC, query its content, and get
data chunks of different sizes for further analysis.

**Open a cube**

.. code:: python

    from cablab import Cube
    from datetime import datetime
    import numpy as np

    cube = Cube.open("/path/to/datacube")


Note, in order to work properly the ``/path/to/datacube/`` passed to ``Cube.open()``
must be the path to an existing ESDC cube directory which contains a valid configuration file named ``cube.config``.
It contains essential metadata about the ESDC to be opened.


.. code:: python

    cube.data.variable_names

.. code-block:: python

    ['aerosol_optical_thickness_1610',
     'aerosol_optical_thickness_550',
     'aerosol_optical_thickness_555',
     'aerosol_optical_thickness_659',
     'aerosol_optical_thickness_865',
     'air_temperature_2m',
     'bare_soil_evaporation',
     'black_sky_albedo',
     'burnt_area',
     'country_mask',
     'c_emissions',
     ...]

After successful opening the ESDC, chunks of data or the entire data set can be accessed via the
``dataset()`` and ``get()`` functions. The first returns a `xarray.Dataset`_ object in which all
cube variables are represented as `xarray.DataArray`_ objects. More about these objects can also be
found in :doc:`dat_python` section. The second function can be used to read subsets of the data.
In contrast it returns a list of `Numpy ndarray`_ arrays, one for each requested variable.

The corresponding API for Julia is very similar and illustrated in :doc:`dat_julia`.

**Accessing the cube data using the ``dataset()`` function**

The ``cube.data.dataset()`` has an optional argument which is a list of variable names to include in the returned
`xarray.DataArray`_ object. If omitted, all variables will be included. Note it can take up to a few seconds to open
generate the dataset object with all variables.

.. code:: python

    ds = cube.data.dataset()
    ds

.. parsed-literal::

    <`xarray.Dataset`_>
    Dimensions:                            (bnds: 2, lat: 720, lon: 1440, time: 506)
    Coordinates:
      * time                               (time) datetime64[ns] 2001-01-05 ...
      * lon                                (lon) float32 -179.875 -179.625 ...
        lon_bnds                           (lon, bnds) float32 -180.0 -179.75 ...
        lat_bnds                           (lat, bnds) float32 89.75 90.0 89.5 ...
      * lat                                (lat) float32 89.875 89.625 89.375 ...
        time_bnds                          (time, bnds) datetime64[ns] 2001-01-01 ...
    Dimensions without coordinates: bnds
    Data variables:
        aerosol_optical_thickness_1610     (time, lat, lon) float64 nan nan nan ...
        aerosol_optical_thickness_550      (time, lat, lon) float64 nan nan nan ...
        aerosol_optical_thickness_555      (time, lat, lon) float64 nan nan nan ...
        aerosol_optical_thickness_659      (time, lat, lon) float64 nan nan nan ...
        aerosol_optical_thickness_865      (time, lat, lon) float64 nan nan nan ...
        air_temperature_2m                 (time, lat, lon) float64 243.4 243.4 ...
        bare_soil_evaporation              (time, lat, lon) float64 nan nan nan ...
        black_sky_albedo                   (time, lat, lon) float64 nan nan nan ...
        burnt_area                         (time, lat, lon) float64 0.0 0.0 0.0 ...
        country_mask                       (time, lat, lon) float64 nan nan nan ...
        ...

.. code:: python

    lst = ds['land_surface_temperature']
    lst

.. parsed-literal::

    <`xarray.DataArray`_ 'land_surface_temperature' (time: 506, lat: 720, lon: 1440)>
    dask.array<concatenate, shape=(506, 720, 1440), dtype=float64, chunksize=(46, 720, 1440)>
    Coordinates:
      * time     (time) datetime64[ns] 2001-01-05 2001-01-13 2001-01-21 ...
      * lon      (lon) float32 -179.875 -179.625 -179.375 -179.125 -178.875 ...
      * lat      (lat) float32 89.875 89.625 89.375 89.125 88.875 88.625 88.375 ...
    Attributes:
        url:            http://data.globtemperature.info/
        long_name:      land surface temperature
        source_name:    LST
        standard_name:  surface_temperature
        comment:        Advanced Along Track Scanning Radiometer pixel land surfa...
        units:          K

The variable ``lst`` can now be used like a `Numpy ndarray`_. Howver, using ``xarray`` there are a
number of more convenient data access methods that take care of the actual coordinates provided for every
dimenstion. For example, the ``sel()`` method can be used to extract slices and subsets from a data array.
Here a point is extract from ``lst``, and the result is a 1-element data array:

.. code:: python

    lst_point = lst.sel(time='2006-06-15', lat=53, lon=11, method='nearest')
    lst_point

.. parsed-literal::
    <xarray.DataArray 'land_surface_temperature' ()>
    dask.array<getitem, shape=(), dtype=float64, chunksize=()>
    Coordinates:
        time     datetime64[ns] 2006-06-14
        lon      float32 11.125
        lat      float32 53.125
    Attributes:
        url:            http://data.globtemperature.info/
        long_name:      land surface temperature
        source_name:    LST
        standard_name:  surface_temperature
        comment:        Advanced Along Track Scanning Radiometer pixel land surfa...
        units:          K

Data arrays also have a handy ``plot()`` method. Try:

.. code:: python

    lst.sel(lat=53, lon=11, method='nearest').plot()
    lst.sel(time='2006-06-15', method='nearest').plot()
    lst.sel(lon=11, method='nearest').plot()
    lst.sel(lat=53, method='nearest').plot()

**Accessing the cube data using the ``get()`` function**

The ``cube.data.get()`` method expects up to four arguments:

.. code-block::

    cube_data.get(variable=None, time=None, latitude=None, longitude=None)

with

    * *variable:* a variable index or name or an iterable returning multiple
      of these (var1, var2, ...
    * *time:* a single datetime.datetime object or a 2-element iterable
      (time\_start, time\_end)
    * *latitude:* a single latitude value or a 2-element iterable
      (latitude\_start, latitude\_end)
    * *longitude:* a single longitude value or a 2-element iterable
      (longitude\_start, longitude\_end)
    * *return:* a dictionary mapping variable names --> data arrays of
      dimension (time, latitude, longitude)


**Getting a chunk of 1 variable, all available time steps, and 40 x 40 spatial grid points:**

.. code:: python

    precip_chunk = cube_data.get('Precip',None,(0,10),(0,10))
    np.array(precip_chunk).shape

.. parsed-literal::

    (1, 457, 40, 40)

**Getting time-series at a single point of all variables for the entire period:**

.. code:: python

    time_series = cube_data.get(None,None,51.34,8.23)
    [var.shape for var in time_series]

.. parsed-literal::

    [(457,), (457,), (457,), (457,), (457,), (368,)]

**Getting a complete global image of a variable at a specific time**

.. code:: python

    Emission_single_image = cube_data.get('Emission', datetime(2002,1,1))
    np.array(Emission_single_image).shape

.. parsed-literal::

    (1, 720, 1440)

.. code:: python

    cube.close()

Note that the available memory limits the maximum size of the data chunk that can be simultaneously loaded,
e.g. a simple cube_reader.get() will load the entire ESDC into memory and thus likely fail on most
personal computers.

Some more elaborate demonstrations are also included in the `ESDC community notebooks`_.

Using Julia
===========

The Data Access API for Julia is part of the :doc:`dat_julia`.

Data Analysis
=============

In addition to the Data Access APIs, we provide a Data Analytics Toolkit (DAT) to facilitate analysis and
visualization of the ESDC. Please see

    * :doc:`dat_julia`
    * :doc:`dat_python`

