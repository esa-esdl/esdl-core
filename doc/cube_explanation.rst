.. index:: Earth System Data Cube

===================================
What is the Earth System Data Cube?
===================================

.. BC

Overview
========

Earth observations (EOs) are usually produced and treated as 3- dimensional singular data cubes, i.e. for each
longitude u ∈ {1, ..., Lon}, each latitude v ∈ {1, …, Lat}, and each time step t ∈ {1,...,T} an observation
X = {x(u,v,t)} ∈ R is defined. The challenge is, however, to take advantage of the numerous
EO streams and to explore them simultaneously.
Hence, the idea is to concatenate data streams such that we obtain a 4-dimensional data cube of the form x(u,v,t,k)
where k ∈ {1, …, N} denotes the index of the data stream. The focus of this project is therefore on learning how
to efficiently and reliably create, curate, and explore a 4-dimensional Earth System Data Cube (ESDC).
If feasible, the included data-sets contain uncertainty information. Limitations associated with the transformation
from source format into the ESDC format are explained in the `description of the data sets <annex.html#Annexes>`__.
The ESDC does not exhibit spatial or temporal gaps, since gaps in the source data are filled during ingestion into
the ESDC. While all observational values are conserved, gaps are filled with synthetic data, i.e. with data that is created by an
adequate gap-filling algorithm. Proper data flags ensure an unambiguous distinction between observational and
synthetic data values.

.. index:: ESDC Macro Structure

ESDC Macro Structure
=========================

The data is organised in the described 4-dimensional form x(u,v,t,k), but additionally each data stream k is assigned to one
of the subsystems of interest:

* Land surface
* Atmospheric forcing
* Socio-economic data

.. index:: Cube Spatial and Temporal Coverage

Spatial and Temporal Coverage
=============================

The fine grid of the ESDC has a spatial resolution of 0.083° (5”), which is properly nested within a coarse grid of
0.25° (15”). Hence, the ESDC is available in two versions

* **High resolution version**: 0.083° (5”) spatial resolution,
* **Low resolution version**:  0.25° (15”) spatial resolution.

While the latter contains all variables, the former only comprises those variables that are natively available at this resolution.
The high-resolution data are nested on the low-resolution data set such that one can analyse these in tandem.
In particular data from the socio-economic subsystem are often organised according to administrative units, typically national states, rather than on regular grids.
These data are dispersed to the coarse grid by means of a national state mask, which is created by assigning a national state property to each grid point.

The **temporal resolution** is 8 days.

The **time span** currently covered is 2001-2011. We are dedicated to expand this period on both ends, but to preserve the ESDC's characteristics, a reasonable coverage of data streams is required.





