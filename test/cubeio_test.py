from cablab.cubeio import CLDataset
from datetime import datetime, timedelta


times_count = 10
dates = [datetime(2002, 6, 7) + i * timedelta(days=8) for i in range(times_count)]
print(dates)

ds = CLDataset.create('test.nc', 'First test', 720, 360, time_values=CLDataset.date2num(dates))
ds.create_variable('temperature', 'f4', 'K', 'Sea Surface Temperature')
ds.create_variable('ozone', 'f4', 'DU', 'Ozone Content')
ds.close()

ds = CLDataset.read('test.nc')
print(ds.dataset.dimensions)
print(ds.dataset.variables)
