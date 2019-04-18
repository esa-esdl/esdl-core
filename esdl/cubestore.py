# The MIT License (MIT)
# Copyright (c) 2018 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import json
import os
from typing import Any

import s3fs
import xarray as xr
import zarr


class CubesStore:

    def __init__(self):
        client_kwargs = {'endpoint_url': "https://obs.eu-de.otc.t-systems.com", 'region_name': "eu-de"}
        s3 = s3fs.S3FileSystem(anon=True, client_kwargs=client_kwargs)

        with s3.open('obs-esdc-configs/datacube_paths.json') as json_data_file:
            self._cube_config = json.load(json_data_file)
        self._dataset_cache = dict()

    def _repr_html_(self):
        html = ""
        for name, props in self._cube_config.items():
            description = props["description"]
            html += f"<tr><td>{name}</td><td>{description}</td></tr>"

        return "<table>" + html + "</table>"

    def __getattr__(self, name: str) -> Any:
        if name in self._cube_config:
            if name in self._dataset_cache:
                return self._dataset_cache[name]
            else:

                dataset_descriptor = self._cube_config[name]
                fs_type = dataset_descriptor.get("FileSystem", "local")
                path = dataset_descriptor.get('Path')

                if not path:
                    print(f"Missing 'path' entry in dataset descriptor")
                if fs_type == 'obs':
                    data_format = dataset_descriptor.get('Format', 'zarr')
                    if data_format != 'zarr':
                        print(f"Invalid format={data_format!r} in dataset descriptor ")
                    client_kwargs = {}
                    if 'Endpoint' in dataset_descriptor:
                        client_kwargs['endpoint_url'] = dataset_descriptor['Endpoint']
                    if 'Region' in dataset_descriptor:
                        client_kwargs['region_name'] = dataset_descriptor['Region']
                    s3 = s3fs.S3FileSystem(anon=True, client_kwargs=client_kwargs)
                    store = s3fs.S3Map(root=path, s3=s3, check=False)
                    cached_store = zarr.LRUStoreCache(store, max_size=2 ** 28)
                    ds = xr.open_zarr(cached_store)
                elif fs_type == 'local':
                    if not os.path.isabs(path):
                        path = os.path.join(self.base_dir, path)
                    data_format = dataset_descriptor.get('Format', 'nc')
                    if data_format == 'nc':
                        ds = xr.open_dataset(path)
                    elif data_format == 'zarr':
                        ds = xr.open_zarr(path)
                    else:
                        print(f"Invalid format={data_format!r} in dataset descriptor")
                self._dataset_cache[name] = ds
            return ds
        return super().__getattribute__(name)


store = CubesStore()
