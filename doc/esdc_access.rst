===========
ESDC Access
===========

.. todo:: GB/NF must restructure & rewrite this section


There are several ways to interact with the ESDC and depending your expertise, resources and, requirements the preferred
method will vary. The CAB-LAB team is eager to learn more about user needs to continuously improve the capabilities of the
ESDC.

Dataset Access Service
======================

The ESDC physically consists of a set of netcdf files on disk, which can be accessed in four different ways:

    * Download from CABLAB's ftp server `<ftp:ftp.brockmann-consult.de>`_. Please contact us to get a valid username.
    * Convenient access via a THREDDS Server at `<http://www.brockmann-consult.de/cablab-thredds/catalog.html>`_.
      The Server allows for subsetting of variables and visual exploration of the data, which can be downloaded as netcdf of
      plain text.
    * Accessing a remotely stored ESDC using the OpenDAP protocol via the Data Access API, which is described in detail below.
      Similar to the options described above, the data will be downloaded to your computer upon request, but depending
      on the variables, and the region and time period of interest, the transferred data volume might be much lower than a
      complete download of the ESDC.
    * Accessing the E-laboratory on a remote Jupyter server, e.g.
      `<http://cablab.earthsystemdatacube.net/cablab-jupyterhub/>`_ (Contact us for login details!). In this case, the data remains in the remote server and also the user's
      computations are executed remotely. This is the most resource efficient and convenient way of exploring the ESDC.

In addition, a cube.config file containing essential metadata of the ESDC is requires to use to Data Access API. It is automatically
generated during the generation of the ESDC and available on the ftp server and the CABLAB homepage.

Getting Started
===============

While in principle the netcdf files comprising the ESDC can be used with any tool of choice, we developed specifically tailored Data Access APIs
for Python 3.X and Julia. In the future, Matlab and Java will join the two to cover the most common programming languages in Earth System Sciences.
Furthermore, a set of high-level routines for data analysis, the Data Analytics Toolkit, greatly facilitates
standard operations on the large amount of data in the ESDC. While in the E-laboratory, the Data Access API and the DAT are already pre-installed,
the user has to download and install the cube library when working on a local computer.

To get started on your local computer, clone the cablab-core repository from `<https://github.com/CAB-LAB>`_:

.. code-block:: tcsh

    git clone https://github.com/CAB-LAB/cablab-core

It will create a new folder cablab-core, which contains a file named setup.py. Before installation, the system dependencies should be checked.
Currently, the cablab-core library requires the following python packages:

    * xarray >= 0.9
    * matplotlib >= 2.0
    * netCDF4 >= 1.2
    * scikit_image >= 0.11
    * scipy >= 0.16

If your python installation lacks one or all of the above packages, we recommend to visit `<http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_ to obtain pre-compiled Python binaries for different
architectures, which can be then installed using pip:

.. code-block:: tcsh

    pip install <wheel-file>

Kudos to Christoph Gohlke for the continuous efforts!
The cablab-core library can be installed from terminal (Linux/Unix/MacOs) or shell (Windows):

.. code-block:: tcsh

    python setup.py install

After download of a ESDC including the corresponding cube.config file and successful installation of the ESDC,
you are ready to explore the data in the ESDC!

Data Access with the API
========================

In the following, the Data Access via a Python notebook in Jupyter is described. All commands do, however, also work in any
interactive Python environment or in a Python script. `Jupyter <http://jupyter.org/>`_ is already included in several Python
distributions, but can also be installed by a simple

.. code-block:: tcsh

    pip install jupyter

and started from the command line by typing:

.. code-block:: tcsh

    jupyter notebook

This will open an interactive jupyter session in your browser. In the example below, it
is demonstrated how the user can access a locally stored ESDC, query the content, and get chunks of different sizes for further
analysis. A valid configuration file, typically named cube.config, has to be located in the root folder of the ESDC, i.e. in the folder
you pass to Cube.open(). It contains essential metadata about the ESDC to be loaded and is automatically built during the generation of the ESDC. Some more elaborate demonstrations are also included in the
`cablab-shared repository on git-hub <https://github.com/CAB-LAB/cablab-shared/tree/master/notebooks>`_ and the `API reference <api_reference.html>`_
is located in the Annex of this Product Handbook.

Data Access Example
===================

In this notebook, data access using CABLAB's Python API is demonstrated.

.. code:: python

    from cablab import Cube
    from cablab import CubeData
    from datetime import datetime
    import numpy as np

.. code:: python

    cube = Cube.open("/path/to/datacube")
    cube_reader = CubeData(cube)

.. code:: python

    cube_reader.variable_names




.. parsed-literal::

    {'BurntArea': 0,
     'Emission': 1,
     'Ozone': 2,
     'Precip': 3,
     'SoilMoisture': 4,
     'tcwv_res': 5}


After successful opening the ESDC, chunks of data or the entire data set can be accessed via the get() function. Below we demonstrate basic approaches
to retrieve different kind of subsets of the ESDC using the Data Access API in Python. The corresponding API for Julia is
very similar and illustrated in the `Data Analytics Toolkit <dat_usage.html>`_ section.


**Get the cube's data**

The get() method expects up to four arguments:

.. parsed-literal::
    get(variable=None, time=None, latitude=None, longitude=None)

with

*variable:* a variable index or name or an iterable returning multiple
of these (var1, var2, ...

*time:* a single datetime.datetime object or a 2-element iterable
(time\_start, time\_end)

*latitude:* a single latitude value or a 2-element iterable
(latitude\_start, latitude\_end)

*longitude:* a single longitude value or a 2-element iterable
(longitude\_start, longitude\_end)

*return:* a dictionary mapping variable names --> data arrays of
dimension (time, latitude, longitude)


**Getting a chunk of 1 variable, all available time steps, and 40 x 40 spatial grid points:**

.. code:: python

    precip_chunk = cube_reader.get('Precip',None,(0,10),(0,10))
    np.array(precip_chunk).shape




.. parsed-literal::

    (1, 457, 40, 40)



**Getting time-series at a single point of all variables for the entire period:**

.. code:: python

    time_series = cube_reader.get(None,None,51.34,8.23)
    [var.shape for var in time_series]




.. parsed-literal::

    [(457,), (457,), (457,), (457,), (457,), (368,)]



**Getting a complete global image of a variable at a specific time**


.. code:: python

    Emission_single_image = cube_reader.get('Emission', datetime(2002,1,1))
    np.array(Emission_single_image).shape




.. parsed-literal::

    (1, 720, 1440)



.. code:: python

    cube.close()



Note that the available memory limits the maximum size of the data chunk that can be simultaneously loaded, e.g. a simple cube_reader.get()
will load the entire ESDC into memory and thus likely fail on most personal computers.



ESDC Analysis
=============

In addition to the Data Access API, which enables the user to conveniently access data from an
Earth System Data Cube (ESDC), we provide a Data Analytics Toolkit (DAT) to facilitate analysis and
visualization of the ESDC.


