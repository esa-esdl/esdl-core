try:
    import setuptools
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()

from setuptools import setup, find_packages


def get_version():
    version_file = 'cablab/version.py'
    locals = {}
    try:
        execfile(version_file, None, locals)
    except NameError:
        with open(version_file) as fp:
            exec(fp.read(), None, locals)
    return locals['version']


# Same effect as "from ect import __version__", but avoids importing ect:
__version__ = get_version()

packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

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
    packages=packages,
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
            'snow_water_equivalent = cablab.providers.snow_water_equivalent:SnowWaterEquivalentProvider',
            'root_moisture = cablab.providers.gleam:GleamProvider',
            'evaporation = cablab.providers.gleam:GleamProvider',
            'evaporative_stress = cablab.providers.gleam:GleamProvider',
            'potential_evaporation = cablab.providers.gleam:GleamProvider',
            'interception_loss = cablab.providers.gleam:GleamProvider',
            'surface_moisture = cablab.providers.gleam:GleamProvider',
            'bare_soil_evaporation = cablab.providers.gleam:GleamProvider',
            'snow_sublimation = cablab.providers.gleam:GleamProvider',
            'transpiration = cablab.providers.gleam:GleamProvider',
            'open_water_evaporation = cablab.providers.gleam:GleamProvider',
            'land_surface_temperature = cablab.providers.land_surface_temperature:LandSurfTemperatureProvider',
            'latent_energy = cablab.providers.mpi_bgc:MPIBGCProvider',
            'sensible_heat = cablab.providers.mpi_bgc:MPIBGCProvider',
            'net_ecosystem_exchange = cablab.providers.mpi_bgc:MPIBGCProvider',
            'terrestrial_ecosystem_respiration = cablab.providers.mpi_bgc:MPIBGCProvider',
            'gross_primary_production = cablab.providers.mpi_bgc:MPIBGCProvider',
            'country_mask = cablab.providers.country_mask:CountryMaskProvider',
            'srex_mask = cablab.providers.srex_mask:SrexMaskProvider',
            'water_mask = cablab.providers.water_mask:WaterMaskProvider',
        ],
    },
    # *Minimum* requirements
    install_requires=['numpy', 'netCDF4', 'gridtools', 'xarray', 'h5netcdf'],
)
