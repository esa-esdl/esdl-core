=============
DAT for Julia
=============

Overview
========

The Data Analytics Toolkit (DAT) for Julia is hosted in `CABLAB's github repository <https://github.com/CAB-LAB/CABLAB.jl>`_
and is developed in close interaction with the scientific community. Here we give a short overview on the capabilities
of the Julia DAT, but we would refer to the `official documentation`_ for
a more detailed and frequently updated software description.

The current implementation of the Julia DAT consists of 3 parts:

  1. A collection of analysis functions that can be applied to the ESDC
  2. Functions for visualizing time-series and spatial maps
  3. A function to register custom functions to be applied on the cube

**1. Collection of analysis functions**

We provide several methods to perform basic statistical analyses on the ESDC. In a typical workflow, the user wants to
apply some function (e.g. a time series analysis) on all points of the cube. In other systems this would mean that the user
must write some loop that reads chunks of data, applies the function, stores the result and then read the next chunk of data
etc. In the Julia DAT, this is done automatically, the user just calls e.g. `mapCube(removeMSC,mycube)` and the mean seasonal
cycle will be subtracted from all individual time series contained in the selected cube.

In Analysis_ one can find a list of all currently implemented DAT methods.

**2. Visualisation of the ESDC**

For a convenient and interactive visual inspection of the ESDC five plotting functions are available:

  - **plotXY** for scatterplotd or bar plots along a single axis
  - **plotTS** like plotXY but the x axis set to TimeAxis by default
  - **plotScatter** for scatter plots of two elements from the same axis, e.g. of two Variables
  - **plotMAP** for generic map plots
  - **plotMAPRGB** for RGB-like maps plots where different variables can be mapped to the plot color channels

For examples and a detailed description of the plotting functions, see Plotting_


**3. Adding user functions into the DAT**

Users can add custom functions to the DAT for individual sessions. This is described in detail in the `adding_new`_ chapter of the manual.


Use Cases and Examples
======================

Example notebooks that explore the ESDC using the Julia DAT can be found in the `cablab-shared`_ repository.



.. _`CABLAB's github repository`: https://github.com/CAB-LAB/CABLAB.jl
.. _`official documentation`: http://cab-lab.github.io/CABLAB.jl/latest/
.. _Analysis: http://cab-lab.github.io/CABLAB.jl/latest/analysis.html
.. _Plotting: http://cab-lab.github.io/CABLAB.jl/latest/plotting.html
.. _`adding_new`: http://cab-lab.github.io/CABLAB.jl/latest/adding_new.html
.. _`cablab-shared`: https://github.com/CAB-LAB/cablab-shared/tree/master/notebooks/Julia
