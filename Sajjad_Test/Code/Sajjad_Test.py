import geopandas as gpd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
from copy import deepcopy
import pandas as pd
import os
import json

# climada libraries
from climada.hazard import TCTracks
from climada.hazard import TropCyclone, Centroids


# HURRICANE INFORMATION FROM IBTrACS
data_provider = 'usa'
hurricane_id = '2017228N14314'          # Storm ID from IBTrACS; This is the ID for Hurricane Harvey (2017)
hurricane_name = 'Hurricane Harvey'
time_report = 2                         # The hours of time stamps i.e. data is provided for every "time_report" hours

# WINDFIELD GENERATION FROM CLIMADA
min_lat, max_lat = 25, 37               # Min and max lattitude for the centroids raster of climada
min_lon, max_lon = -108, -92.5          # Min and max longitude for the centroids raster of climada
centroid_resolution = 0.05              # Resolution for centroids (Hint: lower the better but takes more computation)
intensity_threshold = 0                 # define threshold to compute intensities (eg. 10 means windspeed < 10 is considered as 0)
store_windfields = False                # Boolean value that determines if one needs to save windfield vector (returns csr sparse matrix) and can be accessed by "windfields" method 


# SYNTHETIC TRACK CONFIGURAION
synthetic_track_numbers = 5             # Number of ensemble members per track; Default: 9

# CLIMATE CHANGE SCENARIO
reference_year = 2055                   # Year between 2000 and 2100; default: 2050
rcp_scenario = 45                       # 6 for RCP 2.6, 45 for RCP 4.5, 60 for RCP 6.0 and 85 for RCP 8.5; default: 45


# Loading Track Information
hurricane_track = TCTracks.from_ibtracs_netcdf(provider = data_provider, storm_id = hurricane_id)

# Plotting Hurricane Track
hurricane_track_plot = hurricane_track.plot()

hurricane_track_plot.set_title(hurricane_name) # Plot Title

# Data under Hurricane Track
Hurricane_Data = hurricane_track.get_track(hurricane_id)
Hurricane_Data

type(Hurricane_Data)