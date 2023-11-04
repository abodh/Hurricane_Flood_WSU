import numpy as np
import pandas as pd
import scipy.io
import plotly.figure_factory as ff
import math
import json

# get load loss and expected load from matfiles
load_loss = scipy.io.loadmat("cityloadloss.mat")
con_list = [[element for element in upperElement] for upperElement in load_loss['countyname_loadloss']]
columns = ["City Name", "Load Loss"]
load_loss = pd.DataFrame(con_list, columns=columns)
load_loss['City Name'] = load_loss['City Name'].str[0]
expected_load = scipy.io.loadmat("cities_expected_load.mat")
con_list = [[element for element in upperElement] for upperElement in expected_load['cities_expectedload']]
columns = ["City Name", "Expected Load"]
expected_load = pd.DataFrame(con_list, columns=columns)
expected_load['City Name'] = expected_load['City Name'].str[0]

# find counties for associated city
zip_county = pd.read_csv("texas_zip_county_data.csv")
zip_county = pd.DataFrame(
    [zip_county['city'], zip_county['population'], zip_county['county_name'], zip_county['county_fips'],
     zip_county['county_weights']])
zip_county = zip_county.transpose()
zip_county['county_weights'] = zip_county['county_weights'].tolist()
total_counties = list((zip_county['county_name'].drop_duplicates()))
total_fips = list((zip_county['county_fips'].drop_duplicates()))
total_cities = list((zip_county['city'].drop_duplicates()))
load_loss['county_name'] = np.zeros(len(load_loss))
load_loss['population'] = np.zeros(len(load_loss))
expected_load['county_name'] = np.zeros(len(expected_load))
expected_load['population'] = np.zeros(len(expected_load))
for i, city in enumerate(load_loss['City Name']):
    list_of_county_fips = {}
    for j, city_list in enumerate(zip_county['city']):
        city_list = city_list.upper()
        city_list = city_list.replace(' ', '')
        city_list = city_list.replace('\'', '')
        if city_list == city:
            list_of_county_fips.update(json.loads(zip_county.loc[j, 'county_weights']))
            load_loss.loc[i, 'population'] += zip_county.loc[j, 'population']
    load_loss.loc[i, 'county_name'] = str(list_of_county_fips)
for i, city in enumerate(expected_load['City Name']):
    list_of_county_fips = {}
    for j, city_list in enumerate(zip_county['city']):
        city_list = city_list.upper()
        city_list = city_list.replace(' ', '')
        city_list = city_list.replace('\'', '')
        if city_list == city:
            list_of_county_fips.update(json.loads(zip_county.loc[j, 'county_weights']))
            expected_load.loc[i, 'population'] += zip_county.loc[j, 'population']
    expected_load.loc[i, 'county_name'] = str(list_of_county_fips)

# distribute load loss to each county based on population
load_loss_county = pd.Series(index=total_fips, dtype=float, data=[0 for i in range(len(total_fips))])
expected_load_county = pd.Series(index=total_fips, dtype=float, data=[0 for i in range(len(total_fips))])
for i in range(len(total_fips)):
    for j, dict in enumerate(load_loss['county_name']):
        dict = eval(dict)
        if dict.get(str(total_fips[i])):
            load_loss_county.loc[total_fips[i]] += load_loss.loc[j, 'Load Loss'] * float(
                dict.get(str(total_fips[i]))) / 100
for i in range(len(total_fips)):
    for j, dict in enumerate(expected_load['county_name']):
        dict = eval(dict)
        if dict.get(str(total_fips[i])):
            expected_load_county.loc[total_fips[i]] += expected_load.loc[j, 'Expected Load'] * float(
                dict.get(str(total_fips[i]))) / 100

# Manually add any non mapped losses.
for i in range(len(load_loss)):
    if load_loss.loc[i, 'City Name'] == 'FORTHOOD':
        fip = 48099
        load_loss_county[fip] += load_loss.loc[i, 'Load Loss']
    if load_loss.loc[i, 'City Name'] == 'LACKLANDAFB':
        fip = 48029
        load_loss_county[fip] += load_loss.loc[i, 'Load Loss']
    if load_loss.loc[i, 'City Name'] == 'LEWSIVILLE':
        fip = 48121
        load_loss_county[fip] += load_loss.loc[i, 'Load Loss']
    if load_loss.loc[i, 'City Name'] == 'SILVER':
        fip = 48081
        load_loss_county[fip] += load_loss.loc[i, 'Load Loss']
    if load_loss.loc[i, 'City Name'] == 'WINCHESTER':
        fip = 48149
        load_loss_county[fip] += load_loss.loc[i, 'Load Loss']
for i in range(len(expected_load)):
    if expected_load.loc[i, 'City Name'] == 'FORTHOOD':
        fip = 48099
        expected_load_county[fip] += expected_load.loc[i,'Expected Load']
    if expected_load.loc[i, 'City Name'] == 'LACKLANDAFB':
        fip = 48029
        expected_load_county[fip] += expected_load.loc[i, 'Expected Load']
    if expected_load.loc[i, 'City Name'] == 'LEWSIVILLE':
        fip = 48121
        expected_load_county[fip] += expected_load.loc[i, 'Expected Load']
    if expected_load.loc[i, 'City Name'] == 'SILVER':
        fip = 48081
        expected_load_county[fip] += expected_load.loc[i, 'Expected Load']
    if expected_load.loc[i, 'City Name'] == 'WINCHESTER':
        fip = 48149
        expected_load_county[fip] += expected_load.loc[i, 'Expected Load']

# # county theme 5 - load loss/total load
theme_5 = load_loss_county / expected_load_county
theme_5 = theme_5.astype(float)
# # map theme 5
theme_5=theme_5.sort_index()
theme_5 = theme_5.tolist()
missing_counties = 0
for i,x in enumerate(theme_5):
    if math.isnan(x):
        missing_counties+=1
        theme_5[i] = -1
total_fips.sort()
# fig = ff.create_choropleth(fips=total_fips, values=theme_5, scope=['TX', 'LA', 'OK', 'NM'],
#                            title='Power Outage in Texas', legend_title='%outage',
#                            county_outline={'color': 'rgb(255,255,255)', 'width': 0.5})
# fig.show()
#
# # read in SVI info. Plot with social vulnerability
SVI_Texas = pd.read_csv('texas_2016_svi.csv')
county_SVI = SVI_Texas['RPL_THEMES']
county_SVI.index = SVI_Texas['FIPS']
# theme_5 = load_loss_county / expected_load_county
# modified_SVI = theme_5.add(county_SVI,fill_value=None)*0.5
# modified_SVI = pd.Series([-1 if math.isnan(x) else x for x in modified_SVI])
# fig = ff.create_choropleth(fips=total_fips, values=modified_SVI, scope=['TX', 'LA', 'OK', 'NM'],
#                            title='Social Vulnerability from Outage in Texas', legend_title='%vulnerable',
#                            county_outline={'color': 'rgb(255,255,255)', 'width': 0.5})
# fig.show()
fig = ff.create_choropleth(fips=county_SVI.index, values=county_SVI, scope=['TX', 'LA', 'OK', 'NM'],
                           title='Social Vulnerability Index Texas', legend_title='%vulnerable',
                           county_outline={'color': 'rgb(255,255,255)', 'width': 0.5})
fig.show()

print("done")
