======================
What is the Data Cube?
======================

Overview
========

Earth observations are usually produced and treated as 3- dimensional singular data cubes i.e. for each
longitude u ∈ {1, ..., Lon}, each latitude v ∈ {1, …, Lat} and each time step t ∈ {1,...,T} an observation
X = {x(u,v,t)} ∈ R is defined. The challenge is aiming at exploring multiple EO streams simultaneously.
Hence, the idea is concatenating data streams such that we obtain a 4-dimensional data cube of the form x(u,v,t,k)
where k ∈ {1, …, N} denotes the index of the data stream. The question of how to create, curate, and explore a
4-dimensional Earth system cube of this kind is our object of research.

The Data Cube shall include datasets that exhibit uncertainty information. Uncertainty information shall be included
in the Data Cube, if straightforwardly feasible. Limitations resulting from the transformation from source format
into the format of the Data Cube shall be explained in the Data Handbook.

The Data Cube shall not exhibit spatial or temporal gaps. Gaps in the source data shall be filled in the Data Cube,
using a suitable gap-filling algorithm. All measurement values shall be conserved, only gaps shall be filled. Proper
and prominent data flags shall indicate filled gaps in the Data Cube.

Data Cube Macro Structure
=========================

The data is saved in the described 4-dimensional form, but additionally contains an index assigning each k-th
data stream to one of the fundamental subsystems of interest:

* Land surface
* Atmospheric forcing
* Human data

Spatial and Temporal Coverage
=============================

The Data Cube shall exhibit a spatial target resolution of 0.083° (5”) that is properly nested within a coarser
0.25° (15”) grid. Hence, the data cube will be available in two versions

* **High resolution version**: 0.083° (5”) spatial resolution,
* **Low resolution version**:  0.25° (15”) spatial resolution.

The latter contains all variables, the first ones only those variables natively available at this resolution.
The high-resolution data are nested on the low-resolution data set such that one can analyse these in tandem.
Country-based data (i.e. any data based on administrative units) shall be interpolated to the coarse resolution of
the Data Cube.

The **temporal resolution** will be 8 days.

The **time span** will be from 2001-2011 for the first version. It will ideally be updated as soon to the end of
2014 or 2015.






