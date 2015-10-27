import os
from  datetime import datetime

import numpy
import netCDF4

from cablab import BaseCubeSourceProvider
from cablab.util import NetCDFDatasetCache

VAR_NAME = 'atmosphere_mole_content_of_ozone'


class OzoneProvider(BaseCubeSourceProvider):
    def __init__(self, dir_path):
        super(OzoneProvider, self).__init__()
        self.dir_path = dir_path
        self.files = None
        self.dataset_cache = NetCDFDatasetCache(VAR_NAME)
        self.old_indices = None

    def prepare(self, cube_config):
        # todo - remove check once we have addressed spatial aggregation/interpolation
        if cube_config.grid_width != 1440 or cube_config.grid_height != 720:
            raise ValueError('illegal cube configuration, '
                             'provider does not yet implement proper spatial aggregation/interpolation')
        super(OzoneProvider, self).prepare(cube_config)

    def compute_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file = self.files[i]
                self.dataset_cache.close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file = self.files[i]
            dataset = self.dataset_cache.get_dataset(file)
            ozone = dataset.variables[VAR_NAME]
            ozone = numpy.kron(ozone[:, :], numpy.ones((4, 4), dtype=numpy.float32))
            print(ozone.shape)
        else:
            ozone_sum = numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width),
                                    dtype=numpy.float32)
            weight_sum = 0.0
            for i in new_indices:
                weight = index_to_weight[i]
                file = self.files[i]
                dataset = self.dataset_cache.get_dataset(file)
                ozone = dataset.variables[VAR_NAME]
                ozone = numpy.kron(ozone[:, :], numpy.ones((4, 4), dtype=numpy.float32))
                ozone_sum += weight * ozone
                weight_sum += weight
            ozone = ozone_sum / weight_sum

        return {VAR_NAME: ozone}

    def get_source_time_ranges(self):
        file_names = os.listdir(self.dir_path)
        time_range_recs = list()
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = netCDF4.Dataset(file)
            t1 = dataset.time_coverage_start
            t2 = dataset.time_coverage_end
            dataset.close()
            print('%s: %s ... %s' % (file, t1, t2))
            time_range_recs.append((datetime(int(t1[0:4]), int(t1[4:6]), int(t1[6:8])),
                                    datetime(int(t2[0:4]), int(t2[4:6]), int(t2[6:8])),
                                    file))
        time_range_recs = sorted(time_range_recs, key=lambda rec: rec[0])

        self.files = list()
        time_ranges = list()
        for rec in time_range_recs:
            time_ranges.append((rec[0], rec[1]))
            self.files.append(rec[2])

        return time_ranges

    def get_spatial_coverage(self):
        return 0, 0, 1440, 720

    def get_variable_metadata(self, variable):
        return {
            'datatype': numpy.float32,
            'fill_value': numpy.NaN,
            'units': 'DU',
            'long_name': 'Mean Total Ozone Column in Dobson Units',
            'scale_factor': 1.0,
            'add_offset': 0.0,
            'standard_name': 'atmosphere_mole_content_of_ozone',
        }

    def close(self):
        self.dataset_cache.close_all_datasets()
