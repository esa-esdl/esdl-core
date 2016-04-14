from __future__ import division
import numpy as np


class Raster:
    def __init__(self, w, h, data, gap_count=-1):
        if w <= 0 or h <= 0 or data.size != w * h:
            raise ValueError()
        self.w = w
        self.h = h
        self.size = w * h
        self.data = data
        if gap_count >= 0:
            self.gap_count = gap_count
        else:
            self.gap_count = np.count_nonzero(np.isnan(data))

    def is_singular(self):
        return self.w == 1 and self.h == 1

    def is_free_of_gaps(self):
        return self.gap_count == 0

    def is_full_of_gaps(self):
        return self.gap_count == self.size

    def clone(self):
        return Raster(self.w, self.h, np.copy(self.data), self.gap_count)
