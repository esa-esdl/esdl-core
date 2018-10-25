import os

try:
    import setuptools
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()

from setuptools import setup, find_packages


def get_version():
    version_file = 'esdl/version.py'
    locals = {}
    try:
        execfile(version_file, None, locals)
    except NameError:
        with open(version_file) as fp:
            exec(fp.read(), None, locals)
    return locals['version']


# Same effect as "from ect import __version__", but avoids importing ect:
__version__ = get_version()

# in alphabetical oder
requirements = [
    # Exclude 'gridtools' as it is only required for Cube production
    # 'gridtools',
    'h5netcdf',
    'netCDF4',
    'numpy',
    'xarray',
]

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    # On READTHEDOCS, all dependencies are mocked (except tornado)
    # see doc/source/conf.py and readthedocs-env.yml
    requirements = ['gridtools']

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

setup(
    name="esdl-core",
    version=__version__,
    description='ESDL Cube Software',
    license='GPL 3',
    author='ESDL Development Team',
    author_email='esdl@earthsystemdatacube.net',
    maintainer='Brockmann Consult GmbH',
    maintainer_email='admin@earthsystemdatalab.net',
    url='http://earthsystemdatalab.net/',
    packages=packages,
    entry_points={
        'console_scripts': [
            'cube-gen = esdl.cube_gen:main',
        ],
        'cate_plugins': [
            'cate_esdc = esdl.cate.cube_read:cate_init',
        ],
        'esdl.source_providers': [
            'test = esdl.providers:TestCubeSourceProvider',
            'burnt_area = esdl.providers.burnt_area:BurntAreaProvider',
            'c_emissions = esdl.providers.c_emissions:CEmissionsProvider',
            'ozone = esdl.providers.ozone:OzoneProvider',
            'precip = esdl.providers.precip:PrecipProvider',
            'soil_moisture = esdl.providers.soil_moisture:SoilMoistureProvider',
            'albedo = esdl.providers.albedo:AlbedoProvider',
            'snow_area_extent = esdl.providers.snow_area_extent:SnowAreaExtentProvider',
            'aerosols = esdl.providers.aerosols:AerosolsProvider',
            'globvapour = esdl.providers.globvapour:GlobVapourProvider',
            'air_temperature = esdl.providers.air_temperature:AirTemperatureProvider',
            'snow_water_equivalent = esdl.providers.snow_water_equivalent:SnowWaterEquivalentProvider',
            'root_moisture = esdl.providers.gleam:GleamProvider',
            'evaporation = esdl.providers.gleam:GleamProvider',
            'evaporative_stress = esdl.providers.gleam:GleamProvider',
            'potential_evaporation = esdl.providers.gleam:GleamProvider',
            'interception_loss = esdl.providers.gleam:GleamProvider',
            'surface_moisture = esdl.providers.gleam:GleamProvider',
            'bare_soil_evaporation = esdl.providers.gleam:GleamProvider',
            'snow_sublimation = esdl.providers.gleam:GleamProvider',
            'transpiration = esdl.providers.gleam:GleamProvider',
            'open_water_evaporation = esdl.providers.gleam:GleamProvider',
            'land_surface_temperature = esdl.providers.land_surface_temperature:LandSurfTemperatureProvider',
            'latent_energy = esdl.providers.mpi_bgc:MPIBGCProvider',
            'sensible_heat = esdl.providers.mpi_bgc:MPIBGCProvider',
            'net_ecosystem_exchange = esdl.providers.mpi_bgc:MPIBGCProvider',
            'terrestrial_ecosystem_respiration = esdl.providers.mpi_bgc:MPIBGCProvider',
            'gross_primary_productivity = esdl.providers.mpi_bgc:MPIBGCProvider',
            'country_mask = esdl.providers.country_mask:CountryMaskProvider',
            'srex_mask = esdl.providers.srex_mask:SrexMaskProvider',
            'water_mask = esdl.providers.water_mask:WaterMaskProvider',
            'lai_fapar_tip = esdl.providers.lai_fapar_tip:LaiFaparTipProvider',
            'albedo_avhrr = esdl.providers.albedo_avhrr:AlbedoAVHRRProvider',
        ],
    },
    # *Minimum* requirements
    install_requires=requirements
)
