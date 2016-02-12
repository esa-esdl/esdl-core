
User Story 1: Calculating recurrence scores in time-series
----------------------------------------------------------

.. code:: julia

    using CABLAB
    using ImageMagick #Necessary for inline Map plots

To start, we define the path to the ESDC, choose some variables, and read a
geographical region into memory.

.. code:: Julia

    c             = Cube("/path/to/datacube/")
    vars          = ["BHR_VIS","BurntArea","DHR_VIS","Emission","SoilMoisture","t2m"];
    cdata         = getCubeData(c,latitude=(35,45), longitude=(-10,0),variable=vars);
    cdata         = joinVars(cdata);

Here starts the actual processing step. Note that each function call has
the result of the previous call as its input argument. The following
processing steps are applied:

-  gap-filling with information from the mean seasonal cycle
-  calculating anomalies, i.e. subtract the mean seasonal cycle
-  normalize the different variables to unit variance
-  calculate recurrence scores to detect outliers

.. code:: julia

    cube_filled     = gapFillMSC(cdata,46);
    cube_anomalies  = removeMSC!(cube_filled,46);
    cube_normalized = normalize(cube_anomalies);
    scores          = recurrences!(cube_normalized,500.0,5,zeros(Float32,506,506));

The results can be visualized by interactive time-series plots of the different
variables, anomalies, and recurrence scores. In this example, three extreme events are detected.

.. code:: julia

    plotTS(cube_filled)


.. image:: story1_files/story1_7_6.svg
    :width: 40%
    :align: center
    :alt:



