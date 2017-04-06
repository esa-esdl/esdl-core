"""
ESDC DAT (Data Analytics Toolkit)
=================================

Note, the ESDC (Earth System Data Cube) is accessed via an 
`xarray.Dataset <http://xarray.pydata.org/en/stable/data-structures.html#dataset>_`, therefore the ``xarray.Dataset``
API is the primary DAT.

This module provides additional analytical utility functions which work for `xarray.Dataset`, `xarray.DataArray`, and
also Numpy arrays. 
"""


def corrcf(ds, var1=None, var2=None, dim='time'):
    '''
    Function calculating the correlation coefficient of two variables var1 and var2 in one xarray Dataset
    ds.
    :param ds: Xarray.Dataset
    :param var1: Variable 1
    :param var2: Variable 2, both have to be of identical size
    :param dim: dimension for aggregation, default is time. In the defualt case, the result is an image
    :return:
    '''

    if not isinstance(ds, xr.Dataset):
        print('Input object ', ds, ' is no xarray Dataset!')
        var1 = None

    if var1 is not None:
        if var2 is None:
            var2 = var1
        ds_tmean = ds.mean(skipna=True, dim=dim)
        ds_tstd = ds.std(skipna=True, dim=dim)
        covar_1 = (ds[var1] - ds_tmean[var1]) * (ds[var2] - ds_tmean[var2])
        res = covar_1.mean(dim='time', skipna=True) / (ds_tstd[var1] * ds_tstd[var2])
    else:
        res = None

    return res


def map_plot(ds, var=None, time=0, title_str='No title', projection='kav7', lon_0=0, resolution=None, **kwargs):
    '''
    Function plotting a projected map
    :param ds: xarray.Dataset
    :param var: variable to plot
    :param time: time step or dateime date to plot
    :param title_str: Title string
    :param projection: for Basemap
    :param lon_0: longitude 0 for central
    :param resolution: resolution for Basemap object
    :param kwargs: Any other **kwargs accepted by the pcolormap function of Basemap
    :return:
    '''

    if isinstance(time, int):
        res = ds[var].isel(time=time)
    elif time is None:
        res = ds[var]
        time = None
    else:
        try:
            res = ds[var].sel(time=time, method='nearest')
        except:
            print("Wrong date format, should be YYYY-MM-DD")
            raise

    lons, lats = np.meshgrid(np.array(res.lon), np.array(res.lat))
    ma_res = np.ma.array(res, mask=np.isnan(res))

    if "vmin" in kwargs:
        vmin = kwargs["vmin"]
    else:
        vmin = None
    if "vmax" in kwargs:
        vmax = kwargs["vmax"]
    else:
        vmax = None
    if title_str == "No title":
        title_str = var + ' ' + str(time)
    else:
        title_str = title_str + ' ' + str(res.time.values)[0:10]

    fig = plt.figure()
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
    m = Basemap(projection, lon_0, resolution)
    m.drawmapboundary(fill_color='0.3')
    ccmap = plt.cm.jet
    ccmap.set_bad("gray", 1.)
    im = m.pcolormesh(lons, lats, ma_res, shading='flat', cmap=ccmap, latlon=True, vmin=vmin, vmax=vmax, **kwargs)
    # lay-out
    m.drawparallels(np.arange(-90., 99., 30.))
    m.drawmeridians(np.arange(-180., 180., 60.))
    cb = m.colorbar(im, "bottom", size="5%", pad="2%")
    cb.set_label(ds[var].attrs['standard_name'] + ' (' + ds[var].attrs['units'] + ')')
    ax.set_title(title_str)
    # write to disk if specified
    if "plot_me" in kwargs:
        if kwargs["plot_me"] == True:
            plt.savefig(title_str[0:15] + '.png', dpi=600)

    fig.set_size_inches(8, 12)
    return fig, ax, m