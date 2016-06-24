============
CAB-LAB Core 
============

----------
Components
----------

* ``cablab`` - Public CAB-LAB API
* ``cablab.cube`` - Data Cube Generation and Access (protected, public parts expr) 
* ``cablab.cube_cli`` - Command-line interface (protected) 
* ``cablab.util`` - Common utility functions (protected)


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

* ``cablab.image_providers``: *key* = *class derived from* ``cablab.ImageProvider``    

Extensions
----------

* ``cablab.image_providers``: 
  * ``'burnt_area = cablab.providers.burnt_area.BurntAreaProvider'``    
* ``console_scripts``: 
  * ``'cablab_cli = cablab.cli:main'``, see %PYTHON_HOME%/Scripts/cablab_cli (*.exe on Windows) after installation
    

------------
How to build
------------

Development mode installation::

    > python setup.py develop
    
or real installation::
    
    > python setup.py install
    
    

How to generate a data cube
---------------------------

Create a file ``cablab-config.py`` in your project root directory or your current working directory and add the 
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



