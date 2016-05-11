Single variable image providers
-------------------------------

* AirTemperatureProvider
* BurntAreaProvider
* CEmissionsProvider
* GlobVapourProvider
* OzoneProvider
* PrecipProvider
* SnowAreaExtentProvider
* SnowWaterEquivalentProvider
* SoilMoistureProvider


Multiple variable image providers
---------------------------------
* AlbedoProvider (2)
* AerosolsProvider (5)


Use a _day2date function
------------------------
* AlbedoProvider
* AerosolsProvider

Random notes
------------
* Ozone is the only product that has no time dim!
* Albedo and Aerosol products have a time dim of size one!
* AerosolsProvider uses silly variable names (images_<wl>)
* All resamplings are nearest! Why???



Other refactorings
------------------
(1) rename Provider.get_spatial_coverage -> get_provided_image_size

(2) A common access pattern is:

        self.dataset_cache.get_dataset(file).variables[VAR_NAME][..., :, :]

    Given that Ozone has no time dim and the Albedo and Aerosol time dim is one, we might
    harmonise the code using explicit slice objects:
    * No time dim:  i=(Ellipsis, slice(None), slice(None))
    * Time is one:  i=(0, slice(None), slice(None))
    * Time is any:  i=(time_index, slice(None), slice(None))

        self.dataset_cache.get_dataset(file).variables[VAR_NAME][i]
