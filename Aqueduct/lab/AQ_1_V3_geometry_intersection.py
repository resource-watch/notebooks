import requests
from tqdm import tqdm
import pandas as pd
import geopandas as gpd
import numpy as np
import os
import zipfile
from simpledbf import Dbf5
import fiona
import rtree
from collections import OrderedDict
from shapely.geometry import mapping, shape
import matplotlib.pyplot as plt
import shapely.wkb 
from shapely.ops import cascaded_union
from shapely.geometry import Polygon, Point, MultiPolygon


# Read cell5M geometries
cell5m = gpd.read_file('/Volumes/MacBook HD/data/aqueduct/data_source/spamdata/spam_cells/April_2013_IMPACT_Cell5M.shp')
cell5m.columns = [x.lower() for x in cell5m.columns]
cell5m.rename(columns={'cell5m_id_': 'cell5m', 'iso3code': 'iso'}, inplace=True)
cell5m.sort_values(['iso', 'cell5m'], inplace=True)

# convert the 'cell5m' column to object
cell5m['cell5m'] = cell5m['cell5m'].astype('int') 
#cell5m['cell5m'] = cell5m['cell5m'].astype('object') 

cell5m.drop(columns=['iso', 'alloc_key'], inplace=True)

# We use geopandas’s R-tree spatial index to find which basins lie within each grid cell
def rtree_intersect_fiona(gdf_path, grid, out_path):
    gdf = gpd.read_file(gdf_path)
    columns = list(gdf.columns)
    columns.append('percentage')
    columns.append('cell5m')

    properties = columns.copy()
    properties.remove('geometry')

    sindex = gdf.sindex

    with fiona.open(gdf_path, 'r') as layer1:
        # We copy schema and add the  new property for the new resulting shp
        crss=layer1.crs
        schema = layer1.schema.copy()
        for property in properties: 
            schema['properties'][property] = 'str:80'
    
        with fiona.open(out_path, 'w', 'ESRI Shapefile', schema, crs=crss) as layer2:
    
            # we iterate over the cells
            for n, cell in enumerate(tqdm(grid.geometry)):
                gdf_new = gpd.GeoDataFrame(columns=columns)
                # basins that intersect with the cell
                possible_matches_index = list(sindex.intersection(cell.bounds))
                possible_matches = gdf.iloc[possible_matches_index]
                # intersection between the basin and the cell
                intersection = possible_matches.intersection(cell)
                # percentage of the cell covered by each basin
                percentage = intersection.apply(lambda x: x.area/cell.area)
                # precise matches where percentage > 0
                precise_matches = possible_matches[possible_matches.index.isin(percentage[percentage > 0].index)]
        
                for column in gdf_new.columns:
                    if (column != 'geometry') and (column != 'percentage') and (column != 'cell5m'):
                        gdf_new[column]=precise_matches[column]
                    else:
                        if column == 'geometry':
                            gdf_new[column]=intersection.loc[precise_matches.index]
                        if column == 'percentage':
                            gdf_new[column]=percentage.loc[precise_matches.index]
                        if column == 'cell5m':
                            gdf_new[column]=grid['cell5m'].iloc[n]
                        
                gdf_new[properties] = gdf_new[properties].astype('object')
                for i in range(len(gdf_new)):
                    # Add the content to the right schema in the new shp
                    layer2.write({
                        'properties': OrderedDict(gdf_new[properties].iloc[i].to_dict()),
                        'geometry': mapping(gdf_new['geometry'].iloc[i])
                    });
                    
        
print("baseline geometries")
gdf_path = '/Volumes/MacBook HD/data/aqueduct/dst/spam2010/baseline_geo/baseline_geo.shp'
out_path = '/Volumes/MacBook HD/data/aqueduct/dst/spam2010/cell5m_baseline/cell5m_baseline.shp'
rtree_intersect_fiona(gdf_path, cell5m, out_path)

print("projected geometries")
gdf_path = '/Volumes/MacBook HD/data/aqueduct/dst/spam2010/projected_geo/projected_geo.shp'
out_path = '/Volumes/MacBook HD/data/aqueduct/dst/spam2010/cell5m_projected/cell5m_projected.shp'
rtree_intersect_fiona(gdf_path, cell5m, out_path)