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
nhanes_full['PF_OTHER_TOT'] = nhanes_full['PF_TOTAL'] - nhanes_full['PF_MPS_TOTAL'] - nhanes_full['PF_SEAFD_TOT']

#Create a list of the high level food components, as defined in the FPED
#Fruit, Vegetables, Grains, Protein Foods, and Dairy components
food_cmp_level1 = [
    'F_TOTAL',
    'V_TOTAL',
    'G_TOTAL',
    'D_TOTAL',
    'PF_SEAFD_TOT',
    'PF_TOTAL']

food_cmp_oils_fats = [
    'OILS',
    'SOLID_FATS',
    'PF_SEAFD_TOT']
    
    

#Aggregate and plot the hierarchy 1 food components for the whole seafood meal subset
#nhanes_food_cmp_hr1_sum = nhanes_full[food_cmp_level1].sum()
#nhanes_food_cmp_hr1_sum = nhanes_food_cmp_hr1_sum.sort_values(ascending=False)
#nhanes_food_cmp_hr1_sum.plot.barh(title = 'Food Components Consumed with Seafood', xlabel = 'High Level Component', ylabel = 'Quantity in Grams')

#Explore the aggregate of the main food components within the eat at home vs out groups
nhanes_full_grouped = nhanes_full.groupby('eathome')[food_cmp_level1].sum()
nhanes_full_grouped.plot.bar(title = 'FCs Consumed with Seafood: Home vs Out')

#Explore the aggregate of the oils and fats food components within the eat at home vs out groups
nhanes_oils_grouped = nhanes_full.groupby('eathome')[food_cmp_oils_fats].sum()
nhanes_oils_grouped.plot.bar(title = 'Oils Consumed with Seafood: Home vs Out')

#Explore the aggregate of the added sugars within the eat at home vs out groups
nhanes_sugars_grouped = nhanes_full.groupby('eathome')[['ADD_SUGARS', 'PF_SEAFD_TOT']].sum()
nhanes_sugars_grouped.plot.bar(title = 'Sugars Consumed with Seafood: Home vs Out')


#Define the grouping key by meal. Participant ID, Meal ID, and time of consumption
meal_key = ['SEQN', 'DR1.030Z', 'DR1.020']
nhanes_meal_num = nhanes_full.groupby(meal_key)['eathome'].sum()
sf_meals_home = nhanes_meal_num[nhanes_meal_num > 0]
sf_meals_home_count = sf_meals_home.count()
sf_meals_out = nhanes_meal_num[nhanes_meal_num == 0]
sf_meals_out_count = sf_meals_out.count()


nhanes_full_grouped_norm_0 = nhanes_full_grouped.iloc[0]/sf_meals_out_count
nhanes_full_grouped_norm_1 = nhanes_full_grouped.iloc[1]/sf_meals_home_count

nhnes_full_group_norm = pd.concat([nhanes_full_grouped_norm_0, nhanes_full_grouped_norm_1], axis=1).T
nhnes_full_group_norm.plot.bar(title = 'FCs Consumed with Seafood: Home vs Out - Normalized')


nhanes_oils_grouped_norm_0 = nhanes_oils_grouped.iloc[0]/sf_meals_out_count
nhanes_oils_grouped_norm_1 = nhanes_oils_grouped.iloc[1]/sf_meals_home_count

nhnes_oils_group_norm = pd.concat([nhanes_oils_grouped_norm_0, nhanes_oils_grouped_norm_1], axis=1).T
nhnes_oils_group_norm.plot.bar(title = 'Oils Consumed with Seafood: Home vs Out - Normalized')


nhanes_sugars_grouped_norm_0 = nhanes_sugars_grouped.iloc[0]/sf_meals_out_count
nhanes_sugars_grouped_norm_1 = nhanes_sugars_grouped.iloc[1]/sf_meals_home_count

nhnes_sugars_group_norm = pd.concat([nhanes_sugars_grouped_norm_0, nhanes_sugars_grouped_norm_1], axis=1).T
nhnes_sugars_group_norm.plot.bar(title = 'Sugars Consumed with Seafood: Home vs Out - Normalized')




