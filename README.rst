.. image:: https://travis-ci.org/esa-esdl/esdl-core.svg?branch=master
    :target: https://travis-ci.org/esa-esdl/esdl-core
.. image:: https://ci.appveyor.com/api/projects/status/qvtsx40uv7p0e1tn?svg=true
   :target: https://ci.appveyor.com/project/hans-permana/esdl-core
.. image:: https://codecov.io/gh/esa-esdl/esdl-core/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/esa-esdl/esdl-core


==========
ESDL Core
==========

----------
Components
----------

* ``esdl`` - Public ESDL API
* ``esdl.cube`` - Data Cube Generation and Access (protected, public parts expr)
* ``esdl.cube_cli`` - Command-line interface (protected)
* ``esdl.util`` - Common utility functions (protected)


-------------
Documentation
-------------

Find the ESDL documentation `here <https://esdl.readthedocs.io/en/latest/>`_.

---------------
Developer Guide
---------------

Style
-----

Adhere to PEP-8!

TODOs
-----

Only place TODOs in source code when you have an according issue on GitHub. Mention the issue number in the TODO text.
When fixing a TODO, mention the issue in the commit message.

Tests
-----

Test code in the ``test`` and ``test/providers`` directories should only use libraries that are anyway used by the
production code in ``src``. If you want to check out new libraries for appropriateness please do so in the
``test/sandbox`` directory.

-------------------------------
Extension points and extensions
-------------------------------

Defined extension points
------------------------

* ``esdl.image_providers``: *key* = *class derived from* ``esdl.ImageProvider``

Extensions
----------

* ``esdl.image_providers``:
  * ``'burnt_area = esdl.providers.burnt_area.BurntAreaProvider'``
* ``console_scripts``: 
  * ``'esdl_cli = esdl.cli:main'``, see %PYTHON_HOME%/Scripts/esdl_cli (*.exe on Windows) after installation
    

------------
How to build
------------

Development mode installation::

    > python setup.py develop
    
or real installation::
    
    > python setup.py install
    
    

How to generate a data cube
---------------------------

Create a file ``esdl-config.py`` in your project root directory or your current working directory and add the
following entry::

    cube_sources_root = <your local cube source directory>


To generate a default data cube with a 0.25 degree resolution and variables 'BurntArea', 'C_Emmisions', Ozone', 
'Precip' call the ``cube-gen`` tool::

    > cube-gen testcube burnt_area:dir=BurntAreaDir c_emissions:dir=EmissionsDir ozone:Ozone-CCI/Total_Columns/L3/MERGED precip:dir=CPC_precip

It's usage is::

    > cube-gen <cube-dir> [<provider-key>:dir=<source-path> ...]

------------
Dependencies
------------

If you use Windows, get the Python wheels from Christoph Gohlke's website at http://www.lfd.uci.edu/~gohlke/pythonlibs/.
Install them using::

    > pip install <wheel-file>

Production and test code dependencies
-------------------------------------

* netCDF4  >= 1.2
* numpy >= 1.9
* gridtools
* zarr



