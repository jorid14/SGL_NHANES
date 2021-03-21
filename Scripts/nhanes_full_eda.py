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



nhanes_full.columns = nhanes_full.columns.str.replace('^DR1I_', '')

nhanes_full_fped = nhanes_full[fped_cols]

nhanes_full_cmp = nhanes_full[fped_cols_cmp]
nhanes_full_tot = nhanes_full[fped_cols_tot]


nhanes_full_cmp_sum = nhanes_full_cmp.sum()
nhanes_full_tot_sum = nhanes_full_tot.sum()

nhanes_full_cmp_sum = nhanes_full_cmp_sum.sort_values(ascending=False)
nhanes_full_tot_sum = nhanes_full_tot_sum.sort_values(ascending=False)


nhanes_full_cmp_sum.head(15).plot.barh()
nhanes_full_tot_sum.plot.barh()


