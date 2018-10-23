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
        return{
            "AAOD550_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "units": "1",
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "absorbing AOD",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            },
            "AOD1600_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "units": "1",
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "aerosol optical thickness at 1600 nm",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            },
            "AOD550_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "aerosol optical thickness at 550 nm",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "units": "1",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            },
            "AOD670_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "aerosol optical thickness at 670 nm",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "units": "1",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            },
            "AOD870_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "aerosol optical thickness at 870 nm",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "units": "1",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            },
            "D_AOD550_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "non-spherical dust AOD",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "units": "1",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            },
            "FM_AOD550_mean": {
                "source_name": "AAOD550_mean",
                "data_type": numpy.float32,
                "fill_value": -999.0,
                "projection": "equirectangular",
                "product_version": "4.21",
                "geospatial_lat_units": "degrees_north",
                "long_name": "fine mode AOD",
                "standard_name": "atmosphere_optical_thickness_due_to_ambient_aerosol",
                "geospatial_lon_units": "degrees_east",
                "references": "http:\/\/www.esa-aerosol-cci.org",
                "inputfilelist": "ATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1 \nATS_TOA_1PUUPA20020724_141127_000065272008_00024_02082_5805.N1",
                "keywords": "satellite,observation,atmosphere",
                "Conventions": "CF-1.6",
                "id": "20020724141127-ESACCI-L3C_AEROSOL-AER_PRODUCTS-AATSR_ENVISAT-SU_DAILY-v4.21.nc",
                "naming_authority": "uk.ac.su.aatsraerosol",
                "geospatial_lat_max": "90.0",
                "title": "AARDVARC CCI aerosol product level 3",
                "standard_name_vocabulary": "NetCDF Climate and Forecast (CF) Metadata Convention version 18",
                "lon": 360,
                "coordinates": "latitude longitude",
                "platform": "ENVISAT",
                "units": "1",
                "sensor": "AATSR",
                "creator_email": "p.r.j.north@swansea.ac.uk, a.heckel@swansea.ac.uk",
                "geospatial_lat_min": "-90.0",
                "geospatial_lat_resolution": "1.0",
                "time_coverage_start": "20020724T143513Z",
                "creator_url": "http:\/\/www.swan.ac.uk\/staff\/academic\/environmentsociety\/geography\/northpeter\/",
                "lat": 180,
                "keywords_vocabulary": "NASA Global Change Master Directory (GCMD) Science Keywords",
                "geospatial_lon_max": "180.0",
                "geospatial_lon_min": "-180.0",
                "geospatial_lon_resolution": "1.0",
                "license": "ESA CCI Data Policy: free and open access",
                "creator_name": "Swansea University",
                "time_coverage_end": "20020724T233825Z",
                "summary": "This dataset contains the level-3 daily mean aerosol properties products from AATSR satellite observations. Data are processed by Swansea algorithm",
                "project": "Climate Change Initiative - European Space Agency",
                "cdm_data_type": "grid",
                "source": "ATS_TOA_1P, V6.05",
                "tracking_id": "a63f9cd2-1fed-4f9a-82fd-91f1c1b966b2",
                "time": "1",
                "date_created": "20151022T231808Z",
                "resolution": "1x1 degrees",
                "history": "Level 3 product from Swansea algorithm"
            }
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
