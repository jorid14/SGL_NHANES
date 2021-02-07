#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 11:12:05 2021

@author: Jorid Topi

This script reads the original NHANES .csv data file and drops the variables deemed to irrelevant
for the objectives of the analysis, using variable priority assignment lookup table.

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


#Save data file 
nhanes.to_pickle('../Data/nhanes_pre_proc.pkl')




