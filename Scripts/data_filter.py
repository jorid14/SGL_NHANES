#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 10:05:56 2021

@author: Jorid Topi

This is the priority 1 data pipeline, which is used for the primary objectives of the analysis.
The variable analysis lookup is used to keep only the variables that were identified as useful
for this analysis. The priority 2 and 3 variables are dropped.

The meals that do not include seafood are then filtered out of the dataframe.

"""

import pandas as pd

#Read output of first data cleanup
nhanes = pd.read_pickle('../Data/nhanes_pre_proc.pkl')


#Use the variable lookup to filter out variables for reducing the dataset
variable_lookup = pd.read_csv('../Analysis/Variable_Analysis_Lookup.csv')

#Pull out the priority 2 and 3 variables, which are dropped in this pipeline
var_pri_2 = variable_lookup[variable_lookup['Priority'] == 2]
var_pri_3 = variable_lookup[variable_lookup['Priority'] == 3]


#Drop the priority 2 and 3 variables
nhanes = nhanes.drop(var_pri_2['Variable'], axis = 1)
nhanes = nhanes.drop(var_pri_3['Variable'], axis = 1)


#Obtain dataframe with seafood items
seafood_df = nhanes[nhanes['DR1I_PF_SEAFD_TOT'] > 0]

#Define the dataframe join key for pulling other food items consumed with seafood
join_key = ['SEQN', 'DR1.030Z', 'DR1.020']

#Obtain priority 1 variables from lookup, place them in a list
var_pri_1 = variable_lookup[variable_lookup['Priority'] == 1]
var_list = var_pri_1['Variable'].tolist()

#Create variables to be dropped after the table join from priority 1
drop_vars = [x for x in var_list if x not in join_key]
string = '_x'
drop_vars = [x + string for x in drop_vars]


#Join in the other food items consumed with seafood, based on the defined key
nhanes = pd.merge(seafood_df, nhanes, how='left', on=join_key)
#Drop the left table variables, since left table is only used for filtering
nhanes = nhanes.drop(drop_vars, axis = 1)
#Drop additional unnecessary variables
nhanes = nhanes.drop(['Unnamed: 0_x', 'Unnamed: 0_y'], axis = 1)
#Strip the _y suffix from column names
nhanes.columns = nhanes.columns.str.rstrip('_y')



#Save pipeline output
nhanes.to_pickle('../Data/nhanes_filtered.pkl')



