import datetime
import os
from datetime import timedelta

import numpy

from esdl.cube_provider import NetCDFCubeSourceProvider


class AerosolsProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='aerosols', dir=None, resampling_order=None):
        super(AerosolsProvider, self).__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'AAOD550_mean': {
                'source_name': 'AAOD550_mean',
                'data_type': numpy.float32,
                'fill_value': -999.0,
                'units': '1',
                'long_name': 'Aerosol Optical Thickness at 1610 nm',
                'standard_name': 'atmosphere_optical_thickness_due_to_aerosol_at_1610nm',
                'references': 'Holzer-Popp, T., de Leeuw, G., Griesfeller, J., Martynenko, D., Klueser, L., Bevan, S., et al. (2013). Aerosol retrieval experiments in the ESA Aerosol_cci project. Atmospheric Measurement Techniques, 6, 1919-1957. doi:10.5194/amt-6-1919-2013. ',
                'comment': 'Aerosol optical thickness derived from the dataset produced by the Aerosol CCI project.',
                'url': 'http://www.esa-aerosol-cci.org/',
                'project_name': 'ESA Aerosol CCI',
            },
        }

    def compute_source_time_ranges(self):
        source_time_ranges = []
        for root, sub_dirs, files in os.walk(self.dir_path):
            for file_name in files:
                time_info = file_name.split('-', 1)[0]

                time = self.day2date(int(time_info))

                if self.cube_config.start_time <= time <= self.cube_config.end_time:
                    file = os.path.join(root, file_name)
                    self.dataset_cache.get_dataset(file)
                    self.dataset_cache.close_dataset(file)
                    source_time_ranges.append((time, time + timedelta(days=1), file, 0))
        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by flipping and then shifting horizontally.
        :param source_image: 2D image
        :return: source_image
        """
        #return numpy.flipud(source_image)
        return source_image

    @staticmethod
    def day2date(times):

        """
        Return datetime objects given numeric time values in year and day format.
        For example, 2005021 corresponds to the 21st day of year 2005.

        >>> AerosolsProvider.day2date(20020724)
        datetime.datetime(2002, 7, 24, 0, 0)
        >>> AerosolsProvider.day2date(20020901)
        datetime.datetime(2002, 9, 1, 0, 0)
        >>> AerosolsProvider.day2date(20071020)
        datetime.datetime(2007, 10, 20, 0, 0)

        :param times: numeric time values
        :return: datetime.datetime values
        """

        year = times // 10000
        month_date = times % 10000
        month = month_date // 100
        date = month_date % 100

        return datetime.datetime(year, month, date)
