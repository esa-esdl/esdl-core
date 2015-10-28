
# CAB-LAB Components:

* `cablab.cube` - Data Cube Generation and Access
* `cablab.cli` - Command-line interface

# Extension points and extensions

## Defined extension points:

* `cablab.image_providers`: *key* = *class derived from `cablab.ImageProvider`*    

## Extensions:

* `cablab.image_providers`: 
  * `'burnt_area = cablab.providers.burnt_area.BurntAreaProvider'`    
* `console_scripts`: 
  * `'cablab_cli = cablab.cli:main'`, see %PYTHON_HOME%/Scripts/cablab_cli.exe (Windows) after installation
    

# How to build

Development mode installation:

    > python setup.py develop
    
or real installation
    
    > python setup.py install
    
    
# How to generate a data cube

Generate a default data cube with a 0.25 degree resolution:

    > cablab_cli.exe testcube burnt_area:W:\BurntArea c_emissions:W:\Emissions ozone:W:\Ozone-CCI\Total_Columns\L3\MERGED precip:W:\CPC_precip

# Dependencies

* netCDF4  >= 1.2
* numpy >= 1.9
* scipy >= 0.16
* matplotlib >= 1.4
* scikit_image >= 0.11

For Windows OS get the Python wheels from Christoph Gohlke's website at http://www.lfd.uci.edu/~gohlke/pythonlibs/.
Install them using

    > pip install <wheel-file>

