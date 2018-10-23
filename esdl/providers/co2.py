import os
from datetime import datetime

import netCDF4
import numpy

from esdl.cube_provider import CateCubeSourceProvider


class CH4Provider(CateCubeSourceProvider):
    def __init__(self, cube_config, name='ozone', dir=None, resampling_order=None):
        super().__init__(cube_config, name, dir, resampling_order)
        self.old_indices = None

    @property
    def variable_descriptors(self):
        return {
            'ozone': {
                'source_name': 'xco2',
                'data_type': numpy.float64,
                'fill_value': 1e+20,
                'units': '1',
                'cell_methods': 'time: mean',
                'long_name': 'column-average dry-air mole fraction of atmospheric carbon dioxide',
                'standard_name': 'dry_atmosphere_mole_fraction_of_carbon_dioxide',
                'references': 'Laeng, A., et al. "The ozone climate change initiative: Comparison of four '
                              'Level-2 processors for the Michelson Interferometer for Passive Atmospheric '
                              'Sounding (MIPAS)." Remote Sensing of Environment 162 (2015): 316-343.',
                'comment': 'Satellite retrieved column-average dry-air mole fraction of atmospheric carbon dioxide (XCO2)',
                'url': 'http://www.esa-ghg-cci.org/',
                'project_name' : 'Ozone CCI',
                'associated_files': 'obs4mips_co2_crdp3_v100.sav',
                'contact': 'maximilian.reuter@iup.physik.uni-bremen.de',
                'Conventions': 'CF-1.6',
                'creation_date': '20160303T111125Z',
                'data_structure': 'grid',
                'frequency': 'mon',
                'institute_id': 'IUP',
                'institution': 'Institute of Environmental Physics, University of Bremen',
                'mip_specs': 'CMIP5',
                'product': 'observations',
                'project_id': 'obs4MIPs',
                'realm': 'atmos',
                'source': 'ESA GHG CCI XCO2 CRDP3',
                'source_id': 'XCO2_CRDP3',
                'source_type': 'satellite_retrieval',
                'tracking_id': '60972082-05c2-4a04-947a-99042c642c68',
            }
        }

    def compute_source_time_ranges(self):
        from datetime import date, timedelta
        source_time_ranges = list()
        for root, sub_dirs, files in os.walk(self.dir_path):
            for file_name in files:
                if '.nc' in file_name:
                    f = os.path.join(root, file_name)
                    ds = netCDF4.Dataset(f)
                    base_date = date(1990, 1, 1)
                    t1 = timedelta(numpy.min(ds.variables['time']))
                    t2 = timedelta(numpy.max(ds.variables['time']))

                    t1 = base_date + t1
                    t2 = base_date + t2

                    t1 = datetime(t1.year, t1.month, t1.day)
                    t2 = datetime(t2.year, t2.month, t2.day)

                    ds.close()

                    source_time_ranges.append((t1, t2, f, 0))

        return sorted(source_time_ranges, key=lambda item: item[0])

    def transform_source_image(self, source_image):
        """
        Transforms the source image, here by flipping and then shifting horizontally.
        :param source_image: 2D image
        :return: source_image
        """
        return source_image
