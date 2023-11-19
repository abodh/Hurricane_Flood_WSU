import numpy as np
import pandas as pd
import scipy.io
import plotly.figure_factory as ff
import math
import json
import plotly.express as px


# function process_load_data: processes the city-level data, removes unwanted features, converts it to county level.
# does this for both the load loss per city and load demand per city.
# INPUT: matfile from 2000-bus system loss containing load in MW per zip code
# OUTPUT: load in MW per county
def process_load_data(city_load, keyphrase):
    con_list = [[element for element in upperElement] for upperElement in city_load[keyphrase]]
    columns = ["City Name", "Load"]
    city_load = pd.DataFrame(con_list, columns=columns)
    city_load['City Name'] = city_load['City Name'].str[0]
    # find counties for associated city
    zip_county = pd.read_csv("texas_zip_county_data.csv")
    zip_county = pd.DataFrame(
        [zip_county['city'], zip_county['population'], zip_county['county_name'], zip_county['county_fips'],
         zip_county['county_weights']])
    zip_county = zip_county.transpose()
    zip_county['county_weights'] = zip_county['county_weights'].tolist()
    total_fips = list((zip_county['county_fips'].drop_duplicates()))
    city_load['county_name'] = np.zeros(len(city_load))
    city_load['population'] = np.zeros(len(city_load))
    #  create list of counties that each city has in common, and respective pop. weights. Find total population per city.
    for i, city in enumerate(city_load['City Name']):
        list_of_county_fips = {}
        for j, city_list in enumerate(zip_county['city']):
            city_list = city_list.upper()
            city_list = city_list.replace(' ', '')
            city_list = city_list.replace('\'', '')
            if city_list == city:
                list_of_county_fips.update(json.loads(zip_county.loc[j, 'county_weights']))  # add county weights to list
                city_load.loc[i, 'population'] += zip_county.loc[j, 'population']  # find city's total pop
        city_load.loc[i, 'county_name'] = str(list_of_county_fips)
    # distribute load loss to each county based on population
    county_load = pd.Series(index=total_fips, dtype=float, data=[0 for i in range(len(total_fips))])
    for i in range(len(total_fips)):  # enumerate through all FIPS (counties) within a given city.
        for j, dict in enumerate(city_load['county_name']):
            dict = eval(dict)
            if dict.get(str(total_fips[i])):  # if the current FIPS is in the FIPS dictionary for the city.
                county_load.loc[total_fips[i]] += city_load.loc[j, 'Load'] * float(
                    dict.get(str(total_fips[i]))) / 100  # Add the city load that has the respective FIPS in it proportioned to that pop.
    # Manually add any non mapped losses. (Pre-processed)
    for i in range(len(city_load)):
        if city_load.loc[i, 'City Name'] == 'FORTHOOD':
            fip = 48099
            county_load[fip] += city_load.loc[i, 'Load']
        if city_load.loc[i, 'City Name'] == 'LACKLANDAFB':
            fip = 48029
            county_load[fip] += city_load.loc[i, 'Load']
        if city_load.loc[i, 'City Name'] == 'LEWSIVILLE':
            fip = 48121
            county_load[fip] += city_load.loc[i, 'Load']
        if city_load.loc[i, 'City Name'] == 'SILVER':
            fip = 48081
            county_load[fip] += city_load.loc[i, 'Load']
        if city_load.loc[i, 'City Name'] == 'WINCHESTER':
            fip = 48149
            county_load[fip] += city_load.loc[i, 'Load']
    return county_load, total_fips


# function plot: plots county level data of ERCOT region.
def plot(county_data, title):
    colorscale = ["white","#A0D2E7", "#81B1D5", "#3D60A7", "#26408B", "#0F084B", "black"]
    endpts = list(np.linspace(0, 100, len(colorscale) - 1))
    county_data.dropna(inplace=True)  # drop nan values (no data for given county)
    county_data.replace(to_replace=0.0, value=0.0001,inplace=True)  # change any 0 outages to 0.001 - this fixes the graph legend
    fig = ff.create_choropleth(fips=county_data.index, values=county_data, colorscale=colorscale, scope=['TX'],
                               binning_endpoints=endpts,
                               title=title, legend_title='% Vulnerability',
                               county_outline={'color': 'rgb(0,0,0)', 'width': 0.5},
                               state_outline={'color': 'rgb(0,0,0)', 'width': 0.75})
    fig.show()


load_loss = scipy.io.loadmat("hurricane_load_loss.mat")
keyphrase = 'load_loss'
county_load_loss, total_fips = process_load_data(load_loss,keyphrase)
expected_load = scipy.io.loadmat("hurricane_expected_load.mat")
keyphrase = 'total_load'
county_demand, total_fips = process_load_data(expected_load,keyphrase)
# # county theme 5 - load loss/total load
theme_5 = county_load_loss / county_demand
theme_5 = theme_5.astype(float)*100
# # map theme 5
theme_5=theme_5.sort_index()
total_fips.sort()
title = "Outage Vulnerability Index from Hurricanes in ERCOT"
plot(theme_5, title)
# # read in SVI info. Plot with social vulnerability
SVI_Texas = pd.read_csv('texas_2016_svi.csv')
county_SVI = SVI_Texas['RPL_THEMES']*100
county_SVI.index = SVI_Texas['FIPS']
theme_5 = county_load_loss / county_demand
modified_SVI = theme_5*0.2+county_SVI*0.8
title = "Integrated Community Vulnerability Index from Hurricanes in ERCOT"
plot(modified_SVI, title)

print("done")