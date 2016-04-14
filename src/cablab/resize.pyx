#!python
#cython: language_level=3, boundscheck=False, cdivision=True

# http://stackoverflow.com/questions/7075082/what-is-future-in-python-used-for-and-how-when-to-use-it-and-how-it-works
from __future__ import division
from cablab.raster import Raster
from skimage.transform import resize as skimage_resize
import numpy as np
cimport numpy as np
from libc.math cimport isnan, NAN
from libc.stdio cimport printf

DTYPE_INT = np.int64
DTYPE_DBL = np.float64
ctypedef np.int64_t DTYPE_INT_t
ctypedef np.float_t DTYPE_DBL_t
ctypedef Py_ssize_t SIZE_t

cdef DTYPE_DBL_t EPS = 1e-10


def upsample(raster, SIZE_t dstW, SIZE_t dstH, order):
    """
     Performs a linear interpolation.

     @param raster Source raster
     @param dstW   Target raster width
     @param dstH   Target raster height
     @return Upsampled (interpolated) target raster.
    """

    cdef np.ndarray[DTYPE_DBL_t, ndim=2] interpolated = skimage_resize(raster.data, (dstH, dstW), order)

    return Raster(dstW, dstH, interpolated)


def downsample(raster, SIZE_t dstW, SIZE_t dstH):
    """
     * Performs an area-weighed average aggregation.
     *
     * @param raster Source raster
     * @param dstW   Target raster width
     * @param dstH   Target raster height
     * @return Downsampled (aggregated) target raster.
    """
    cdef SIZE_t srcW = raster.w
    cdef SIZE_t srcH = raster.h
    if srcW == dstW and srcH == dstH:
        return raster

    if dstW > srcW or dstH > srcH:
        raise ValueError("Invalid target size")

    cdef DTYPE_DBL_t sx = <DTYPE_DBL_t>srcW / <DTYPE_DBL_t>dstW
    cdef DTYPE_DBL_t sy = <DTYPE_DBL_t>srcH / <DTYPE_DBL_t>dstH
    cdef np.ndarray[DTYPE_DBL_t, ndim=2] aggregated = np.zeros((dstH, dstW), dtype=DTYPE_DBL)
    cdef np.ndarray[DTYPE_DBL_t, ndim=2] data = raster.data
    cdef SIZE_t gapCount = 0
    cdef SIZE_t dstX, dstY, srcX, srcY, srcX0, srcX1, srcY0, srcY1
    cdef DTYPE_DBL_t srcXF0, srcXF1, srcYF0, srcYF1
    cdef DTYPE_DBL_t wx0, wx1, wy0, wy1, wx, wy, vSum, wSum, v, w
    if np.ma.is_masked(data):
        aggregated = np.ma.empty((dstH, dstW), dtype=DTYPE_DBL)
        data = np.ma.filled(data, np.nan)
    for dstY in range(dstH):
        srcYF0 = sy * dstY
        srcYF1 = srcYF0 + sy
        srcY0 = <SIZE_t>srcYF0
        srcY1 = <SIZE_t>srcYF1
        wy0 = 1.0 - (srcYF0 - srcY0)
        wy1 = srcYF1 - srcY1
        if wy1 < EPS:
            wy1 = 1.0
            if srcY1 > srcY0:
                srcY1 -= 1
        for dstX in range(dstW):
            srcXF0 = sx * dstX
            srcXF1 = srcXF0 + sx
            srcX0 = <SIZE_t>srcXF0

            srcX1 = <SIZE_t>srcXF1
            wx0 = 1.0 - (srcXF0 - srcX0)
            wx1 = srcXF1 - srcX1
            if wx1 < EPS:
                wx1 = 1.0
                if srcX1 > srcX0:
                    srcX1 -= 1
            vSum = 0.0
            wSum = 0.0
            for srcY in range(srcY0, srcY1 + 1):
                wy = wy0 if (srcY == srcY0) else wy1 if (srcY == srcY1) else 1.0
                for srcX in range(srcX0, srcX1 + 1):
                    wx = wx0 if (srcX == srcX0) else wx1 if (srcX == srcX1) else 1.0
                    v = data[srcY, srcX]
                    if not isnan(v):
                        w = wx * wy
                        vSum += w * v
                        wSum += w
            if isnan(vSum) or wSum < EPS:
                aggregated[dstY, dstX] = NAN
                gapCount += 1
            else:
                aggregated[dstY, dstX] = vSum / wSum
    return Raster(dstW, dstH, aggregated, gapCount)


def resize(SIZE_t w, SIZE_t h, np.ndarray[DTYPE_DBL_t, ndim=2] data, SIZE_t wNew, SIZE_t hNew, order=1):
    """
     * Performs raster resizing which may imply interpolation while upsampling or aggregation while downsampling.
     *
     * @param w     Source raster width
     * @param h     Source raster height
     * @param data  Source raster
     * @param wNew  Target raster width
     * @param hNew  Target raster height
     * @return Target raster
     *
     * @author Norman Fomferra
    """

    if wNew < w and hNew < h:
        downsampled = downsample(Raster(w, h, data), wNew, hNew)
        return downsampled.data
    elif wNew < w:
        downsampled = downsample(Raster(w, h, data), wNew, h)
        if hNew > h:
            upsampled = upsample(downsampled, wNew, hNew, order)
            return upsampled.data
        else:
            return downsampled.data
    elif hNew < h:
        downsampled = downsample(Raster(w, h, data), w, hNew)
        if wNew > w:
            upsampled = upsample(downsampled, wNew, hNew, order)
            return upsampled.data
        else:
            return downsampled.data
    elif wNew > w or hNew > h:
        upsampled = upsample(Raster(w, h, data), wNew, hNew, order)
        return upsampled.data
    return data


