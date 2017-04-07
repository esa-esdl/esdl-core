============
Introduction
============

.. BC

Motivation
==========

Earth observations (EOs) are usually produced and treated as 3-dimensional singular data cubes, i.e. for each
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

Depending on the specific question, the user can extract different types of data subsets from the Earth System Data Cube (ESDC)
for further processing and analysis with specialized methods from the
`Data Analytics Toolkit <dat_usage.html#the-data-analytics-toolkit>`__. For example,

* investigating the data cube **at a single geographic location**, the user obtains multivariate time series for each
  longitude-latitude pair. These time series can be investigated using established methods of multivariate time series
  analysis, and afterwards the results can be merged onto a global grid again.
* Assessing the data-cube **at single time stamps** results in synoptic geospatial maps,
  whose properties can be investigated with geostatistical methods.
* It is also possible to perform **univariate spatiotemporal analyses** on single variables extracted from the
  Data Cube. 
* The main objective is, however, to develop **multivariate spatiotemporal analyses** by utilizing the entire 4D ESDC.
  Following this avenue unravels the full potential of the ESDC and may provide a holistic view on the entire Earth System.

The ESDC allows for all these approaches, because all variables are available on a common spatiotemporal grid, which greatly
reduces the pre-processing efforts typically required to establish consistency among data from different sources.


The CAB-LAB Project
===================

The steadily growing Earth Observation archives are currently mostly investigated
by means of disciplinary approaches. It would be, however, desirable to adopt a more holistic approach in understanding land-atmosphere interactions and
the role of humans in the earth system. The potential of a simultaneous exploration of multiple EO data streams
has so far been widely neglected in the scientific community.
The Coupled Atmosphere Biosphere virtual LABoratory project (CAB-LAB) aims at filling this gap by providing
a virtual laboratory that facilitates the co-exploration of multiple EOs for a better understanding of land ecosystem trajectories.

The idea is to build on the existing data-sets and to offer novel tools and technical methods to detect dependencies in the coupled human-nature system.
CAB-LAB's central service to the scientific community will be a Biosphere Atmosphere Virtual Laboratory (BAVL), which comprises a Data
Cube populated with a wide range of EOs and convenient methods to access and analyze this data remotely by means of the Jupiter framework.
Moreover, the project aims at advancing the scientific analysis capacities by developing data-driven exploration strategies that identify and attribute major changes
in the biosphere-atmosphere system. Ultimately, CAB-LAB will develop a set of indices
characterizing the major relevant Biosphere-Atmosphere System Trajectories, BASTs.
The project partners, Max-Planck-Institute for Biogeochemistry, Brockmann Consult GmbH,
and Stockholm Resilience Center are financed by the European Space Agency (ESA) for three years (2015 to 2017) to
develop the software for CAB-LAB, to collect and analyze the EO data, and to disseminate the idea of the project and its preliminary results.


Purpose
=======

This Product Handbook is a living document that is under active development just as the CAB-LAB project itself.
Its purpose is to facilitate the usage of the BAVL and primarily targets scientists from various disciplines with a good
command of one of the supported high-level programming languages (`Python <http://www.python.org>`_, `Julia <http://julialang.org/>`_,
and `R <http://www.>`_), a solid background in the analysis of
large data-sets, and a sound understanding of the Earth System.
The focus of this document is therefore clearly on the description of the data and on the methods to access and manipulate the data.


In the final version, it is meant to be a self-contained documentation that enables the user to independently reap the full potential of the Earth System Data Cube (ESDC).
Developers may find a visit of the `project's git-hub pages <https://github.com/CAB-LAB>`_ worthwile.

Scope
=====

The Product Handbook gives a general overview of the `ESCD's structure <esdc_descr.html#ESDC Description>`__
and provide some examples to illustrate `potential uses of the system <cube_scenarios.html#What can I do with the Earth System Data Cube?>`__ .
The main part is considered with a detailed `technical description of the ESDC <cube_usage.html#How can I use the Earth System Data Cube?>`__
, which is accompanied by the full `specification of the API <api_reference.html#CAB-LAB API Reference>`__.
Finally, all data-sets included in the ESDC are listed and described in the `annex of the Product Handbook <annex.html#Annexes>`__.

References
==========

.. todo:: GB add more references here

1.  ESDC webpage: http://www.earthsystemdatacube.net

2.  CAB-LAB's github repository: https://github.com/CAB-LAB


Peer-reviewed Publications
==========================

.. todo:: FG add more references here

1. Sippel, S., Zscheischler, J., Heimann, M., Otto, F. E. L., Peters, J. and Mahecha, M. D. (2015),
   Quantifying changes in climate variability and extremes: Pitfalls and their overcoming,
   Geophys. Res. Lett., 42, 9990–9998. doi:10.1002/2015GL066307.


Terms and Abbreviations
=======================

.. todo:: GB keep this section up-to-date

=======================  =============================================================================================
Term                     Description
=======================  =============================================================================================
BAST                     Biosphere-Atmosphere System Trajectory
-----------------------  ---------------------------------------------------------------------------------------------
BAVL                     Biosphere Atmosphere Virtual Laboratory
-----------------------  ---------------------------------------------------------------------------------------------
CAB-LAB                  Coupled Atmosphere Biosphere virtual LABoratory
-----------------------  ---------------------------------------------------------------------------------------------
DAT                      Data Analytics Toolkit
-----------------------  ---------------------------------------------------------------------------------------------
EDSC                     Earth System Data Cube
-----------------------  ---------------------------------------------------------------------------------------------
EO                       Earth Observations
-----------------------  ---------------------------------------------------------------------------------------------
ESA                      European Space Agency
-----------------------  ---------------------------------------------------------------------------------------------
Grid                     The Data Cube's layout given by its spatial and temporal resolution and its variables.
-----------------------  ---------------------------------------------------------------------------------------------
Image                    An 2D data cube subset with dimension (lat, lon)
=======================  =============================================================================================

.. index:: Data Policy

Data Policy
===========

The CAB-LAB team processes and distributes the data in the ESDC in good faith, but makes no warranty, expressed or implied,
nor assumes any legal liability or responsibility for any purpose for which the data are used.
In particular, the CAB-LAB team does not claim ownership of the data distributed through the ESDC nor does it alter the data
policy of the data owner. Therefore, the user is referred to the data owner for specific questions of data use.
References and more details of the data sets are listed in the `annex of the Product Handbook <annex.html#Annexes>`_.

The CAB-LAB team is thankful to have received permissions for re-distribution of all data contained in the ESDC from
the respective data owners.

.. note::

    Please cite the ESDC as:

    The CAB-LAB developer team (2016). The Earth System Data Cube (Version 0.1), available at: https://github.com/CAB-LAB.


.. index:: Legal information

Legal information
=================

The Earth System Data Cube consists of a variety of source data sets from different providers, the Data Cube software, which
transforms all data to the common Data Cube format and allows for convenient data access, and the Data Analytics Toolkit, which
provides methods for scientific analysis.

The Data Cube software and the Data Analytics Toolkit are free software:
you can redistribute it and/or modify it under the terms of the GNU General
Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see http://www.gnu.org/licenses/.

