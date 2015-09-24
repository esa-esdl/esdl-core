import netCDF4
import numpy


class CLDataset:
    TIME_UNITS = 'hours since 0001-01-01 00:00:00.0'
    TIME_CALENDAR = 'gregorian'

    def __init__(self, dataset):
        self.dataset = dataset

    @staticmethod
    def create(file, description, width, height, level_values=[1013.25], time_values=[]):
        # Note: format='NETCDF4_CLASSIC' is important, with format='NETCDF4' multi
        # files cannot be read with MFDataset!
        dataset = netCDF4.Dataset(file, 'w', format='NETCDF4_CLASSIC')

        # TODO: assert that global metadata fully complies to with CF-Conventions
        dataset.createDimension('time', len(time_values))
        dataset.createDimension('level', len(level_values))
        dataset.createDimension('lat', height)
        dataset.createDimension('lon', width)

        times = dataset.createVariable('time', 'f8', ('time',))
        times.units = CLDataset.TIME_UNITS
        times.calendar = CLDataset.TIME_CALENDAR
        times[:] = time_values

        levels = dataset.createVariable('level', 'f4', ('level',))
        levels.units = 'hPa'
        levels[:] = level_values

        latitudes = dataset.createVariable('latitude', 'f4', ('lat',))
        latitudes.units = 'degrees north'

        longitudes = dataset.createVariable('longitude', 'f4', ('lon',))
        longitudes.units = 'degrees east'

        # TODO: grid cell centers or lower-left corner?
        latitudes[:] = numpy.arange(-90, 90, 180 / height)
        longitudes[:] = numpy.arange(-180, 180, 360 / width)

        import time
        dataset.description = description
        dataset.source = 'CAB-LAB Software (module ' + __name__ + ')'
        dataset.history = 'Created ' + time.ctime(time.time())

        return CLDataset(dataset)

    @staticmethod
    def read(file, mode='r'):
        dataset = netCDF4.Dataset(file, mode)
        # TODO: ensure that dataset complies with CAB-LAB format specification
        return CLDataset(dataset)

    def create_variable(self, varname, datatype, units, description, fill_value=numpy.nan):
        variable = self.dataset.createVariable(varname,
                                               datatype,
                                               ("time", "level", "lat", "lon",),
                                               zlib=True,
                                               fill_value=fill_value)
        variable.units = units
        variable.description = description
        return variable

    def close(self):
        self.dataset.close()

    @staticmethod
    def date2num(dates):
        return netCDF4.date2num(dates,
                                units=CLDataset.TIME_UNITS,
                                calendar=CLDataset.TIME_CALENDAR)

    @staticmethod
    def num2date(times):
        return netCDF4.num2date(times,
                                units=CLDataset.TIME_UNITS,
                                calendar=CLDataset.TIME_CALENDAR)
