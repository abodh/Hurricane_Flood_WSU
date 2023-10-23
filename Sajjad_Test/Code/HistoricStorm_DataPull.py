
# =============================================================================
# REQUIRED MODULES
# =============================================================================

# External Modules
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import os
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning)

# Climada Modules
from climada.hazard import TCTracks
from climada.hazard import TropCyclone, Centroids


# =============================================================================
# USER INPUTS
# =============================================================================

# storm information
data_provider = 'usa'       # set the data provider "usa" for default
start_year = 1992           # start year in the range of years from which the hurricane data is required
end_year = 2022             # end year in the range of years from which the hurricane data is required
sub_basin = 'GM'            # can provide basin or sub-basin. Here, 'GM' refers to the gulf of mexico
storm_id = '2017228N14314'  # For a specific hurricane
time_report = 1             # set the hours of time stamps i.e. data is provided for every "time_report" hours

# plotting
plot_fileType = '.png'
title_fontSize = 20
axis_fontSize = 16
label_fontSize = 10
legend_position = 'best'    # 'upper left', 'upper right', 'lower left', 'lower right' 'upper center', 'lower center', 'center left', 'center right'
xtick_rotation_deg = 30
savefigures_indicator = 1

# =============================================================================
# ACCESSING FOLDERS
# =============================================================================

# getting current file directory path
current_filepath = os.path.dirname(__file__)

# =============================================================================
# CREATING RESULTS FOLDER
# =============================================================================

# navigating to workplace folder
os.chdir("..")
workplace_folderpath = os.path.abspath(os.curdir)

#navigating to result folder
result_folderpath = os.path.join(workplace_folderpath, 'Results')

# result folder name
csv_foldername = 'Historic_Storm_csv'
image_foldername = 'Historic_Storm_Image'

# checking if folders exist, if not create folders
if (os.path.isdir(os.path.join(result_folderpath, csv_foldername))):
    z = None # folder exists already

else:
    # creating csv folder
    os.mkdir(os.path.join(result_folderpath, csv_foldername))

# checking if folders exist, if not create folders
if (os.path.isdir(os.path.join(result_folderpath, image_foldername))):
    z = None # folder exists already

else:
    # creating image folder
    os.mkdir(os.path.join(result_folderpath, image_foldername))

# getting result folder directory
csv_folderpath = os.path.join(result_folderpath, csv_foldername)
image_folderpath = os.path.join(result_folderpath, image_foldername)


# =============================================================================
# HISTORIC STORM GENERATION
# =============================================================================

# getting historic storm information from IBTrACS
storm_track_all = TCTracks.from_ibtracs_netcdf(provider=data_provider, year_range=(start_year, end_year), subbasin=sub_basin, correct_pres=False)

# computing total number of historic storms
storm_number_total = storm_track_all.size

# getting the list of all storms
storm_track_all_list = storm_track_all.data

# getting storm id, name and category dataframe
storm_info_df = pd.DataFrame(columns=['Storm ID', 'Name', 'Category'])

count = 0

