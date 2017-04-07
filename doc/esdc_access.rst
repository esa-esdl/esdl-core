.. _NetCDF: https://www.unidata.ucar.edu/software/netcdf/docs/
.. _Web Coverage Service (WCS): http://www.opengeospatial.org/standards/wcs
.. _OPeNDAP: https://www.opendap.org/

.. _Jupyter: http://jupyter.org/about.html
.. _JupyterHub: https://jupyterhub.readthedocs.io/en/latest/
.. _Notebooks: https://jupyter.readthedocs.io/en/latest/index.html
.. _Conda: https://conda.io/docs/intro.html

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

To get started on your local computer with Python, clone the `cablab-core`
repository from `<https://github.com/CAB-LAB>`_:

.. code-block:: tcsh

    git clone https://github.com/CAB-LAB/cablab-core

It will create a new folder ``cablab-core``, which contains a file named ``setup.py``. Before installation,
the system dependencies should be checked. Currently, the ``cablab-core`` library requires the following
Python packages:

    * xarray >= 0.9
    * matplotlib >= 2.0
    * netCDF4 >= 1.2
    * h5netcdf >= 0.3
    * h5py >= 2.7
    * scikit_image >= 0.11
    * scipy >= 0.16

We recommend to using Conda_ for installation of these packages (requires a Anacondfa/Miniconda environment).
If you can't use Conda, and you have to stay with standard Python, it may lack one or more of the above's transitive
package dependencies, we recommend to visit `<http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_ to obtain
pre-compiled Python binaries for different architectures, which can be then installed using pip:

.. code-block:: tcsh

    pip install <wheel-file>

Kudos to Christoph Gohlke for the continuous efforts!
The cablab-core library can be installed from terminal (Linux/Unix/MacOs) or shell (Windows):

.. code-block:: tcsh

    python setup.py install

After download of a ESDC including the corresponding ``cube.config`` file and successful installation of the ESDC,
you are ready to explore the data in the ESDC using the :ref:`data_access_py`.

.. data_access_api

Usage
-----

In the following, the Data Access via a Python in a Jupyter_ Notebook is described. All commands do, however,
also work in any interactive Python environment or in a Python script. Jupyter is already included in
several Python distributions, but can also be installed by a simple

.. code-block:: tcsh

    pip install jupyter

and started from the command line by typing:

.. code-block:: tcsh

    jupyter notebook

This will open an interactive Jupyter session in your browser.

In the example below, it is demonstrated how the user can access a locally stored ESDC, query the content, and get
chunks of different sizes for further analysis. A valid configuration file, typically named cube.config,
has to be located in the root folder of the ESDC, i.e. in the folder you pass to ``Cube.open()``.
It contains essential metadata about the ESDC to be loaded and is automatically built during the generation
of the ESDC. Some more elaborate demonstrations are also included in the `ESDC community notebooks`_.

In the following notebook, data access using CABLAB's Python API is demonstrated.

.. code:: python

    from cablab import Cube
    from cablab import CubeData
    from datetime import datetime
    import numpy as np

.. code:: python

    cube = Cube.open("/path/to/datacube")
    cube_data = cube.data

.. code:: python

    cube_data.variable_names

.. parsed-literal::

    {'BurntArea': 0,
     'Emission': 1,
     'Ozone': 2,
     'Precip': 3,
     'SoilMoisture': 4,
     'tcwv_res': 5}


After successful opening the ESDC, chunks of data or the entire data set can be accessed via the get() function.
Below we demonstrate basic approaches to retrieve different kind of subsets of the ESDC using the Data Access
API in Python. The corresponding API for Julia is very similar and illustrated in :doc:`dat_julia`.

**Get the cube's data**

The ``cube_data.get()`` method expects up to four arguments:

.. parsed-literal::

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

Using Julia
===========

The Data Access API for Julia is part of the :doc:`dat_julia`.

Data Analysis
=============

In addition to the Data Access APIs, we provide a Data Analytics Toolkit (DAT) to facilitate analysis and
visualization of the ESDC. Please see

    * :doc:`dat_julia`
    * :doc:`dat_python`

