"""
A list of available providers.
A provider is created for each input dataset so that an individual treatment in regards to data reading and
aggregation/interpolation can be applied.
"""

from .aerosols import AerosolsProvider
from .air_temperature import AirTemperatureProvider
from .albedo import AlbedoProvider
from .burnt_area import BurntAreaProvider
from .c_emissions import CEmissionsProvider
from .country_mask import CountryMaskProvider
from .gleam import GleamProvider
from .globvapour import GlobVapourProvider
from .land_surface_temperature import LandSurfTemperatureProvider
from .mpi_bgc import MPIBGCProvider
from .ozone import OzoneProvider
from .precip import PrecipProvider
from .snow_area_extent import SnowAreaExtentProvider
from .snow_water_equivalent import SnowWaterEquivalentProvider
from .soil_moisture import SoilMoistureProvider
from .water_mask import WaterMaskProvider
from .test_provider import TestCubeSourceProvider

__author__ = 'Brockmann Consult GmbH'

__all__ = [
    'AerosolsProvider',
    'AirTemperatureProvider',
    'AlbedoProvider',
    'BurntAreaProvider',
    'CEmissionsProvider',
    'CountryMaskProvider',
    'GleamProvider',
    'GlobVapourProvider',
    'LandSurfTemperatureProvider',
    'MPIBGCProvider',
    'OzoneProvider',
    'PrecipProvider',
    'SnowAreaExtentProvider',
    'SnowWaterEquivalentProvider',
    'SoilMoistureProvider',
    'WaterMaskProvider',
    'TestCubeSourceProvider'
]
