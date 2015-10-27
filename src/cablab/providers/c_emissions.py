from datetime import datetime
import os
import gzip

import numpy
import netCDF4

from cablab import BaseImageProvider


class CEmissionsProvider(BaseImageProvider):
    def __init__(self, dir_path):
        super(CEmissionsProvider, self).__init__()
        self.dir_path = dir_path
        self.time_range_to_file = None
        self.open_datasets = dict()
        # check: cache_dir could be a property of CubeConfig
        cache_dir = os.path.join(os.path.join(os.path.expanduser("~"), '.cablab'), 'cache')
        self.temp_path = os.path.join(cache_dir, os.path.basename(self.dir_path))
        self.old_indices = None

    def compute_images_from_sources(self, source_indices_to_time_overlap):

        # close all datasets that wont be used anymore
        new_indices = source_indices_to_time_overlap.keys()
        if self.old_indices:
            unused_indices = self.old_indices - new_indices
            for i in unused_indices:
                file, _ = self.time_range_to_file[i]
                if file in self.open_datasets:
                    self.open_datasets[file].close()
                    del self.open_datasets[file]

        self.old_indices = new_indices

        emissions_sum = numpy.zeros((self.cube_config.grid_height, self.cube_config.grid_width), dtype=numpy.float32)
        weight_sum = 0.0
        for i in new_indices:
            weight = source_indices_to_time_overlap[i]
            file, time_index = self.time_range_to_file[i]

            if file in self.open_datasets:
                dataset = self.open_datasets[file]
            else:
                root, ext = os.path.splitext(file)
                if ext == '.gz':
                    # Unpack to temp_path, if it is gzipped
                    real_file = os.path.join(self.temp_path, os.path.basename(root))
                    if not os.path.exists(real_file):
                        if not os.path.exists(self.temp_path):
                            os.makedirs(self.temp_path, exist_ok=True)
                        with gzip.open(file, 'rb') as istream:
                            with open(real_file, 'wb') as ostream:
                                ostream.write(istream.read())
                else:
                    real_file = file
                dataset = netCDF4.Dataset(real_file)
                self.open_datasets[file] = dataset

            emissions = dataset.variables['C_Emissions']
            emissions_sum += weight * emissions[time_index, :, :]
            weight_sum += weight

        return {'C_Emissions': emissions_sum / weight_sum}

    def get_source_time_ranges(self):
        file_dict = self._get_year_to_file_dict(self.dir_path)
        years = sorted(file_dict.keys())
        source_time_ranges = []
        self.time_range_to_file = []
        for year in years:
            for month in range(1, 13):
                t1 = datetime(year, month, 1)
                if month < 12:
                    t2 = datetime(year, month + 1, 1)
                else:
                    t2 = datetime(year + 1, 1, 1)
                source_time_ranges.append((t1, t2))
                self.time_range_to_file.append((file_dict[year], month - 1))
        return source_time_ranges

    def get_spatial_coverage(self):
        return -180, -90, 1440, 720

    def close(self):
        for dataset in self.open_datasets.values():
            dataset.close()

    def get_variable_metadata(self, variable):
        metadata = {
            'datatype': numpy.float32,
            'fill_value': -9999.0,
            'units': 'g C m-2 month-1',
            'long_name': 'CASA-GFED4 BB',
            'scale_factor': 1.0,
            'add_offset': 0.0,
        }
        return metadata

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
