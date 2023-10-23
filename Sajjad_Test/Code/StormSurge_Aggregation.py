"""
Author: Sajjad Uddin Mahmud, WSU

This code is to get the aggregated MEOWs (Maximum Elevation of Water) levels from SLOSH Display Program (SDP) output at different basins.

Input: User will provide storm_id, category, direction, translational speed, tide level and basin.
Output: .csv files for each basin, contains MEOW levels gathered from SDP output files, also provides average and maximum MEOW level for the given combination.

"""



# =============================================================================
# LIBRARIES
# =============================================================================

import os
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings(action='ignore', category=RuntimeWarning)


# =============================================================================
# ACCESSING FOLDERS
# =============================================================================
# getting current file directory path
current_filepath = os.path.dirname(__file__)

# navigating to workplace folder
os.chdir("..")
workplace_folderpath = os.path.abspath(os.curdir)

#navigating to data folder
data_folderpath = os.path.join(workplace_folderpath, 'Data')
surgedata_folderpath = os.path.join(data_folderpath, 'SloshSurge')


# =============================================================================
# USER INPUT
# =============================================================================
storm_id = '2003188N11307'
category = 1  # category = 0, 1, 2, 3, 4, 5
speed = ['15']  # forward speed = '05', '10', '15', '25'
direction = ['wnw', 'w']  # directions = 'ene', 'ne', 'nne', 'n', 'nnw', 'nw', 'wnw', 'w', 'wsw'
tide_level = ['mean', 'high']  # tide level = 'mean', 'high'
basin = ['Sabine', 'Galveston', 'Matagorda', 'Corpus', 'Laguna']  # texas basins = 'Sabine' , 'Galveston', 'Matagorda', 'Corpus', 'Laguna', user can choose one or multiple as list format

# =============================================================================
# CREATING RESULTS FOLDER
# =============================================================================
# navigating to result folder
result_folderpath = os.path.join(workplace_folderpath, 'Results')

# result folder name
surge_aggregation_foldername = 'Surge_Aggregation'
surge_foldername = storm_id + '_surge'

# checking if folders exist, if not create folders
if (os.path.isdir(os.path.join(result_folderpath, surge_aggregation_foldername))):
    z = None # folder exists already
else:
    # creating folder
    os.mkdir(os.path.join(result_folderpath, surge_aggregation_foldername))

surge_aggregation_folderpath = os.path.join(result_folderpath, surge_aggregation_foldername)

if (os.path.isdir(os.path.join(surge_aggregation_folderpath, surge_foldername))):
    z = None # folder exists already
else:
    # creating folder
    os.mkdir(os.path.join(surge_aggregation_folderpath, surge_foldername))

surge_folderpath = os.path.join(surge_aggregation_folderpath, surge_foldername)


# =============================================================================
# GETTING SLOSH SURGE DATA
# =============================================================================

# FOR LOOP:surge generation for each basin

for b in range(len(basin)):


    # getting basin folder
    basin_foldername = 'Basin_' + basin[b]
    basin_folderpath = os.path.join(surgedata_folderpath, basin_foldername)

    count = 1

    # FOR LOOP: aggregating storm surge data
    for d in range(len(direction)):
        for s in range(len(speed)):
            for t in range(len(tide_level)):

                # setting tide level code: tide level code as per SDP = i0:mean, i2:high except Galveston where i1:mean
                if (basin == 'Galveston' and tide_level[t] == 'mean'):
                    tide_level_code = 'i1'
                elif (tide_level[t] == 'mean'):
                    tide_level_code = 'i0'
                elif (tide_level[t] == 'high'):
                    tide_level_code = 'i2'

                # getting surge csv file
                surge_csv_filename = direction[d] + str(category) + speed[s] + tide_level_code + '.csv'

                current_stormsurge_df_path = os.path.join(basin_folderpath, surge_csv_filename)

                # IF LOOP: checking whether the particular file exists
                if os.path.exists(current_stormsurge_df_path):
                    current_stormsurge_df = pd.read_csv(current_stormsurge_df_path)

                    # IF LOOP: first time setting up the output dataframe
                    if count == 1:
                        output_surge_df = current_stormsurge_df

                        # renaming column name
                        output_surge_df.rename(columns={' Depth': 'Depth_' + direction[d] + str(category) + speed[s] + tide_level_code}, inplace=True)

                    # getting data into output dataframe from rest of the files
                    else:
                        current_surge_depth = current_stormsurge_df.iloc[:, 4]

                        # appending current surge into output_surge_df
                        output_surge_df = pd.concat([output_surge_df, current_surge_depth], axis=1)
                        output_surge_df.rename(columns={' Depth': 'Depth_' + direction[d] + str(category) + speed[s] + tide_level_code},inplace=True)

                    count = count + 1

                # IF LOOP: in case the particular file does not exist, continue
                else:
                    continue


    # calculating the average and maximum surge depth
    Depth_avg = (output_surge_df.iloc[:,4:]).mean(axis=1)
    Depth_max = (output_surge_df.iloc[:,4:]).max(axis=1)

    # appending average and maximum depth data into output_surge_df
    output_surge_df['Depth_avg'] = Depth_avg
    output_surge_df['Depth_max'] = Depth_max


    # =============================================================================
    # SAVING OUTPUT FILES
    # =============================================================================

    # creating .csv file name

    surge_csv_filename = 'meow_' + basin[b] + '.csv'

    # saving storm information as .csv file in the result folder
    output_surge_df.to_csv(os.path.join(surge_folderpath, surge_csv_filename), index=False)








