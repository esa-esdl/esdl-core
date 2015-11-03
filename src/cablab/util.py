"""
Various utility constants, functions and classes.
Developer note: make sure this module does not import any other cablab module!
"""

import os
import gzip

import netCDF4


def temporal_weight(a1, a2, b1, b2):
    """
    Compute a weight (0.0 to 1.0) from the overlap of time range a1...a2 with time range b1...b2.
    If there is no overlap at all, return 0.
    """
    a1_in_b_range = b1 <= a1 <= b2
    a2_in_b_range = b1 <= a2 <= b2
    if a1_in_b_range and a2_in_b_range:
        return 1.0
    if a1_in_b_range:
        return (b2 - a1) / (b2 - b1)
    if a2_in_b_range:
        return (a2 - b1) / (b2 - b1)
    b1_in_a_range = a1 <= b1 <= a2
    b2_in_a_range = a1 <= b2 <= a2
    if b1_in_a_range and b2_in_a_range:
        return 1.0
    return 0.0


class NetCDFDatasetCache:
    def __init__(self, name, cache_base_dir=None):
        if cache_base_dir is None:
            cache_base_dir = os.path.join(os.path.join(os.path.expanduser("~"), '.cablab'), 'cache')
        self.cache_dir = os.path.join(cache_base_dir, name)
        self.file_to_dataset = dict()

    def get_dataset(self, file):
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

    def close_dataset(self, file):
        if file not in self.file_to_dataset:
            return
        dataset = self.file_to_dataset[file]
        dataset.close()
        del self.file_to_dataset[file]

    def close_all_datasets(self):
        files = list(self.file_to_dataset.keys())
        for file in files:
            self.close_dataset(file)

    def _get_unpacked_file(self, file):
        root, _ = os.path.splitext(file)
        filename = os.path.basename(root)
        real_file = os.path.join(self.cache_dir, filename)
        if not os.path.exists(real_file):
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir, exist_ok=True)
            with gzip.open(file, 'rb') as istream:
                with open(real_file, 'wb') as ostream:
                    ostream.write(istream.read())
        return real_file
