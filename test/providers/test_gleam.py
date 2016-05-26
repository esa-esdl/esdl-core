import os
import unittest
from datetime import datetime

from cablab import CubeConfig
from cablab.providers.globvapour import GlobVapourProvider
from cablab.util import Config

SOURCE_DIR = Config.instance().get_cube_source_path('Usersgunnar\src\data\GLEAM\v3a_BETA')