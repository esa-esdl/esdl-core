import os

import numpy
import datetime

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache, aggregate_images
from skimage.transform import resize
from netCDF4 import date2num, num2date

# VAR_NAME = 'Snow_Fraction'
VAR_NAME_BRIGHT = 'BHR_VIS'
VAR_NAME_DARK = 'DHR_VIS'
VAR_NAME = [VAR_NAME_BRIGHT, VAR_NAME_DARK]


class AlbedoProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, dir_path):
        super(AlbedoProvider, self).__init__(cube_config)
        # todo (hp 20151030) - remove check once we have addressed spatial aggregation/interpolation, see issue #3
        if cube_config.grid_width != 1440 or cube_config.grid_height != 720:
            raise ValueError('illegal cube configuration, '
                             'provider does not yet implement spatial aggregation/interpolation')
        self.dir_path = dir_path
        self.dataset_cache = NetCDFDatasetCache("albedo")
        self.source_time_ranges = None
        self.old_indices = None

    def prepare(self):
        self._init_source_time_ranges()

    def get_variable_descriptors(self):
        return {
            VAR_NAME_BRIGHT: {
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': '-',
                'long_name': 'White Sky Albedo in VIS',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            VAR_NAME_DARK: {
                'data_type': numpy.float32,
                'fill_value': numpy.nan,
                'units': '-',
                'long_name': 'Black Sky Albedo in VIS',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            }
        }

    def compute_variable_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file, _ = self._get_file_and_time_index(i)
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file, _ = self._get_file_and_time_index(i)
            dataset = self.dataset_cache.get_dataset(file)
            albedo = {i: resize(dataset.variables[i][0, :, :], (720, 1440), preserve_range=True, order=3) for i in
                      VAR_NAME}
        else:
            images_bright = [None] * len(new_indices)
            images_dark = [None] * len(new_indices)
            weights = [None] * len(new_indices)
            j = 0
            for i in new_indices:
                file, _ = self._get_file_and_time_index(i)
                dataset = self.dataset_cache.get_dataset(file)
                images_bright[j] = resize(dataset.variables[VAR_NAME_BRIGHT][0, :, :], (720, 1440), preserve_range=True,
                                          order=3)
                images_dark[j] = resize(dataset.variables[VAR_NAME_DARK][0, :, :], (720, 1440), preserve_range=True,
                                        order=3)
                weights[j] = index_to_weight[i]
                j += 1
            images = {VAR_NAME_BRIGHT: images_bright, VAR_NAME_DARK: images_dark}
            albedo = {i: aggregate_images(images[i], weights=weights) for i in VAR_NAME}

        return {i: albedo[i] for i in VAR_NAME}

    def _get_file_and_time_index(self, i):
        return self.source_time_ranges[i][2:4]

    def get_source_time_ranges(self):
        return self.source_time_ranges

    def get_spatial_coverage(self):
        return 0, 0, 1440, 720

    def close(self):
        self.dataset_cache.close_all_datasets()

    def _init_source_time_ranges(self):
        source_time_ranges = []

        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            time_info = file_name.split('.', 5)[4]
            t1, t2 = self._day2date(int(time_info))
            if self.cube_config.start_time <= t1 <= self.cube_config.end_time:
                file = os.path.join(self.dir_path, file_name)
                self.dataset_cache.get_dataset(file)
                self.dataset_cache.close_dataset(file)
                source_time_ranges.append((t1, t2, file, 0))

        self.source_time_ranges = sorted(source_time_ranges, key=lambda item: item[0])

    @staticmethod
    def _day2date(times):
        """
        Return datetime objects given numeric time values in year and day format.
        For example, 2005021 corresponds to the 21st day of year 2005.

        >>> AlbedoProvider._day2date(2000001)
        (datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 9, 0, 0))
        >>> AlbedoProvider._day2date(2000361)
        (datetime.datetime(2000, 12, 26, 0, 0), datetime.datetime(2001, 1, 3, 0, 0))

        :param times: numeric time values
        :return: datetime.datetime values
        """
        year = times // 1000
        year_start_date = date2num(datetime.datetime(year, 1, 1), units='days since 0001-1-1 00:00',
                                   calendar='gregorian')

        day = times % 1000 - 1
        actual_start_date = year_start_date + day
        actual_end_date = actual_start_date + 8

        return num2date(actual_start_date, units='days since 0001-1-1 00:00', calendar='gregorian'), num2date(
            actual_end_date, units='days since 0001-1-1 00:00',
            calendar='gregorian')
