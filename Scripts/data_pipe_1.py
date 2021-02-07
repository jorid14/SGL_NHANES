#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 10:05:56 2021

@author: Jorid Topi

This is the priority 1 data pipeline, which is used for the primary objectives of the analysis.
The variable analysis lookup is used to keep only the variables that were identified as useful
for this analysis. The priority 2 and 3 variables are dropped, as well as variables that are 
no longer useful after being transformed.

"""

import pandas as pd

#Read output of first data cleanup
nhanes = pd.read_pickle('../Data/nhanes_pre_proc.pkl')


#Drop the variables that are now transformed. This is identified in the data_read.py

#New variables added in data_read
transformed_vars = ['SDDSRVYR', 'DR1.030Z', 'DR1.020']


#Use the variable lookup to filter out variables for reducing the dataset
variable_lookup = pd.read_csv('../Analysis/Variable_Analysis_Lookup.csv')

#Pull out the priority 2 and 3 variables, which are dropped in this pipeline
var_pri_2 = variable_lookup[variable_lookup['Priority'] == 2]
var_pri_3 = variable_lookup[variable_lookup['Priority'] == 3]


#Drop the transformed and priority 2 and 3 variables
nhanes = nhanes.drop(transformed_vars, axis = 1)
nhanes = nhanes.drop(var_pri_2['Variable'], axis = 1)
nhanes = nhanes.drop(var_pri_3['Variable'], axis = 1)


#Save pipeline output
nhanes.to_pickle('../Data/nhanes_1.pkl')


