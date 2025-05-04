# -*- coding: utf-8 -*-
"""
Created on Sun Apr 20 23:11:50 2025

@author: Jared
"""

#A simple map project, showing decline of employment in the manufacturing sector as well as county 
#level poverty rates

#Libraries
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import NYS_Functions as apa
#Importing Files____________________________________________________________________________
data = pd.read_csv('GoodData.csv')
GeoData = gpd.read_file("my_shapes.gpkg")
#____________Data Maniuplation and Validation______________
data_2 = data[(data["Month"] == 0) & (data["Title"] == "Manufacturing")]
service_produce = data[data["Title"] == "Service-Providing"].copy()
comparison = data[data["Title"].isin(["Service-Providing", "Goods Producing"])].copy()
#Data Validation, to ensure that "New York State" was removed.
csv_names = set(pd.read_csv('GoodData.csv')['Area Name'].unique())
shape_names = set(GeoData['Area Name'].unique())
missing_in_shapes = csv_names - shape_names
print(f"Area Names in CSV but missing in my_shapes.gpkg:, {missing_in_shapes}")
#__________________________________________________________________________________________
#Analysis Sample
df_result = apa.sector_pct_change(1998, 2006, data, ["Manufacturing", "Construction"], False, "Rochester Metro Area", True)
print(apa.list_sectors(data, filterby="Manu"))
