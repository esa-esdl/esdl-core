.. _xarray: http://xarray.pydata.org/en/stable/
.. _xarray.Dataset: http://xarray.pydata.org/en/stable/data-structures.html#dataset
.. _xarray.DataArray: http://xarray.pydata.org/en/stable/data-structures.html#dataarray
.. _xarray API: http://xarray.pydata.org/en/stable/api.html
.. _Numpy: http://www.numpy.org/
.. _Numpy ndarrays: http://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html
.. _cablab.dat: https://github.com/CAB-LAB/cablab-core/blob/master/cablab/dat.py
.. _E-Lab: https://cablab.earthsystemdatacube.net
.. _Jupyter notebook: https://github.com/CAB-LAB/cablab-shared/blob/master/notebooks/Python/Python_DAT.ipynb


.. _Indexing and selecting data: http://xarray.pydata.org/en/stable/indexing.html
.. _Computation: http://xarray.pydata.org/en/stable/computation.html
.. _Split-apply-combine: http://xarray.pydata.org/en/stable/groupby.html
.. _Reshaping and reorganizing data: http://xarray.pydata.org/en/stable/reshaping.html
.. _Combining data: http://xarray.pydata.org/en/stable/combining.html
.. _Time series data: http://xarray.pydata.org/en/stable/time-series.html


==============
DAT for Python
==============

Overview
========

The main objective of the Data Analytics Toolkit is to facilitate the exploitation
of the multi-variate data set in the ESDC for experienced users and empower less experienced
users to explore the wealth of information contained in the ESDC. To this end, Python is almost
a natural choice for the programming language, as it is easy to learn and use, offers numerous,
well-maintained community packages for data handling and analysis, statistics, and visualisation.

The DAT for Python relies primarily on xarray_ a package that provides N-dimensional data structures
and efficient computing methods on those object. In fact, xarray closely follows the approach adopted
NetCDF, the quasi-standard file format for geophysical data, and provides methods for many
commonly executed operations on spatial data.
The central data structure used for representing the ESDC in Python is thus the `xarray.Dataset`_.

Such dataset objects are what you get when accessing the cube's data as follows:

.. code-block:: python

    from cablab import Cube
    cube = Cube.open("/home/doe/esdc/cablab-datacube-0.2.4/low-res")
    dataset = cube.data.dataset(["precipitation", "evaporation", "ozone", "soil_moisture","air_temperature_2m"])

Any geo-physical variable in the ESDC is represented by a `xarray.DataArray`_, which are Numpy_-like data arrays
with additional coordinate information and metadata.

The following links point into the xarray_ documentation, they provide the low-level interface for the Python DAT:

* `Indexing and selecting data`_
* `Computation`_
* `Split-apply-combine`_
* `Reshaping and reorganizing data`_
* `Combining data`_
* `Time series data`_

Building on top of the xarray_ API the DAT offers high-level functions for ESDC-specific workflows
in the `cablab.dat`_ module. These functions are addressing specific user requirements and
the scope of the module will increase with the users of the DAT. In the following, typical use cases and examples
provide an illustrative introduction into the usage of the DAT and thus into the exploration of the ESDC.

Use Cases and Examples
======================
The below examples are all contained in a `Jupyter notebook`_, which is also available in the E-Lab_.

In the first step described above, a subset of five variables is loaded into the dataset.

.. code-block:: python

    dataset

.. image:: pix/dat1.png
   :width: 600 px
   :align: left

Constraints and Limitations
===========================

.. todo:: GB add any Constraints and Limitations, e.g. by xarray, dask, see Fabian's Julia DAT


Python API Reference
====================

The low-level interface of the ESDC Python DAT is the `xarray API`_.

The following functions provide the high-level API of the ESDC Python DAT:

.. automodule:: cablab.dat
    :members:


