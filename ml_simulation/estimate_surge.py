import pandas as pd
import plotly.express as px
import numpy as np

hurricanes = pd.read_csv('ibtracs.NA.list.v04r00.csv')
list_of_names = hurricanes['NAME']
list_of_names = list_of_names.to_list()
names = []
[names.append(x) for x in list_of_names if x not in names]
hurricanes = hurricanes.groupby(['SID'])
Harvey = hurricanes.get_group('2017228N14314')
# geometry = [Point(xy) for xy in zip(Harvey['LON'], Harvey['LAT'])]
# gdf = GeoDataFrame(Harvey, geometry=geometry)
flood = pd.read_csv('2017228N14314_surge/meow_Galveston.csv')
fig = px.scatter_mapbox(Harvey,lat='LAT',lon='LON')
fig.add_densitymapbox(lat=flood[' Lat'],lon=-1*flood[' Lon'])
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
print('done')