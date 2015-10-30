try:
    import setuptools
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name="cablab-core",
    version="0.1.0",
    description='CAB-LAB Data Cube Software',
    license='GPL 3',
    author='CAB-LAB Development Team',
    author_email='cablab@earthsystemdatacube.net',
    maintainer='Brockmann Consult GmbH',
    maintainer_email='cablab@earthsystemdatacube.net',
    url='http://earthsystemdatacube.net/',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'cube_cli = cablab.cube_cli:main',
        ],
        'cablab.source_providers': [
            'burnt_area = cablab.providers.burnt_area:BurntAreaProvider',
            'c_emissions = cablab.providers.c_emissions:CEmissionsProvider',
            'ozone = cablab.providers.ozone:OzoneProvider',
            'precip = cablab.providers.precip:PrecipProvider',
            'soil_moisture = cablab.providers.soil_moisture:SoilMoistureProvider',
        ],
    },
    requires=['numpy', 'netCDF4']
)
