#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jorid Topi

This script performs the data structuring tasks for the text analysis of the NHANES data

Creates seafood species to side dish associations to be used for the analysis
"""

import pandas as pd
import numpy as np
import re


#Read filtered dataframe
nhanes = pd.read_pickle('../../Data/nhanes_text_post.pkl')


#Obtain dataframe with seafood items
seafood_df = nhanes[nhanes['DR1I_PF_SEAFD_TOT'] > 0]
#Obtain dataframe with side dishes
side_dish_df = nhanes[nhanes['DR1I_PF_SEAFD_TOT'] == 0]

"""
Obtain initial test corpus for the whole meal, seafood item only, and side dishes only
Obtains the first word in the text description string before a comma, if comma exists.
Obtains the whole string in the text description if comma is not present.
"""
food_type_cps = nhanes['DESCRIPTION'].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)
seafood_cps = seafood_df['DESCRIPTION'].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)
side_dish_cps = side_dish_df['DESCRIPTION'].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)


"""
Create a dataframe that joins the seafood corpus with seafood df
"""
seafood_cps_key = pd.DataFrame(seafood_cps)
seafood_cps_key.columns = ['Seafood_CPS']
seafood_df = seafood_df.join(seafood_cps_key, how='outer')


#Save pipeline output
food_type_cps.to_pickle('../../Data/food_type_cps.pkl')
seafood_cps.to_pickle('../../Data/seafood_cps.pkl')
side_dish_cps.to_pickle('../../Data/side_dish_cps.pkl')
seafood_df.to_pickle('../../Data/seafood_df.pkl')

'''
This section structures the data by meal. First using seafood grouping, then side dish grouping
'''

#Obtain only required variables
group_nhanes = nhanes[['SEQN', 'DR1.030Z', 'DR1.020', 'DESCRIPTION', 'species']]
#Define the grouping key by meal. Participant ID, Meal ID, and time of consumption
meal_key = ['SEQN', 'DR1.030Z', 'DR1.020']

'''
Seafood grouping
'''

#Obtain seafood items
sf_nhanes = group_nhanes[group_nhanes['species'].notna()]

#Group the seafood df by meal
sf_meal_group = sf_nhanes.groupby(meal_key)

#Obtain the unique seafood item for each meal
sf_group = sf_meal_group.apply(lambda x: x['species'].unique())
sf_group = sf_group.apply(pd.Series)

#Rename the series columns and convert both grouping indecies to columns
sf_group = sf_group.rename({0: 'SF1', 1: 'SF2', 2: 'SF3', 3: 'SF4', 4: 'SF5', 5: 'SF6', 6: 'SF7'}, axis=1)
sf_group.reset_index(level=0, inplace=True)
sf_group.reset_index(level=0, inplace=True)
sf_group.reset_index(level=0, inplace=True)

#Obtain the seafood item count in each column. Result can be used as a statistic to count
#the number of seafood species per meal
meal_fish_count = sf_group.count()


'''
Seafood description grouping
'''

#Group the seafood df by meal
sf_meal_group = sf_nhanes.groupby(meal_key)

#Obtain the unique seafood item for each meal
sf_des_group = sf_meal_group.apply(lambda x: x['DESCRIPTION'].unique())
sf_des_group = sf_des_group.apply(pd.Series)

#Rename the series columns and convert both grouping indecies to columns
sf_des_group = sf_des_group.rename({0: 'SFD1', 1: 'SFD2', 2: 'SFD3', 3: 'SFD4', 4: 'SFD5', 5: 'SFD6', 
                                    6: 'SFD7', 7: 'SFD8', 8: 'SFD9'}, axis=1)
sf_des_group.reset_index(level=0, inplace=True)
sf_des_group.reset_index(level=0, inplace=True)
sf_des_group.reset_index(level=0, inplace=True)


'''
Side dish grouping
'''

#Obtain non-seafood items
not_sf_group = group_nhanes[group_nhanes['species'].isnull()]

#Group the side dish df by meal
not_sf_group = not_sf_group.groupby(meal_key)

#Obtain the unique side dish descriptions for each meal
not_sf_group = not_sf_group.apply(lambda x: x['DESCRIPTION'].unique())

#Rename the series columns and convert both grouping indecies to columns
not_sf_group = not_sf_group.apply(pd.Series)
not_sf_group = not_sf_group.rename({0: 'SD1', 1: 'SD2', 2: 'SD3', 3: 'SD4', 4: 'SD5', 5: 'SD6', 6: 'SD7',
                  7: 'SD8', 8: 'SD9', 9: 'SD10', 10: 'SD11', 11: 'SD12', 12: 'SD13', 13: 'SD14',
                  14: 'SD15', 15: 'SD16', 16: 'SD17', 17: 'SD18', 18: 'SD19', 19: 'SD20', 20: 'SD21', 
                  21: 'SD22'}, axis=1)
not_sf_group.reset_index(level=0, inplace=True)
not_sf_group.reset_index(level=0, inplace=True)
not_sf_group.reset_index(level=0, inplace=True)

#Obtain the first word in description item for each column
for i in range(22):
    idx_string = 'SD' + str(i+1)
    not_sf_group[idx_string] = not_sf_group[idx_string].fillna('None')
    not_sf_group[idx_string] = not_sf_group[idx_string].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)

#Re-apply NaNs for counting purposes
not_sf_group = not_sf_group.replace('None', np.nan)


#Join the seafood species, seafood description, and derived side dish in a structured dataframe
df1 = pd.merge(sf_group, not_sf_group, how='left', on=meal_key)
df_final = pd.merge(df1, sf_des_group, how='left', on=meal_key)


df_final_cols = df_final.columns.values.tolist()

#Create a list of all the "SFx" columns, where x is a digit. This pulls in the columns containing the 
#seafood type from the structured database. 
#The regular expression looks for two digits after "SF" first, then it looks for one digit. 
#This will only work for SF0-SF99, and will break if there are more than 99 seafood dishes in one meal (unlikely)
sf_cols = []
for i in range(len(df_final_cols)):
    if (re.match(r"SF\d\d", df_final_cols[i])):
        sf_cols.append(re.findall(r"SF\d\d", df_final_cols[i])[0])
    elif (re.match(r"SF\d", df_final_cols[i])):
        sf_cols.append(re.findall(r"SF\d", df_final_cols[i])[0])
 
#Create a list of all the "SDx" columns, where x is a digit. This pulls in the columns containing the 
#side dish type from the structured database. 
#The regular expression looks for three digits after "SD" first, then it looks for two digits, then one. 
#This will only work for SD0-SD999, and will break if there are more than 999 seafood side dishes in one meal (unlikely)
sd_cols = []
for i in range(len(df_final_cols)):
    if (re.match(r"SD\d\d\d", df_final_cols[i])):
        sd_cols.append(re.findall(r"SD\d\d\d", df_final_cols[i])[0])
    elif (re.match(r"SD\d\d", df_final_cols[i])):
        sd_cols.append(re.findall(r"SD\d\d", df_final_cols[i])[0])
    elif (re.match(r"SD\d", df_final_cols[i])):
        sd_cols.append(re.findall(r"SD\d", df_final_cols[i])[0])

#Create the seafood to side dish associations by sequentially melting the dataframe, pivoting on each SF column
df_sf_to_sd = pd.DataFrame()
#Loop over the SF columns to pivot the associations
for i in sf_cols:
    #Temporary storage of the Df columns. The columns will be used to filter the DF
    #This line is used to reset at start of loop.
    df_cols_temp = [] 
    #Append the DF columns with the SD columns
    for j in range(len(sd_cols)):
        df_cols_temp.append(sd_cols[j]) 
    #Append the DF columns with the SF pivot column
    df_cols_temp.append(i)
    #Include only SF pivot column and all SD columns
    df_temp = df_final[df_cols_temp]
    #Melt the dataframe by the SF pivot column
    df_temp = pd.melt(df_temp, id_vars=i)
    #Rename the the SF pivot column to a common name to be used in all loop iterations
    #Rename variable to the sd_n, to indicate the number of side dishes for the seafod type
    df_temp.rename({i: 'sf_type', 'variable': 'sd_n', 'value': 'sd_name'}, axis=1, inplace=True)
    #Append the result of each loop to the final dataframe
    df_sf_to_sd = df_sf_to_sd.append(df_temp) 
    df_sf_to_sd = df_sf_to_sd.reset_index(drop=True)
    
#Remove rows that are NaN
df_sf_to_sd = df_sf_to_sd[df_sf_to_sd['sf_type'].notna()]
df_sf_to_sd = df_sf_to_sd[df_sf_to_sd['sd_name'].notna()]

df_sf_to_sd.to_pickle('../../Data/sf_to_sd_association.pkl')

