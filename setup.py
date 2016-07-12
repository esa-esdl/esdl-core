try:
    import setuptools
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()

from setuptools import setup, find_packages


def get_version():
    version_file = 'src/cablab/version.py'
    locals = {}
    try:
        execfile(version_file, None, locals)
    except NameError:
        with open(version_file) as fp:
            exec(fp.read(), None, locals)
    return locals['version']


# Same effect as "from ect import __version__", but avoids importing ect:
__version__ = get_version()

setup(
    name="cablab-core",
    version=__version__,
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
            'cube-gen = cablab.cube_gen:main',
        ],
        'cablab.source_providers': [
            'test = cablab:TestCubeSourceProvider',
            'burnt_area = cablab.providers.burnt_area:BurntAreaProvider',
            'c_emissions = cablab.providers.c_emissions:CEmissionsProvider',
            'ozone = cablab.providers.ozone:OzoneProvider',
            'precip = cablab.providers.precip:PrecipProvider',
            'soil_moisture = cablab.providers.soil_moisture:SoilMoistureProvider',
            'albedo = cablab.providers.albedo:AlbedoProvider',
            'snow_area_extent = cablab.providers.snow_area_extent:SnowAreaExtentProvider',
            'aerosols = cablab.providers.aerosols:AerosolsProvider',
            'globvapour = cablab.providers.globvapour:GlobVapourProvider',
            'air_temperature = cablab.providers.air_temperature:AirTemperatureProvider',
            'snow_water_equivalent = cablab.providers.snow_water_equivalent:SnowWaterEquivalentProvider'
        ],
    },
    # *Minimum* requirements
    install_requires=['numpy', 'netCDF4', 'gridtools', 'xarray', 'h5netcdf'],
)
