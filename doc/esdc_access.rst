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

.. _ESDL E-Laboratory: http://jupyterhub.earthsystemdatalab.net/
.. _ESDL THREDDS server: http://www.brockmann-consult.de/cablab-thredds/catalog.html
.. _ESDL FTP server: ftp://ftp.brockmann-consult.de/cablab02/esdc-31d-1deg-1x180x360-1.0.1_1/
.. _ESDL community repository: https://github.com/esa-esdl/esdl-shared
.. _ESDL community notebooks: https://github.com/esa-esdl/esdl-shared/tree/master/notebooks

.. _OBS Cube configuration: https://obs-esdc-configs.obs.eu-de.otc.t-systems.com/datacube_paths.json

===========
ESDC Access
===========

As introduced in the last section, the ESDC physically consists of a set of NetCDF_ files on disk,
which can be accessed in a number of different ways which are described in this section.


OPeNDAP and WCS Services
========================

Replaced by an S3 object store (OBS). Please refer to the Usage section.

E-Laboratory
============

A dedicated `ESDL E-Laboratory`_ has been developed to access the ESDC data via distributed
`Jupyter`_ `Notebooks`_ for Julia and Python. This is the most resource efficient and convenient
way of exploring the ESDC.

These notebooks have direct access to the ESDC data so there is no need to download it.
In addition they provide the ESDC Python and Julia APIs comprising
the Data Access API and the Data Analytics Toolkit.

The E-Laboratory provides some example notebooks in the shared `ESDL community repository`_.

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

To get started on your local computer with Python, clone the `esdl-core`
repository from `<https://github.com/esa-esdl>`_:

.. code-block:: bash

    git clone https://github.com/esa-esdl/esdl-core

The following command will create a new Python 3.5 environment named ``esdl`` with all required dependencies, namely

    * dask >= 0.14
    * gridtools >= 0.1 (from Conda channel ``cablab``)
    * h5netcdf >= 0.3
    * h5py >= 2.7
    * netcdf4 >= 1.2
    * scipy >= 0.16
    * scikit_image >= 0.11
    * matplotlib >= 2.0
    * xarray >= 0.9

.. code-block:: bash

    $ conda env create environment.yml

To active new Python environment named ``esdl`` you must execute the following command:

.. code-block:: bash

    $ conda activate esdl

Now change into new folder ``esdl-core`` and install the ``esdl`` Python package using the ``develop`` target:

.. code-block:: bash

    $ cd esdl-core
    $ python setup.py develop

You can now easily change source code in ``esdl-core`` without reinstalling it.
When you do not plan to add or modify any code (e.g. add a new source data provider), you can also permanently
install the sources using

.. code-block:: bash

    $ python setup.py install

However, if you now change any code, make sure to the install command again.

After download of a ESDC including the corresponding ``cube.config`` file and successful installation of the ESDC,
you are ready to explore the data in the ESDC using the :ref:`data_access_py`.

.. data_access_py

Usage
-----

The following example code demonstrates how to access a locally stored ESDC, query its content, and get
data chunks of different sizes for further analysis.

**Open a cube**

First get a list of available Cubes:

.. code:: python

    from esdl.cube_store import CubeStore
    cs = CubesStore()
    cs

.. parsed-literal::

    CUBE_V2.0.0_global_spatially_optimized_0.25deg_supplement ...
    CUBE_V2.0.0_global_spatially_optimized_0.25deg ...
    CUBE_V2.0.0_global_time_optimized_0.25deg ...
    CUBE_V2.0.0_colombia_spatially_optimized_0.083deg ...
    ...

Obtain a Cube by using the Cube's name:

.. code:: python

    ds = cs['CUBE_V2.0.0_global_spatially_optimized_0.25deg']
    ds.data_vars

.. parsed-literal::

    Data variables:
    Rg                                 (time, lat, lon) float32 dask.array<shape=(1702, 720, 1440), chunksize=(1, 720, 1440)>
    aerosol_optical_thickness_1600     (time, lat, lon) float32 dask.array<shape=(1702, 720, 1440), chunksize=(1, 720, 1440)>
    aerosol_optical_thickness_550      (time, lat, lon) float32 dask.array<shape=(1702, 720, 1440), chunksize=(1, 720, 1440)>
    aerosol_optical_thickness_670      (time, lat, lon) float32 dask.array<shape=(1702, 720, 1440), chunksize=(1, 720, 1440)>
    aerosol_optical_thickness_870      (time, lat, lon) float32 dask.array<shape=(1702, 720, 1440), chunksize=(1, 720, 1440)>
    air_temperature_2m                 (time, lat, lon) float32 dask.array<shape=(1702, 720, 1440), chunksize=(1, 720, 1440)>
    ...

**Accessing the cube data**

An `xarray.DataArray`_ object can be retrieved by accessing the datasets variable by
variable name.

.. code:: python
    lst = ds.aerosol_optical_thickness_1610

.. parsed-literal::

    <xarray.DataArray 'Rg' (time: 1702, lat: 720, lon: 1440)>
    dask.array<shape=(1702, 720, 1440), dtype=float32, chunksize=(1, 720, 1440)>
    Coordinates:
      * lat      (lat) float32 89.875 89.625 89.375 ... -89.375 -89.625 -89.875
      * lon      (lon) float32 -179.875 -179.625 -179.375 ... 179.625 179.875
      * time     (time) datetime64[ns] 1980-01-05 1980-01-13 ... 2016-12-30
    Attributes:
        ID:                        2
        esa_cci_path:              nan
        long_name:                 Downwelling shortwave radiation
        orig_attrs:                {'long_name': 'Downwelling shortwave radiation...
        orig_version:              15.10.2017
        project_name:              BESS
        time_coverage_end:         2010-12-31
        time_coverage_resolution:  P8D
        time_coverage_start:       2000-03-01
        url:                       http://environment.snu.ac.kr/bess_rad/


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


**Downloading a Cube**

The data cubes are available from an S3 Object Storage (OBS). There are two ways of accessing the data:

- Use the esdl-core Cubestore class
- Or use you own S3 libraries

To download the data locally use:

.. code:: python

    from esdl.cube_store import CubeStore
    cs = CubesStore()
    ds = cs['CUBE_V2.0.1_colombia_time_optimized_0.0083deg']

    ds.to_zarr('CUBE_V2.0.1_colombia_time_optimized_0.0083deg.zarr')

Please be aware that downloading a whole cube may take a substantial
amount of time.

You might use a different programming language. In that case
You can access a configuration file with all information like endpoints,
regions etc. using the following URL: `OBS Cube configuration`_


Using Julia
===========

The Data Access API for Julia is part of the :doc:`dat_julia`.

Data Analysis
=============

In addition to the Data Access APIs, we provide a Data Analytics Toolkit (DAT) to facilitate analysis and
visualization of the ESDC. Please see

    * :doc:`dat_julia`
    * :doc:`dat_python`

