from datetime import datetime
import os
import gzip

import numpy
import netCDF4

from cablab import BaseCubeSourceProvider


class CEmissionsProvider(BaseCubeSourceProvider):
    def __init__(self, dir_path):
        super(CEmissionsProvider, self).__init__()
        self.dir_path = dir_path
        self.index_to_file = None
        self.file_to_dataset = dict()
        # check: cache_dir could be a property of CubeConfig
        cache_dir = os.path.join(os.path.join(os.path.expanduser("~"), '.cablab'), 'cache')
        self.temp_path = os.path.join(cache_dir, os.path.basename(self.dir_path))
        self.old_indices = None

    def prepare(self, cube_config):
        # todo - remove check once we have addressed spatial aggregation/interpolation
        if cube_config.grid_width != 1440 or cube_config.grid_height != 720:
            raise ValueError('illegal cube configuration, '
                             'provider does not yet implement spatial aggregation/interpolation')
        super(CEmissionsProvider, self).prepare(cube_config)

    def compute_images_from_sources(self, index_to_weight):

        # close all datasets that wont be used anymore
        new_indices = set(index_to_weight.keys())
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file, _ = self.index_to_file[i]
                self._close_dataset(file)

        self.old_indices = new_indices

        if len(new_indices) == 1:
            i = next(iter(new_indices))
            file, time_index = self.index_to_file[i]
            dataset = self._get_dataset(file)
            emissions = dataset.variables['C_Emissions'][time_index, :, :]
        else:
            emissions_sum = numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width),
                                        dtype=numpy.float32)
            weight_sum = 0.0
            for i in new_indices:
                weight = index_to_weight[i]
                file, time_index = self.index_to_file[i]
                dataset = self._get_dataset(file)
                emissions = dataset.variables['C_Emissions']
                emissions_sum += weight * emissions[time_index, :, :]
                weight_sum += weight
            emissions = emissions_sum / weight_sum

        return {'C_Emissions': emissions}

    def _get_dataset(self, file):
        if file in self.file_to_dataset:
            dataset = self.file_to_dataset[file]
        else:
            root, ext = os.path.splitext(file)
            if ext == '.gz':
                real_file = self._get_unpacked_file(file)
            else:
                real_file = file
            dataset = netCDF4.Dataset(real_file)
            self.file_to_dataset[file] = dataset
        return dataset

    def get_source_time_ranges(self):
        year_to_file = self._get_year_to_file_dict(self.dir_path)
        years = sorted(year_to_file.keys())
        source_time_ranges = []
        self.index_to_file = []
        for year in years:
            for month in range(1, 13):
                t1 = datetime(year, month, 1)
                if month < 12:
                    t2 = datetime(year, month + 1, 1)
                else:
                    t2 = datetime(year + 1, 1, 1)
                source_time_ranges.append((t1, t2))
                self.index_to_file.append((year_to_file[year], month - 1))
        return source_time_ranges

    def get_spatial_coverage(self):
        return -180, -90, 1440, 720

    def get_variable_metadata(self, variable):
        return {
            'datatype': numpy.float32,
            'fill_value': -9999.0,
            'units': 'g C m-2 month-1',
            'long_name': 'CASA-GFED4 BB',
            'scale_factor': 1.0,
            'add_offset': 0.0,
        }

    def close(self):
        files = list(self.file_to_dataset.keys())
        for file in files:
            self._close_dataset(file)

    def _close_dataset(self, file):
        if file not in self.file_to_dataset:
            return
        self.log('closing %s' % file)
        dataset = self.file_to_dataset[file]
        dataset.close()
        del self.file_to_dataset[file]

    def _get_unpacked_file(self, file):
        root, _ = os.path.splitext(file)
        filename = os.path.basename(root)
        real_file = os.path.join(self.temp_path, filename)
        if not os.path.exists(real_file):
            if not os.path.exists(self.temp_path):
                os.makedirs(self.temp_path, exist_ok=True)
            self.log('unpacking %s to %s' % (file, real_file))
            with gzip.open(file, 'rb') as istream:
                with open(real_file, 'wb') as ostream:
                    ostream.write(istream.read())
        return real_file

    @staticmethod
    def _get_year_to_file_dict(dir_path):
        files = os.listdir(dir_path)
        file_dict = dict()
        for file in files:
            parts = file.split('.')
            if parts[-1] == 'gz' and parts[-2] == 'nc':
                year = int(parts[-3])
                file_dict[year] = os.path.join(dir_path, file)
        return file_dict
