
Refactorings in this branch
---------------------------

SKIP (1) rename Provider.get_spatial_coverage() -> get_provided_image_size()

DONE (2) A common access pattern is:

        self.dataset_cache.get_dataset(file).variables[VAR_NAME][..., :, :]

    Given that Ozone has no time dim and the Albedo and Aerosol time dim is one, we might
    harmonise the code using explicit slice objects:
    * No time dim:  i=(Ellipsis, slice(None), slice(None))
    * Time is one:  i=(0, slice(None), slice(None))
    * Time is any:  i=(time_index, slice(None), slice(None))

        self.dataset_cache.get_dataset(file).variables[VAR_NAME][i]

(3) a) move aggregation code from cablab.util to gridtools
    b) rename temporal_weight() -> range_overlap_ratio()
    c) rename aggregate_images() -> aggregate_2d()

(4) a) move DatasetCache, NetCDFDatasetCache to ds_cache.py
    b) rename close_dataset() -> close_file
    c) rename close_all_datasets() -> close_all_files
    d) introduce abstract DatasetCache.close_dataset(dataset), override in NetCDFDatasetCache

DONE (5) a) rename get_source_time_ranges() -> compute_source_time_ranges()
    b) store result of compute_source_time_ranges in self._source_time_ranges
    c) introduce property source_time_ranges

DONE (6) a) rename cube_cli.py -> cube_gen.py
    b) move Provider stuff from cube.py to cube_gen.py
    c) rename cube.py -> cube_access.py, merge xarray stuff from branch 'issue_29'
    d) new cube_config.py
    e) move CubeConfig into cube_config.py
    Resulting dependencies:
        cube_access: cube_gen, cube_config
        cube_gen: cube_config
        any provider: cube_gen, cube_config

(7) It seems that util.Config is only used by cube_gen and provider tests!
    If so, move to cube_config.py

DONE (8) Provider interface:
    rename get_spatial_coverage(self) -> spatial_coverage, make abstract property
    rename get_variable_descriptors(self) -> variable_descriptors, make abstract property

DONE (9) must address netCDF variable renamings. Introduce var attribute 'source_name'

DONE (10) Replace special compute_variable_images_from_sources() impl. by generic one in base class.


(11) Review all variable_descriptors() impls (Fabian and Gunnar):
     * check: target variable names, use CF names or just CF-compliant names?
     * check: why are the different 'fill_value' values? we should use a common one for each data type, e.g. np.nan
     * check: find correct 'standard_name' for each variable, current ones are mostly wrong
     * check: 'long_name' name is often wrong or confusing,
              e.g. 'level 3b fractional snow cover (%) aggregated monthly' when our period is 8 days.
              All lower case?
     * check: possibly add 'comment' or 'description' or 'history' and tell where data comes from

(12) Generated netCDF files and variables still lack important CF variables:
     * 'Conventions'
     * 'history'
     * 'coordinates'
     * 'lat_bnd', 'lon_bnds' + their 'standard_name' values, see #20, #30