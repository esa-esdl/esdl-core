try:
    import setuptools
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name="cablab-core",
    version="0.2.0",
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
            'open_water_evaporation = cablab.providers.gleam:GleamProvider'
        ],
    },
    # *Minimum* requirements
    install_requires=['numpy', 'netCDF4', 'gridtools'],
)