.. raw:: html

    <div id="pwid14819"><script>new Patchwork.Node("pwid14819", {"t":"svg","p":{"viewBox":"0 0 141.4213562373095 100.0","stroke-width":"0.3","width":"141.4213562373095mm","font-size":"3.88","height":"100.0mm","stroke":"none","fill":"#000000"},"c":[{"t":"g","p":{"class":"plotroot xscalable yscalable"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide xlabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"class":"guide colorkey"},"c":[{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#4C404B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"stroke":"#000000"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#362A35","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"g","p":{"clip-path":"url(#clippath-1)"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"opacity":1.0,"fill-opacity":0.0,"fill":"#000000","stroke":"#000000","class":"guide background"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide ygridlines xfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide xgridlines yfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"class":"plotpanel"},"c":[{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_t2m","stroke":"#FF6765"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_BHR_VIS","stroke":"#BEA9FF"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_SoilMoisture","stroke":"#00B78D"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_BurntArea","stroke":"#FF6DAE"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_DHR_VIS","stroke":"#D4CA3A"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_Emission","stroke":"#00BFFF"},"n":"svg"}],"n":"svg"}],"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide ylabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"defs","c":[{"t":"clipPath","p":{"id":"clippath-1"},"c":[{"t":"path","p":{"d":"M24.92,5 L 117.45 5 117.45 80.72 24.92 80.72"},"n":"svg"}],"n":"svg"}],"n":"svg"}],"n":"svg"});</script></div>




.. code:: julia

    plotTS(cube_anomalies)



.. image:: story1_files/story1_8_6.svg
    :width: 40%
    :align: center
    :alt:





.. raw:: html

    <div id="pwid14821"><script>new Patchwork.Node("pwid14821", {"t":"svg","p":{"viewBox":"0 0 141.4213562373095 100.0","stroke-width":"0.3","width":"141.4213562373095mm","font-size":"3.88","height":"100.0mm","stroke":"none","fill":"#000000"},"c":[{"t":"g","p":{"class":"plotroot xscalable yscalable"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide xlabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"class":"guide colorkey"},"c":[{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#4C404B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"stroke":"#000000"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#362A35","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"g","p":{"clip-path":"url(#clippath-1)"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"opacity":1.0,"fill-opacity":0.0,"fill":"#000000","stroke":"#000000","class":"guide background"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide ygridlines xfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide xgridlines yfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"class":"plotpanel"},"c":[{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_t2m","stroke":"#FF6765"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_BHR_VIS","stroke":"#BEA9FF"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_SoilMoisture","stroke":"#00B78D"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_BurntArea","stroke":"#FF6DAE"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_DHR_VIS","stroke":"#D4CA3A"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_Emission","stroke":"#00BFFF"},"n":"svg"}],"n":"svg"}],"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide ylabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"defs","c":[{"t":"clipPath","p":{"id":"clippath-1"},"c":[{"t":"path","p":{"d":"M23.69,5 L 117.45 5 117.45 80.72 23.69 80.72"},"n":"svg"}],"n":"svg"}],"n":"svg"}],"n":"svg"});</script></div>






.. code:: julia

    plotTS(cube_normalized)





.. image:: story1_files/story1_9_6.svg
    :width: 40%
    :align: center
    :alt:




.. raw:: html

    <div id="pwid14823"><script>new Patchwork.Node("pwid14823", {"t":"svg","p":{"viewBox":"0 0 141.4213562373095 100.0","stroke-width":"0.3","width":"141.4213562373095mm","font-size":"3.88","height":"100.0mm","stroke":"none","fill":"#000000"},"c":[{"t":"g","p":{"class":"plotroot xscalable yscalable"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide xlabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"class":"guide colorkey"},"c":[{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#4C404B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"stroke":"#000000"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#362A35","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"g","p":{"clip-path":"url(#clippath-1)"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"opacity":1.0,"fill-opacity":0.0,"fill":"#000000","stroke":"#000000","class":"guide background"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide ygridlines xfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide xgridlines yfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"class":"plotpanel"},"c":[{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_t2m","stroke":"#FF6765"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_BHR_VIS","stroke":"#BEA9FF"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_SoilMoisture","stroke":"#00B78D"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_BurntArea","stroke":"#FF6DAE"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_DHR_VIS","stroke":"#D4CA3A"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry color_Emission","stroke":"#00BFFF"},"n":"svg"}],"n":"svg"}],"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide ylabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"defs","c":[{"t":"clipPath","p":{"id":"clippath-1"},"c":[{"t":"path","p":{"d":"M16.15,5 L 117.45 5 117.45 80.72 16.15 80.72"},"n":"svg"}],"n":"svg"}],"n":"svg"}],"n":"svg"});</script></div>





.. code:: julia

    scores          = recurrences!(cube_normalized,7.0,5,zeros(Float32,506,506));
    plotTS(scores)


.. image:: story1_files/story1_10_0.svg
    :width: 40%
    :align: center
    :alt:

.. raw:: html

    <div id="pwid14825"><script>new Patchwork.Node("pwid14825", {"t":"svg","p":{"viewBox":"0 0 141.4213562373095 100.0","stroke-width":"0.3","width":"141.4213562373095mm","font-size":"3.88","height":"100.0mm","stroke":"none","fill":"#000000"},"c":[{"t":"g","p":{"class":"plotroot xscalable yscalable"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide xlabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"clip-path":"url(#clippath-1)"},"c":[{"t":"g","p":{"stroke-opacity":0.0,"opacity":1.0,"fill-opacity":0.0,"fill":"#000000","stroke":"#000000","class":"guide background"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide ygridlines xfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.2,"stroke-dasharray":"0.5,0.5","class":"guide xgridlines yfixed","stroke":"#D0D0E0"},"n":"svg"},{"t":"g","p":{"class":"plotpanel"},"c":[{"t":"g","p":{"stroke-opacity":1.0,"stroke-width":0.3,"fill-opacity":0.0,"stroke-dasharray":"none","fill":"#000000","class":"geometry","stroke":"#00BFFF"},"n":"svg"}],"n":"svg"}],"n":"svg"},{"t":"g","p":{"fill-opacity":1.0,"font-size":2.822222222222222,"font-family":"'PT Sans Caption','Helvetica Neue','Helvetica',sans-serif","class":"guide ylabels","fill":"#6C606B"},"n":"svg"},{"t":"g","p":{"stroke-opacity":0.0,"fill-opacity":1.0,"font-size":3.880555555555555,"font-family":"'PT Sans','Helvetica Neue','Helvetica',sans-serif","fill":"#564A55","stroke":"#000000"},"n":"svg"}],"n":"svg"},{"t":"defs","c":[{"t":"clipPath","p":{"id":"clippath-1"},"c":[{"t":"path","p":{"d":"M17.83,5 L 136.42 5 136.42 80.72 17.83 80.72"},"n":"svg"}],"n":"svg"}],"n":"svg"}],"n":"svg"});</script></div>
