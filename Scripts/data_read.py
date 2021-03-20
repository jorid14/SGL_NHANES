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
nhanes = pd.read_csv('../Data/nhanes.csv')

#Use the variable lookup to filter out variables for reducing the dataset
variable_lookup = pd.read_csv('../Analysis/Variable_Analysis_Lookup.csv')
#Pull out the priority 0 variables, which are dropped from the start
var_pri_0 = variable_lookup[variable_lookup['Priority'] == 0]
#Pull out the priority 2 and 3 variables, which are dropped in this pipeline
var_pri_2 = variable_lookup[variable_lookup['Priority'] == 2]
var_pri_3 = variable_lookup[variable_lookup['Priority'] == 3]

#The following variables have been deemed irrelevant for this analysis, so they are dropped.
nhanes = nhanes.drop(var_pri_0['Variable'], axis = 1)
nhanes = nhanes.drop(var_pri_2['Variable'], axis = 1)
nhanes = nhanes.drop(var_pri_3['Variable'], axis = 1)

#Save data file 
nhanes.to_pickle('../Data/nhanes_pre_proc.pkl')


'''
This section reads the additional NHANES full data file and drops any column that is not a priority 1
from the variable analysis lookup table for the full file. The output is saved as a pickle data file.
'''

#Read the NHANES full dataset
nhanes_full = pd.read_csv('../Data/nhanes_full.csv')

#Use the variable lookup to filter out variables for reducing the dataset
variable_lookup_full = pd.read_csv('../Analysis/Variable_Analysis_Lookup_NHANES_full.csv')
#Pull out the priority 0 variables, which are dropped from the start
var_full_pri_0 = variable_lookup_full[variable_lookup_full['Priority'] == 0]
#Pull out the priority 2 variables, which are dropped from the start
var_full_pri_2 = variable_lookup_full[variable_lookup_full['Priority'] == 2]
#Pull out the priority 3 variables, which are dropped from the start
var_full_pri_3 = variable_lookup_full[variable_lookup_full['Priority'] == 3]

#The following variables have been deemed irrelevant for this analysis, so they are dropped.
nhanes_full = nhanes_full.drop(var_full_pri_0['Variable'], axis = 1)
nhanes_full = nhanes_full.drop(var_full_pri_2['Variable'], axis = 1)
nhanes_full = nhanes_full.drop(var_full_pri_3['Variable'], axis = 1)

#Save data file 
nhanes_full.to_pickle('../Data/nhanes_full_pre_proc.pkl')










