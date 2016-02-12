============
Introduction
============

.. BC

Project background
==================

The steadily growing Earth Observation (EO) archives are currently mostly investigated
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

The Product Handbook gives a general overview of the `ESCD's structure <cube_explanation.html#What is the Earth System Data Cube?>`__
and provide some examples to illustrate `potential uses of the system <cube_scenarios.html#What can I do with the Earth System Data Cube?>`__ .
The main part is considered with a detailed `technical description of the ESDC <cube_usage.html#How can I use the Earth System Data Cube?>`__
, which is accompanied by the full `specification of the API <api_reference.html#CAB-LAB API Reference>`__.
Finally, all data-sets included in the ESDC are listed and described in the `annex of the Product Handbook <annex.html#Annexes>`__.

References
==========

.. todo:: GB add more references here

1.  CAB-LAB's webpage: http://www.earthsystemdatacube.net

2.  CAB-LAB's github repository: https://github.com/CAB-LAB

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

Copyright (C) 2016  The CAB-LAB developer team.

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

    Please cite the Earth System Data Cube as:

    The CAB-LAB developer team (2016). The Earth System Data Cube (Version 0.1), available at: https://github.com/CAB-LAB.
