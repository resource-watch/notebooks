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



# Read cell5M geometries intersected with baseline basins
print('Read cell5M geometries intersected with baseline basins')
cell5M_baseline = gpd.read_file('/Volumes/MacBook HD/data/aqueduct/dst/spam2010/cell5m_baseline/cell5m_baseline.shp')
cell5M_baseline['aq30_id'] = cell5M_baseline['aq30_id'].astype('int64')
cell5M_baseline['percentage'] = cell5M_baseline['percentage'].astype('float64')
cell5M_baseline['percentage'] = cell5M_baseline['percentage'].apply(lambda x: round(x,4))
cell5M_baseline['cell5m'] = cell5M_baseline['cell5m'].astype('int')

# Read cell5M geometries intersected with projected basins
print('Read cell5M geometries intersected with projected basins')
cell5M_projected = gpd.read_file('/Volumes/MacBook HD/data/aqueduct/dst/spam2010/cell5m_projected/cell5m_projected.shp')
cell5M_projected['basinid'] = cell5M_projected['basinid'].astype('int64')
cell5M_projected['percentage'] = cell5M_projected['percentage'].astype('float64')
cell5M_projected['percentage'] = cell5M_projected['percentage'].apply(lambda x: round(x,4))
cell5M_projected['cell5m'] = cell5M_projected['cell5m'].astype('int')

# Add cell5M geometry and baisin ids to the SPAM data table
print('Add cell5M geometry and baisin ids to the SPAM data table')
df_filtered = pd.read_csv('/Volumes/MacBook HD/data/aqueduct/dst/spam2010/data_filtered.csv')
df_filtered.drop(columns=['Unnamed: 0'], inplace=True)
gdf_filtered = gpd.GeoDataFrame(df_filtered)
gdf_filtered['cell5m'] = gdf_filtered['cell5m'].astype('int')

# Add baseline basins
print('Add baseline basins')
# Merge GeoDataFrames
filtered_cell5M_baseline = pd.merge(left=gdf_filtered, right=cell5M_baseline, how='left', on='cell5m')

# Multiply the area and the production with the percentage of each cell fraction
def f(*x):
    return x[0]*x[1]
filtered_cell5M_baseline['prod'] = filtered_cell5M_baseline[['prod','percentage']].apply(lambda x: f(*x), axis=1).round(1)
filtered_cell5M_baseline['area'] = filtered_cell5M_baseline[['area','percentage']].apply(lambda x: f(*x), axis=1).round(1)
filtered_cell5M_baseline.drop(columns=['percentage'], inplace=True)

# Add projected basins
filtered_cell5M_projected = pd.merge(left=gdf_filtered, right=cell5M_projected, how='left', on='cell5m')

# Multiply the area and the production with the percentage of each cell fraction
def f(*x):
    return x[0]*x[1]
filtered_cell5M_projected['prod'] = filtered_cell5M_projected[['prod','percentage']].apply(lambda x: f(*x), axis=1).round(1)
filtered_cell5M_projected['area'] = filtered_cell5M_projected[['area','percentage']].apply(lambda x: f(*x), axis=1).round(1)
filtered_cell5M_projected.drop(columns=['percentage'], inplace=True)

rank = filtered_cell5M_baseline[['cell5m', 'crop', 'irrigation', 'prod', 'aq30_id']]


# Ranking of the crops in each cell
print('Ranking of the crops in each cell for baseline basins')
rank_baseline = filtered_cell5M_baseline[['cell5m', 'crop', 'irrigation', 'prod', 'aq30_id']].copy()

rank_baseline_new = pd.DataFrame(columns=['cell5m', 'crop', 'irrigation', 'prod', 'aq30_id', 'rank'])

for irrigation in ['irrigated', 'rainfed']:
    rank = rank_baseline[rank_baseline['irrigation'] == irrigation]
    
    rank.sort_values(['cell5m'], inplace=True)
    cell5m_unique = rank['cell5m'].unique()
    cell5m_unique.sort()
    
    cell = []
    basin = []
    prod = []
    ranking = []

    for cell5m in  tqdm(cell5m_unique):
        df = rank[rank['cell5m'] == cell5m]
        for aq30_id in df['aq30_id'].unique():
            df_aq = df[df['aq30_id'] == aq30_id]
        
            cell.extend([cell5m] * len(df_aq))
            basin.extend([aq30_id] * len(df_aq))
            prod.extend(list(df_aq['prod']))
            ranking.extend(list(df_aq['prod'].rank(ascending=False)))
        
    df_rank = pd.DataFrame({'cell5m': cell, 'aq30_id': basin, 'prod': prod, 'rank': ranking}) 
    

    rank_new = pd.merge(left=rank, right=df_rank, how='inner', on=['cell5m', 'aq30_id', 'prod'])   
    
    rank_baseline_new = pd.concat([rank_baseline_new, rank_new])
    
    rank_baseline_new.to_csv('/Volumes/MacBook HD/data/aqueduct/dst/spam2010/rank_baseline.csv')
    
    
print('Ranking of the crops in each cell for projected basins')  
rank_projected = filtered_cell5M_projected[['cell5m', 'crop', 'irrigation', 'prod', 'basinid']].copy()

rank_projected_new = pd.DataFrame(columns=['cell5m', 'crop', 'irrigation', 'prod', 'basinid', 'rank'])

for irrigation in ['irrigated', 'rainfed']:
    rank = rank_projected[rank_projected['irrigation'] == irrigation]
    
    rank.sort_values(['cell5m'], inplace=True)
    cell5m_unique = rank['cell5m'].unique()
    cell5m_unique.sort()
    
    cell = []
    basin = []
    prod = []
    ranking = []

    for cell5m in  tqdm(cell5m_unique):
        df = rank[rank['cell5m'] == cell5m]
        for basinid in df['basinid'].unique():
            df_aq = df[df['basinid'] == basinid]
        
            cell.extend([cell5m] * len(df_aq))
            basin.extend([basinid] * len(df_aq))
            prod.extend(list(df_aq['prod']))
            ranking.extend(list(df_aq['prod'].rank(ascending=False)))
        
    df_rank = pd.DataFrame({'cell5m': cell, 'basinid': basin, 'prod': prod, 'rank': ranking}) 
    

    rank_new = pd.merge(left=rank, right=df_rank, how='inner', on=['cell5m', 'basinid', 'prod'])   
    
    rank_projected_new = pd.concat([rank_projected_new, rank_new])
    
    rank_projected_new.to_csv('/Volumes/MacBook HD/data/aqueduct/dst/spam2010/rank_projected.csv')