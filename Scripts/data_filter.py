#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 10:05:56 2021

@author: Jorid Topi

This script finds the meals that contain seafood by obtaining the unique combination of 
person interviewed, meal name, and meal time for every observation that contains seafood.
Those unique key values are used to pull in the rest of the food items that are consumed in 
that same meal, to create the filtered data frame. This is done for both the original NHANES
and the NHANES_full dataframes. 

"""

import pandas as pd

'''
This section performs the filtering for the original NHANES data file, and saves filtered
dataframe to a pickle data file.
'''
#Read output of first data cleanup
nhanes = pd.read_pickle('../Data/nhanes_pre_proc.pkl')

#Obtain dataframe with seafood items
seafood_df = nhanes[nhanes['DR1I_PF_SEAFD_TOT'] > 0]

#Define the dataframe join key for pulling other food items consumed with seafood
join_key = ['SEQN', 'DR1.030Z', 'DR1.020']

'''
This filter obtains the ID of the person interviewed, the meal and time, 
if there is at least one seafood item in this meal, time, for that person. 
'''
#Dropping the duplicates keeps a unique key for a meal where there is a seafood item
seafood_df_key = seafood_df.drop_duplicates(join_key)
#Dropp all other columns from this df, keep only the key columns
seafood_df_key = seafood_df_key[join_key]
#Join the nhanes df based on those keys
nhanes = pd.merge(seafood_df_key, nhanes, how='left', on=join_key)

#Save pipeline output
nhanes.to_pickle('../Data/nhanes_filtered.pkl')


'''
This section performs the filtering for the NHANES_full data file, and saves filtered
dataframe to a pickle data file.
'''
#Read output of first data cleanup for full df
nhanes_full = pd.read_pickle('../Data/nhanes_full_pre_proc.pkl')

#Obtain dataframe with seafood items for full df
seafood_full_df = nhanes_full[nhanes_full['DR1I_PF_SEAFD_TOT'] > 0]

'''
This filter obtains the ID of the person interviewed, the meal and time, 
if there is at least one seafood item in this meal, time, for that person. 
'''

#Dropping the duplicates keeps a unique key for a meal where there is a seafood item
seafood_full_df_key = seafood_full_df.drop_duplicates(join_key)
#Dropp all other columns from this df, keep only the key columns
seafood_full_df_key = seafood_full_df_key[join_key]
#Join the nhanes df based on those keys
nhanes_full = pd.merge(seafood_full_df_key, nhanes_full, how='left', on=join_key)

#Save pipeline output
nhanes_full.to_pickle('../Data/nhanes_full_filtered.pkl')
