import datetime
import os
from datetime import timedelta

import gridtools.resampling as gtr
import numpy

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache, aggregate_images

VAR_NAME_1610 = 'AOD1610_mean'
VAR_NAME_550 = 'AOD550_mean'
VAR_NAME_555 = 'AOD555_mean'
VAR_NAME_659 = 'AOD659_mean'
VAR_NAME_865 = 'AOD865_mean'
VAR_NAME = [VAR_NAME_550, VAR_NAME_555, VAR_NAME_659, VAR_NAME_865, VAR_NAME_1610]
FILL_VALUE = -999.0


class AerosolsProvider(BaseCubeSourceProvider):
    def __init__(self, cube_config, dir_path):
        super(AerosolsProvider, self).__init__(cube_config)
        self.dir_path = dir_path
        self.dataset_cache = NetCDFDatasetCache(VAR_NAME_1610)
        self.source_time_ranges = None
        self.old_indices = None

    def prepare(self):
        self._init_source_time_ranges()

    def get_variable_descriptors(self):
        return {
            VAR_NAME_1610: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': '1',
                'long_name': 'aerosol optical thickness at 1610 nm',
                'standard_name': 'atmosphere_optical_thickness_due_to_aerosol',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            VAR_NAME_550: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': '1',
                'long_name': 'aerosol optical thickness at 550 nm',
                'standard_name': 'atmosphere_optical_thickness_due_to_aerosol',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            VAR_NAME_555: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': '1',
                'long_name': 'aerosol optical thickness at 555 nm',
                'standard_name': 'atmosphere_optical_thickness_due_to_aerosol',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            VAR_NAME_659: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': '1',
                'long_name': 'aerosol optical thickness at 659 nm',
                'standard_name': 'atmosphere_optical_thickness_due_to_aerosol',
                'scale_factor': 1.0,
                'add_offset': 0.0,
            },
            VAR_NAME_865: {
                'data_type': numpy.float32,
                'fill_value': FILL_VALUE,
                'units': '1',
                'long_name': 'aerosol optical thickness at 865 nm',
                'standard_name': 'atmosphere_optical_thickness_due_to_aerosol',
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
            aerosols = {i: self.dataset_cache.get_dataset(file).variables[i][0, :, :] for i in VAR_NAME}
        else:
            images_1660 = [None] * len(new_indices)
            images_550 = [None] * len(new_indices)
            images_555 = [None] * len(new_indices)
            images_659 = [None] * len(new_indices)
            images_865 = [None] * len(new_indices)
            weights = [None] * len(new_indices)
            j = 0
            for i in new_indices:
                file, _ = self._get_file_and_time_index(i)
                images_1660[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME_1610][0, :, :]
                images_550[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME_550][0, :, :]
                images_555[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME_555][0, :, :]
                images_659[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME_659][0, :, :]
                images_865[j] = self.dataset_cache.get_dataset(file).variables[VAR_NAME_865][0, :, :]
                weights[j] = index_to_weight[i]
                j += 1
            images = {VAR_NAME_550: images_550, VAR_NAME_555: images_555, VAR_NAME_659: images_659,
                      VAR_NAME_865: images_865, VAR_NAME_1610: images_1660}
            aerosols = {i: aggregate_images(images[i], weights=weights) for i in VAR_NAME}

        aerosols = {i: gtr.resample_2d(aerosols[i][:, :], self.cube_config.grid_width, self.cube_config.grid_height,
                                       us_method=gtr.US_NEAREST, fill_value=FILL_VALUE)
                    for i in VAR_NAME}
        return {i: aerosols[i] for i in VAR_NAME}

    def _get_file_and_time_index(self, i):
        return self.source_time_ranges[i][2:4]

    def get_source_time_ranges(self):
        return self.source_time_ranges

    def get_spatial_coverage(self):
        return 0, 0, self.cube_config.grid_width, self.cube_config.grid_height

    def close(self):
        self.dataset_cache.close_all_datasets()

    def _init_source_time_ranges(self):
        source_time_ranges = []

        for root, sub_dirs, files in os.walk(self.dir_path):
            for sub_dir in sub_dirs:
                source_year = int(sub_dir)
                if self.cube_config.start_time.year <= source_year <= self.cube_config.end_time.year:
                    sub_dir_path = os.path.join(self.dir_path, sub_dir)
                    file_names = os.listdir(sub_dir_path)
                    for file_name in file_names:
                        time_info = file_name.split('-', 1)[0]
                        time = self._day2date(int(time_info))
                        if self.cube_config.start_time <= time <= self.cube_config.end_time:
                            file = os.path.join(sub_dir_path, file_name)
                            self.dataset_cache.get_dataset(file)
                            self.dataset_cache.close_dataset(file)
                            source_time_ranges.append((time, time + timedelta(days=1), file, 0))
        self.source_time_ranges = sorted(source_time_ranges, key=lambda item: item[0])

    @staticmethod
    def _day2date(times):

        """
        Return datetime objects given numeric time values in year and day format.
        For example, 2005021 corresponds to the 21st day of year 2005.

        >>> AerosolsProvider._day2date(20020724)
        datetime.datetime(2002, 7, 24, 0, 0)
        >>> AerosolsProvider._day2date(20020901)
        datetime.datetime(2002, 9, 1, 0, 0)
        >>> AerosolsProvider._day2date(20071020)
        datetime.datetime(2007, 10, 20, 0, 0)

        :param times: numeric time values
        :return: datetime.datetime values
        """

        year = times // 10000
        month_date = times % 10000
        month = month_date // 100
        date = month_date % 100

        return datetime.datetime(year, month, date)
