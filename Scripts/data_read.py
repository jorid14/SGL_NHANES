#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 11:12:05 2021

@author: jori
"""

import pandas as pd

#Read the NHANES dataset
nhanes = pd.read_csv('../Data/nhanes.csv')

#Use the variable lookup to filter out variables for reducing the dataset
variable_lookup = pd.read_csv('../Analysis/Variable_Analysis_Lookup.csv')
#Pull out the priority 0 variables, which are dropped from the start
var_pri_0 = variable_lookup[variable_lookup['Priority'] == 0]


#The following variables have been deemed irrelevant for this analysis, so they are dropped.
nhanes = nhanes.drop(var_pri_0['Variable'], axis = 1)



#Map the survey year data, based on the SDDSRVYR encoding key

#Obtain description and value counts
nhanes['SDDSRVYR'].describe()
nhanes['SDDSRVYR'].value_counts()

#Create Survey Year variable based on lookup, mapping from CDC source
survey_year_lookup = {4: '2005-2006', 5: '2009-2010', 6: '2011-2012', 7: '2013-2014', 8:'2015-2016', 9:'2017-2018'}
nhanes['Survey_Year'] = nhanes['SDDSRVYR'].map(survey_year_lookup)
#nhanes = nhanes.drop(['SDDSRVYR'], axis = 1)

#Check for NAs
#print("Survey Year NA count is "+str(nhanes['Survey_Year'].isnull().sum()))


#Map the meal occasion data, based on the DR1.030Z encoding key

#Obtain description and value counts
nhanes['DR1.030Z'].describe()
nhanes['DR1.030Z'].value_counts()

#Create Survey Year variable based on lookup, mapping from CDC source
meal_name_lookup = {1: 'Breakfast', 2: 'Lunch', 3: 'Dinner', 4: 'Supper', 5:'Brunch', 6:'Snack',
                    7: 'Drink', 8: 'Infant Feeding', 9: 'Extended consumption', 10: 'Desayano',
                    11: 'Almuerzo', 12: 'Comida', 13: 'Merienda', 14: 'Cena', 15: 'Enter comida',
                    16: 'Botana', 17: 'Bocadillo', 18: 'Tentempie', 19: 'Bebida', 91: 'Other'}


nhanes['Meal_Name'] = nhanes['DR1.030Z'].map(meal_name_lookup)
#nhanes = nhanes.drop(['DR1.030Z'], axis = 1)

#Check for NAs
#print("Meal Name NA count is "+str(nhanes['Meal_Name'].isnull().sum()))


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
#nhanes = nhanes.drop(['DR1.020'], axis = 1)





nhanes.to_pickle('../Data/nhanes_pre_proc.pkl')




