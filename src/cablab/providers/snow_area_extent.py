import os
from datetime import timedelta

import gridtools.resampling as gtr
import netCDF4
import numpy

from cablab import NetCDFCubeSourceProvider
from cablab.util import Config, NetCDFDatasetCache, aggregate_images, temporal_weight

VAR_NAME = 'MFSC'
FILL_VALUE = -9999


class SnowAreaExtentProvider(NetCDFCubeSourceProvider):
    def __init__(self, cube_config, name='snow_area_extent', dir=None):
        super(SnowAreaExtentProvider, self).__init__(cube_config, name, dir)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'fractional_snow_cover': {
                'source_name': 'MFSC',
                'data_type': numpy.float32,
                'fill_value': -9999.0,
                'units': 'percent',
                # 'long_name': 'level 3b fractional snow cover (%) aggregated monthly',
            }
        }

    def compute_variable_images_from_sources(self, index_to_weight):

        new_indices = self.close_unused_open_files(index_to_weight)

        var_descriptors = self.variable_descriptors
        target_var_images = dict()
        for var_name, var_attributes in var_descriptors.items():
            source_var_images = [None] * len(new_indices)
            source_weights = [None] * len(new_indices)
            var_image_index = 0
            for i in new_indices:
                file, time_index = self._get_file_and_time_index(i)
                variable = self._dataset_cache.get_dataset(file).variables[var_attributes.get('source_name', var_name)]
                if len(variable.shape) == 3:
                    var_image = variable[time_index, :, :]
                elif len(variable.shape) == 2:
                    var_image = variable[:, :]
                else:
                    raise TypeError("unexpected shape for variable '%s'" % var_name)
                var_image = self.transform_source_image(var_image)

                            # Spatial resampling
                var_image = gtr.resample_2d(var_image,
                                        self.cube_config.grid_width,
                                        self.cube_config.grid_height,
                                        ds_method=gtr.__dict__['DS_' + var_attributes.get('ds_method', 'MEAN')],
                                        us_method=gtr.__dict__['US_' + var_attributes.get('us_method', 'NEAREST')],
                                        fill_value=var_attributes.get('fill_value', numpy.nan))

                if var_image.shape[1]/var_image.shape[0] != 2.0:
                    print("Warning: wrong size ratio of image in '%s'. Expected 2, got %f" % (file, var_image.shape[1]/var_image.shape[0]))
                source_var_images[var_image_index] = var_image
                source_weights[var_image_index] = index_to_weight[i]
                var_image_index += 1
            if len(new_indices) > 1:
                # Temporal aggregation
                var_image = aggregate_images(source_var_images, weights=source_weights)
            else:
                # Temporal aggregation not required
                var_image = source_var_images[0]

            target_var_images[var_name] = var_image

        return target_var_images
    # Special in this implementation:
    #  - aggregate_image not called, see Hans' memory problem,
    #  - performs it's own temporal aggregation which is wrong because it doesn't consider masked values
    # def compute_variable_images_from_sources(self, index_to_weight):
    #
    #     # close all datasets that wont be used anymore
    #     new_indices = set(index_to_weight.keys())
    #     if self.old_indices:
    #         unused_indices = self.old_indices - new_indices
    #         for i in unused_indices:
    #             file, _ = self._get_file_and_time_index(i)
    #             self.dataset_cache.close_dataset(file)
    #     self.old_indices = new_indices
    #
    #     if len(new_indices) == 1:
    #         i = next(iter(new_indices))
    #         file, time_index = self._get_file_and_time_index(i)
    #         var_image = 1.0 * self.dataset_cache.get_dataset(file).variables[VAR_NAME][time_index, :, :].astype(numpy.float32)
    #     else:
    #         weight_sum = 0.0
    #         snow_area_extent_sum = numpy.zeros((18000, 36000), dtype=numpy.float32)
    #         for i in new_indices:
    #             weight = index_to_weight[i]
    #             file, time_index = self._get_file_and_time_index(i)
    #             var_image = self.dataset_cache.get_dataset(file).variables[VAR_NAME]
    #             print(i,weight,var_image.shape, index_to_weight, var_image.__sizeof__())
    #             snow_area_extent_sum += weight * var_image[time_index, :, :]
    #             weight_sum += weight
    #         var_image = snow_area_extent_sum / weight_sum
    #
    #     var_image = gtr.resample_2d(var_image, self.cube_config.grid_width, self.cube_config.grid_height,
    #                                 us_method=gtr.US_NEAREST, fill_value=FILL_VALUE)
        return {VAR_NAME: var_image}

    def compute_source_time_ranges(self):
        source_time_ranges = []
        file_names = os.listdir(self.dir_path)
        for file_name in file_names:
            file = os.path.join(self.dir_path, file_name)
            dataset = self.dataset_cache.get_dataset(file)
            time = dataset.variables['time']
            # dates = netCDF4.num2date(time[:], time.units, calendar=time.calendar)
            dates = netCDF4.num2date(time[:] - 14, 'days since 1582-10-15 00:00', calendar='gregorian')
            self.dataset_cache.close_dataset(file)
            n = len(dates)
            for i in range(n):
                t1 = dates[i]
                if i < n - 1:
                    t2 = dates[i + 1]
                else:
                    t2 = t1 + timedelta(days=31)  # assuming it's December
                source_time_ranges.append((t1, t2, file, i))
        return sorted(source_time_ranges, key=lambda item: item[0])
