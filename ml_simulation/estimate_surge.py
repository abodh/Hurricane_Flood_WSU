import numpy as np
import pandas as pd
import warnings

warnings.filterwarnings(action='ignore', category=RuntimeWarning)
from climada.hazard import TCTracks
from climada.hazard import TropCyclone, Centroids

# storm information
data_provider = 'usa'  # set the data provider "usa" for default
start_year = 1992  # start year in the range of years from which the hurricane data is required
end_year = 2022  # end year in the range of years from which the hurricane data is required
sub_basin = 'GM'  # can provide basin or sub-basin. Here, 'GM' refers to the gulf of mexico
storm_id = '2017228N14314'  # For a specific hurricane
time_report = 1  # set the hours of time stamps i.e. data is provided for every "time_report" hours

# getting historic storm information from IBTrACS
storm_track_all = TCTracks.from_ibtracs_netcdf(provider=data_provider, year_range=(start_year, end_year),
                                               subbasin=sub_basin, correct_pres=False)

# computing total number of historic storms
storm_number_total = storm_track_all.size

# getting the list of all storms
storm_track_all_list = storm_track_all.data

# getting storm id, name and category dataframe
storm_info_df = pd.DataFrame(columns=['Storm ID', 'Name', 'Category'])
