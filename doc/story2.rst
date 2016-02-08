
Calculating temporal variance with and without seasonal cycle
=============================================================

.. code:: python

    using CABLAB
    using ImageMagick

A Cube is defined via its path and some a single variable is read into
memory.

.. code:: python

    c             = Cube("/Volumes/BGI/scratch/DataCube/v1/brockmann-consult.de/datacube/")
    cdata         = getCubeData(c,variable="SoilMoisture",latitude=(35,65), longitude=(-15,40));

Here we demonstrate how to add a user-defined function to use the DAT's
capabilities. First we define the function that has the signature *xin*
(input data), *xout* (output data), *maskin* (input mask), *maskout*
(output mask). In this case it simply cacluates the variance of a time
series. Then we call the @registerDATFunction macro, which creates a
wrapper around the function and makes it applicable to a Cube object.

.. code:: python

    function varianceTime{T}(xin::AbstractVector{T},xout::AbstractArray{T,0},maskin::AbstractVector,maskout::AbstractArray{UInt8,0})
      s=zero(T)
      s2=zero(T)*zero(T)
      n=0
      for i in eachindex(xin)
        if maskin[i]==CABLAB.VALID
          s+=xin[i]
          s2+=xin[i]*xin[i]
          n+=1
        end
      end
      if n>0
        m=s/n
        v=s2/n-m*m
        xout[1]=v
        maskout[1]=CABLAB.VALID
      else
        maskout[1]=CABLAB.MISSING
      end
    end

    @registerDATFunction varianceTime (TimeAxis,) ();

Here we call the function with our 3D data cube as its argument.

.. code:: python

    v1             = varianceTime(cdata);
    cube_anomalies = removeMSC!(cdata,46);
    v2             = varianceTime(cube_anomalies);

We get the spatial mean of the time variances

.. code:: python

    mv1=spatialMean(v1)
    mv2=spatialMean(v2)
    println("Mean variance with seasonal cycle: ", mv1)
    println("Mean variance without seasonal cycle: ", mv2)


.. parsed-literal::

    Mean variance with seasonal cycle: 0.0053804195
    Mean variance without seasonal cycle: 0.0038234952


Plot a map of the original soil mositure data:

.. code:: python

    plotMAP(cdata)



.. raw:: html





.. image:: story2_files/story2_11_1.png


And show the maps of variances:

.. code:: python

    plotMAP(v1,dmin=0.0f0,dmax=0.01f0)
    plotMAP(v2,dmin=0.0f0,dmax=0.01f0)



.. image:: story2_files/story2_13_0.png



.. image:: story2_files/story2_13_1.png
