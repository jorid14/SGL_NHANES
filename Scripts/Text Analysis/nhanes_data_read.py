#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 11:12:05 2021

@author: Jorid Topi

This script reads the NHANES and NHANES_Full data files. The NHANES_Full dataset has been added
to the analysis at a later point than the NHANES data file. The NHANES_Full dataset contains
additional variables/information that is obtained using the Food Patterns Equivalents Database 
Components (FPED). 

"""

import pandas as pd

'''
This section reads the original NHANES data file and drop any column that is not a priority 1
from the variable analysis lookup table. The output is saved as a pickle data file.
'''

#Read the NHANES dataset
nhanes = pd.read_csv('../../Data/nhanes.csv')

#Use the variable lookup to filter out variables for reducing the dataset
variable_lookup = pd.read_csv('../../Analysis/Variable_Analysis_Lookup.csv')
#Pull out the priority 0 variables, which are dropped from the start
var_pri_0 = variable_lookup[variable_lookup['Priority'] == 0]
#Pull out the priority 2 and 3 variables, which are dropped in this pipeline
var_pri_2 = variable_lookup[variable_lookup['Priority'] == 2]
var_pri_3 = variable_lookup[variable_lookup['Priority'] == 3]

#The following variables have been deemed irrelevant for this analysis, so they are dropped.
nhanes = nhanes.drop(var_pri_0['Variable'], axis = 1)
nhanes = nhanes.drop(var_pri_2['Variable'], axis = 1)
nhanes = nhanes.drop(var_pri_3['Variable'], axis = 1)


'''
This section finds the meals that contain seafood by obtaining the unique combination of 
person interviewed, meal name, and meal time for every observation that contains seafood.
Those unique key values are used to pull in the rest of the food items that are consumed in 
that same meal, to create the filtered data frame. 
'''

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

'''
This section performs data enconding and transformations:
    1. Create Survey Year variable based on lookup, mapping from CDC source
    2. Map the meal occasion data, based on the DR1.030Z encoding key and CDC source
    3. Create a time column, in a pandas time format, using the DR1.020 time variable
'''

#Create Survey Year variable based on lookup, mapping from CDC source
survey_year_lookup = {4: '2005-2006', 5: '2009-2010', 6: '2011-2012', 7: '2013-2014', 8:'2015-2016', 9:'2017-2018'}
nhanes['Survey_Year'] = nhanes['SDDSRVYR'].map(survey_year_lookup)


#Create Survey Year variable based on lookup, mapping from CDC source
meal_name_lookup = {1: 'Breakfast', 2: 'Lunch', 3: 'Dinner', 4: 'Supper', 5:'Brunch', 6:'Snack',
                    7: 'Drink', 8: 'Infant Feeding', 9: 'Extended consumption', 10: 'Desayano',
                    11: 'Almuerzo', 12: 'Comida', 13: 'Merienda', 14: 'Cena', 15: 'Enter comida',
                    16: 'Botana', 17: 'Bocadillo', 18: 'Tentempie', 19: 'Bebida', 91: 'Other'}


nhanes['Meal_Name'] = nhanes['DR1.030Z'].map(meal_name_lookup)

#Create a time column, in a pandas time format
#Remove the 5AM bias from the value in seconds
def remove_time_bias(time_in):
    midnight = 24*60*60
    if (time_in >= midnight):
        time_post = time_in - midnight
    else: time_post = time_in
    return round(time_post)

#Create time variable and convert to time formatefrom DR1.020
nhanes['Time'] = nhanes['DR1.020'].apply(remove_time_bias)
nhanes['Time'] = nhanes['Time'].astype(int)
nhanes['Time'] = nhanes['Time'].round().apply(pd.to_timedelta, unit='s')


#Save data for further processing
nhanes.to_pickle('../../Data/nhanes_text_post.pkl')










