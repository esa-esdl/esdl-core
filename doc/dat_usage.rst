=========================================================
How can I analyze the Data in the Earth System Data Cube?
=========================================================

The Data Analytics Toolkit
==========================

.. Responsible: BC


In addition to the Data Access API, which enables the user to conveniently access data from an
Earth System Data Cube (ESDC),
we provide a Data Analytics Toolkit (DAT) to facilitate analysis and
visualization of the ESDC. The DAT is hosted in `CABLAB's github repository <https://github.com/CAB-LAB/CABLAB.jl>`_
and is developed in close interaction with the scientific community.
The CABLAB team is leading the development of the DAT for Python and Julia.


Julia implementation of the DAT
-------------------------------

The current implementation of the Julia DAT consists of 3 parts:

  1. A collection of time-series and spatial analysis functions
  2. Functions for visualizing time-series and spatial maps
  3. A macro to conveniently add custom functions to the DAT

**1. Collection of analysis functions**

We provide several methods to perform basic statistical analyses on the ESDC.
These methods expect Data Cube representations as first argument.
Splitting of the data along the appropriate axes, handling of missing data, and formatting of the results
are automatically dealt with. Currently, the following analytical methods are implemented:

  - **removeMSC** subtracts the mean annual cycle of each time series in the Data Cube
  - **gapFillMSC** uses the mean annual cycle to fill missing values per time series in the Data Cube
  - **normalize** normalizes the whole Data Cube so that each time series has zero mean and unit variance
  - **timeVariance** calculates the variance per time series
  - **timeMean** returns the time mean for each time series in the Data Cube

**2. Visualisation of the ESDC**

For a convenient and interactive visual inspection of the ESDC two plotting functions are available:
plotTS for plotting time-series and plotMAP for plotting maps of sptial data.
The resulting plots are interactive. For example, when plotting time-series of a 4D dataset
sliders allow users to move along longitudes and latitudes. Moreover, the selection of variables is realized through buttons.
The same holds for maps, which users can move through time and switch between variables.

**3. Adding user functions into the DAT**

Users can add custom functions to the DAT for individual sessions.
Before we explain how to do this we describe how the DAT handles Data Cube dimensions.
Each Cube object has an **axes** property, which is a vector of the Data Cube axes.
Currently the following axes types are defined:

  - **LonAxis** represents the Data Cube's longitude dimension
  - **LatAxis** represents the Data Cube's latitude dimension
  - **TimeAxis** represents the Data Cube's time dimension
  - **VariableAxis** defines the variables of the Data Cube
  - **CountryAxis** can be used for by-country variables

A Data Cube has the shape of a 4-dimensional array with the axes Variable, Time, Latitude and Longitude.
DAT methods may change the dimensionality of the input. For example, if a time average is applied to a 4-dimensional Cube object,
the result will have only 3 dimensions, since the time dimension has been eliminated.

A custom function is added to the DAT using the **@registerDATFunction** macro.
Its first argument is a function that is supposed to be applied on slices of the Cube object.
Its signature must have at least 4 input variables: **xin**, **xout**, which are the input and output data arrays
and **maskin** and **maskout** which are the input and output mask.
The second argument is a tuple containing the axes the function is applied to.
The third argument is a tuple containing the return axes of the operation.
Any additional arguments are passed to the underlying function.

To give an example, here is how the mean seasonal cycle gap-filling function is defined:

.. code:: Julia

    function gapFillMSC(xin::AbstractVector,xout::AbstractVector,maskin::AbstractVector{UInt8},maskout::AbstractVector{UInt8},NpY::Integer)

      msc=getMSC!(xin,xout,maskin,NpY)
      replaceMisswithMSC!(msc,xin,xout,maskin,maskout,NpY)

    end

    @registerDATFunction gapFillMSC (TimeAxis,) (TimeAxis,) NpY::Integer


First, an atomic function that operates on single time-series is defined.
It accepts an input and an output vector and a mask as its arguments as well as an additional argument, which
is the number of time steps per year. Then the macro **@registerDATFunction** is called, the input dimension
is a TimeAxis as well as the output dimension. Internally this generates a new method of the gapFillMSC function,
which operates on a memory representation of a Cube object (as returned from a call to getCubeData).
It will automatically take care of slicing the data correctly, permute dimensions if necessary, apply
the function, and collect the results into an output data structure, which is again a memory representation of a Cube object
with the appropriate axes.


Use Cases and Examples
----------------------
In the following the potentials of the DAT are demonstrated by two more complex examples, the user stories.

.. include:: story1.rst


.. include:: story2.rst



Constraints and Limitations
---------------------------

The current implementation of the DAT is subject to several limitations, some of which will be mitigated in future releases of the software.
Most importantly, the DAT methods currently only work on data loaded into memory. Hence, the user has to explicitly load a part of the ESDC into memory prior
to run any analysis on it. Obviously, this way the available memory severely constraints the analytical strategy and may even
render analyses impossible if the ratio between available memory and size of the data chunk of interest is unfavourable.
In the future, it is anticipated to overcome this limitation by enabling DAT functions to work also on Cube objects that
are not yet available in memory. In particular, methods will be provided to automatically load and process Cube data
incrementally, i.e. bit by bit. This will most likely involve writing the interim results to a temporary Cube on disk.
The same applies to plot functions for Cube objects that will be adjusted to access only the data required for the current
plot and that will automatically reduce the data resolution if adequate, which in typical cases means that there is more
data than can be diplayed given the resolution of the plot.
