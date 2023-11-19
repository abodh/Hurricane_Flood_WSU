import numpy as np
import pandas as pd
import scipy.io
import json
import plotly.express as px
from urllib.request import urlopen

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
def plot(county_data, pl_scale):
    county_data.dropna(inplace=True)  # drop nan values (no data for given county)
    with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
        counties = json.load(response)
    fig=px.choropleth(county_data,geojson=counties,
                      locations=county_data.index,color=county_data,
                      labels={'color':'% Vulnerability'},
                      color_continuous_scale=pl_scale)
    fig.update_geos(fitbounds="locations", scope='usa',visible=True)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
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
plot(theme_5, "PuBu")
# # read in SVI info. Plot with social vulnerability
SVI_Texas = pd.read_csv('texas_2016_svi.csv')
county_SVI = SVI_Texas['RPL_THEMES']*100
county_SVI.index = SVI_Texas['FIPS']
theme_5 = county_load_loss / county_demand
modified_SVI = theme_5*0.2+county_SVI*0.8
plot(modified_SVI, "Greens")

print("done")