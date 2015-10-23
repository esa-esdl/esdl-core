import netCDF4

ds = netCDF4.Dataset("C:\\Users\\Norman\\Desktop\\BurntArea\\BurntArea.GFED4.2008.nc", 'r')

ba_input = ds.variables['BurntArea']
print(ba_input.units)

from test.sandbox.cubeio import CLDataset
from datetime import datetime, timedelta

times_count = 12
dates = [datetime(2008, 1, 1) + i * timedelta(days=8) for i in range(times_count)]
print(dates)

from skimage.measure import block_reduce
import numpy

output_file = 'cablab-burnt_area-2008-comb.nc'
ds = CLDataset.create(output_file, 'First test', 720, 360, time_values=CLDataset.date2num(dates))
ba_output = ds.create_variable('burnt_area', ba_input.dtype, ba_input.units, ba_input.long_name,
                               fill_value=ba_input.missing_value)
ba_output[:, :, :, :] = block_reduce(ba_input, block_size=(1, 2, 2), func=numpy.mean, cval=0)
ds.close()

ds = CLDataset.read(output_file)
print(ds.dataset)
