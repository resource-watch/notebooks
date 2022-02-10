## Layer v4 definitions 

All functions definitions are in [this notebook](./RW-LM4_migration_functions.ipynb)

All layer types in the v4 specification are defined based on the layerConfig property of a layer
object.  The layerConfig object is a dictionary with the following keys:

* source: dictionary that contains the source of the data for the layer. This dictionary contains the next
          set of keys:
  * type: Required the type of the layer.  Valid values are: 'raster', 'vector', 'geojson'
    * tiles: Required list of urls to the tiles that make up the layer
    * provider: Optional object that describes the data provider specific needs.  This dictionary contains the next
          required set of keys plus a variable set depending on the data provider type:
      * 'type': the type of the data provider.  Valid values are: 'carto', 'wms', 'feature-service', 'gee'

* render: dictionary that contains the rendering information for the layer. it follows [Mapbox style spec syntax](https://www.mapbox.com/mapbox-gl-js/style-spec/)

note:

* The gee layer styles provider is a custom internal tyler so in order to render the tiles in the server you must keep  the gee keys `[body, assetId, isImageCollection, position]`

* Timeline layers does also contain `[timelineLabel, order, timeline]`