# FOR LOOP: to save storm information as individual .csv file
for ii in range(len(storm_track_all_list)):

    # getting current storm information
    current_storm_id = storm_track_all_list[ii].attrs['sid']
    current_storm_name = storm_track_all_list[ii].attrs['name']
    current_storm_category = storm_track_all_list[ii].attrs['category']

    # assigning storm information (id, name and category) into dataframe
    current_storm_info_df = pd.DataFrame([[current_storm_id, current_storm_name, current_storm_category]],columns=['Storm ID', 'Name', 'Category'])
    storm_info_df = pd.concat([storm_info_df, current_storm_info_df], ignore_index=True)

    # based on the provider. and storm argument the track for the storm is obtained from the particular method
    current_storm_track = TCTracks.from_ibtracs_netcdf(provider=data_provider, storm_id=current_storm_id)

    # this method ensures that equal time step is reported back from TCTracks()
    current_storm_track.equal_timestep(time_report)  # data of hurricane every 'time_report' hours

    # generate synthetic tracks to generate per present hurricane tracks.
    """
        nb_synth_tracks         = number of synthetic tracks to generate (including original),
        max_shift_ini           = point upto which starting track is perturbed (in both lon and lat) using random uniform values (unit: decimal degree) 
        max_dspeed_rel          = Amplitude of translation speed perturbation in relative terms (0.2 -> 20%)
        max_ddirection          = Amplitude of track direction (bearing angle) perturbation per hour (unit: radian)
        autocorr_dspeed         = Temporal autocorrelation in translation speed perturbation at a lag of 1 hour,
        autocorr_ddirection     = 0.25,
        seed                    = 8,
        decay                   = True,
        use_global_decay_params = True,
        pool                    = None

        Note: the values below are tweaked manually. Please read more about these values in Climada documentation
        or refer to other references.
    """

    current_storm_track.calc_perturbed_trajectories(nb_synth_tracks=1, max_shift_ini=0.55, max_dspeed_rel=0.30,
                                            max_ddirection=np.pi / 360, autocorr_dspeed=0.6, autocorr_ddirection=0.25,
                                            seed=8, decay=True, use_global_decay_params=True, pool=None)

    # converting current storm data into dataframe
    current_storm_df = (current_storm_track.data[0]).to_dataframe() # as we are using synthetic track generation function [0] will give us the original track

    # creating .csv file name
    # IF LOOP: if storm has name, include name in the .csv file name
    if (current_storm_name == 'NOT_NAMED'):
        current_storm_csv_filename = current_storm_id + '_cat' + str(current_storm_category) + '.csv'

    else:
        current_storm_csv_filename = current_storm_id + '_cat' + str(current_storm_category) + '_' + current_storm_name + '.csv'

    # saving storm information as .csv file in the result folder
    current_storm_df.to_csv(os.path.join(csv_folderpath, current_storm_csv_filename), index=False)


    # =============================================================================
    # Plotting
    # =============================================================================

    # getting current storm track
    # current_storm_track = TCTracks.from_ibtracs_netcdf(provider=data_provider, storm_id=current_storm_id)

    # creating .png file name
    # IF LOOP: if storm has name, include name in the .png file name
    if (current_storm_name == 'NOT_NAMED'):
        current_storm_image_filename = current_storm_id + '_cat' + str(current_storm_category) + '.png'
        storm_plot_title = current_storm_id + '_cat' + str(current_storm_category)

    else:
        current_storm_image_filename = current_storm_id + '_cat' + str(current_storm_category) + '_' + current_storm_name + '.png'
        storm_plot_title = current_storm_id + '_cat' + str(current_storm_category) + '_' + current_storm_name

    # plotting the storm
    current_storm_track_plot = current_storm_track.plot()
    current_storm_track_plot.set_title(storm_plot_title)
    plt.tight_layout()

    # saving storm plot as .png file in the result folder
    plt.savefig(os.path.join(image_folderpath, current_storm_image_filename))

    count = count + 1
    print(count)

# =============================================================================
# Save Output as .csv in Results Folder
# =============================================================================

# saving all storm id, name and category into a single .csv
storm_info_filename = 'all_storm.csv'
storm_info_df.to_csv(os.path.join(csv_folderpath, storm_info_filename), index=False)


# =============================================================================
# Convert and Save Output .csv to .pickle in Results Folder
# =============================================================================

# getting all .csv files paths from .csv folder
csv_filename_list = os.listdir(csv_folderpath)

# initializing csv_filepath_list
csv_filepath_list = []

# FOR LOOP: for each file in csv_folderpath
for file in csv_filename_list:

    # check only .csv files
    if file.endswith('.csv'):
        # appending .csv file paths to csv_filepath_list
        csv_filepath_list.append(os.path.join(csv_folderpath, file))

'''
# initializing storm_output_dict
storm_output_dict = {}

storm_output_df = pd.DataFrame()

storm_output_columnname_list = []

counter = 0

# FOR LOOP: for each .csv file in csv_filepath_list
for file_path in csv_filepath_list:

    # reading .csv file in dataframe
    current_df = pd.read_csv(file_path)

    # getting current_df_1
    if (counter == 0):

        # Keeping DateTime Column
        Current_DF_1 = Current_DF

    else:

        # Dropping DateTime Column
        Current_DF_1 = Current_DF.drop(Current_DF.columns[[0]], axis=1)

    # Concatenating IDF_OutputVariable_Full_DF
    IDF_OutputVariable_Full_DF = pd.concat([IDF_OutputVariable_Full_DF, Current_DF_1], axis="columns")

'''


