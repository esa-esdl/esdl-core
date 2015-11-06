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
'Precip' call the ``cablab-cli`` tool::

    > cablab-cli testcube burnt_area:BurntArea c_emissions:Emissions ozone:Ozone-CCI/Total_Columns/L3/MERGED precip:CPC_precip

It's usage is::

    > cablab-cli <cube-dir> [<provider-key>:<source-path> ...]

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
* scikit_image >= 0.11
* scipy >= 0.16
* matplotlib >= 1.4



