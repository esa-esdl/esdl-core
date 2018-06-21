import os
from datetime import datetime

import netCDF4
import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class OzoneProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='ozone', dir=None, resampling_order=None):
        super(OzoneProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'ozone': {
                'source_name': 'atmosphere_mole_content_of_ozone',
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': 'DU',
                'long_name': 'Mean total ozone column in dobson units',
                'standard_name': 'atmosphere_mole_content_of_ozone',
                'references': 'Laeng, A., et al. "The ozone climate change initiative: Comparison of four '
                              'Level-2 processors for the Michelson Interferometer for Passive Atmospheric '
                              'Sounding (MIPAS)." Remote Sensing of Environment 162 (2015): 316-343.',
                'comment': 'Atmospheric ozone based on the Ozone CCI data.',
                'url': 'http://www.esa-ozone-cci.org/',
                'project_name' : 'Ozone CCI',
            }
        }

    def compute_source_time_ranges(self):
        file_names = os.listdir(self.dir_path)
        source_time_ranges = list()
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = netCDF4.Dataset(file)
            t1 = dataset.time_coverage_start
            t2 = dataset.time_coverage_end
            dataset.close()
            source_time_ranges.append((datetime(int(t1[0:4]), int(t1[4:6]), int(t1[6:8])),
                                       datetime(int(t2[0:4]), int(t2[4:6]), int(t2[6:8])),
                                       file,
                                       None))
        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by flipping and then shifting horizontally.
        :param source_image: 2D image
        :return: source_image
        """
        # TODO (hans-permana, 20161219): the following line is a workaround to an issue where the nan values are
        # always read as -9.9. Find out why these values are automatically converted and create a better fix.
        source_image[source_image == -9.9] = numpy.nan
        return numpy.roll(numpy.flipud(source_image), 180, axis=1)
