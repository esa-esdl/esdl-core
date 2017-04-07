.. _xarray: http://xarray.pydata.org/en/stable/
.. _xarray.Dataset: http://xarray.pydata.org/en/stable/data-structures.html#dataset
.. _xarray.DataArray: http://xarray.pydata.org/en/stable/data-structures.html#dataarray
.. _xarray API: http://xarray.pydata.org/en/stable/api.html
.. _Numpy: http://www.numpy.org/
.. _Numpy ndarrays: http://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html
.. _cablab.dat: https://github.com/CAB-LAB/cablab-core/blob/master/cablab/dat.py



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

The primary Data Analytics Toolkit for Python is xarray_ since the central
data structure used for representing the ESDC in Python is the `xarray.Dataset`_.

Such dataset objects are what you get when accessing the cube's data as follows:

.. code-block:: python

    from cablab import Cube
    cube = Cube.open("/home/doe/esdc/cablab-datacube-0.2.4/low-res")
    dataset = cube.data.dataset(["precipitation", "evaporation", "ozone"])

Any geo-physical variable in the ESDC is represented by a `xarray.DataArray`_, which are Numpy_-like data arrays
with additional coordinate information and metadata.

The following links point into the xarray_ documentation, they provide the low-level interface for the Python DAT:

* `Indexing and selecting data`_
* `Computation`_
* `Split-apply-combine`_
* `Reshaping and reorganizing data`_
* `Combining data`_
* `Time series data`_

In addition to what the xarray_ API is providing, some higher-level DAT functions are available
in the `cablab.dat`_ module.

Use Cases and Examples
======================

.. todo:: GB convert your notebook to prosa here and/or link to it


Constraints and Limitations
===========================

.. todo:: GB add any Constraints and Limitations, e.g. by xarray, dask, see Fabian's Julia DAT


Python API Reference
====================

The low-level interface of the ESDC Python DAT is the `xarray API`_.

The following functions provide the high-level API of the ESDC Python DAT:

.. automodule:: cablab.dat
    :members:


