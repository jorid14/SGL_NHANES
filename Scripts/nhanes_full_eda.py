#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script performs the initial EDA for the NHANES_full dataset

"""

import pandas as pd
import re

#Read the structured dataframe
nhanes_full = pd.read_pickle('../Data/nhanes_full_filtered.pkl')
nhanes_full_cols = nhanes_full.columns.values.tolist()


#Create a list of all the FPED columns, removing the "DR1I_" prefix. 
fped_cols = []
for i in range(len(nhanes_full_cols)):
    if (re.match(r"DR1I_", nhanes_full_cols[i])):
        fped_cols.append(re.findall(r"DR1I_(.*)", nhanes_full_cols[i])[0])
        
fped_cols_tot = []
fped_cols_cmp = []
for i in range(len(fped_cols)):
    if (re.search(r"_TOT", fped_cols[i])):
        fped_cols_tot.append(fped_cols[i])
    else: fped_cols_cmp.append(fped_cols[i])


#Remove the "DR1I_" prefix for simplification
nhanes_full.columns = nhanes_full.columns.str.replace('^DR1I_', '')
#Create a protein other total item, that excludes meats and seafood. Meant to capture
#other protein sources at a higher level
nhanes_full['PF_OTHER_TOT'] = nhanes_full['PF_TOTAL'] - nhanes_full['PF_MEAT_TOT'] - nhanes_full['PF_SEAFD_TOT']

#Create a list of the hierarchy 1 food components, for a higher level analysis
food_cmp_hr1 = [
'F_TOTAL',
'V_TOTAL',
'G_TOTAL',
'D_TOTAL',
'PF_OTHER_TOT',
'PF_MEAT_TOT',
'PF_SEAFD_TOT']

#Aggregate and plot the hierarchy 1 food components for the whole seafood meal subset
nhanes_food_cmp_hr1_sum = nhanes_full[food_cmp_hr1].sum()
nhanes_food_cmp_hr1_sum = nhanes_food_cmp_hr1_sum.sort_values(ascending=False)
nhanes_food_cmp_hr1_sum.plot.barh(title = 'Food Components Consumed with Seafood', xlabel = 'High Level Component', ylabel = 'Quantity in Grams')

#Explore the aggregate of the hierarchy 1 food components within the eat at home vs out groups
nhanes_full_grouped = nhanes_full.groupby('eathome')[food_cmp_hr1].sum()
nhanes_full_grouped.plot.bar(title = 'Food Components Consumed with Seafood: Home vs Out')
    

