#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 10:05:56 2021

@author: Jorid Topi


"""

import pandas as pd
import re


#Read output of first data cleanup
nhanes_full = pd.read_pickle('../Data/nhanes_full_read.pkl')
nhanes_full_cols = nhanes_full.columns.values.tolist()

#Create a list of all the FPED columns, removing the "DR1I_" prefix. 
fped_cols = []
fped_cols_meal_key = []
for i in range(len(nhanes_full_cols)):
    if (re.match(r"DR1I_", nhanes_full_cols[i])):
        fped_cols.append(re.findall(r"DR1I_(.*)", nhanes_full_cols[i])[0])
        fped_cols_meal_key.append(re.findall(r"DR1I_(.*)", nhanes_full_cols[i])[0])

#Define the dataframe join key for pulling other food items consumed with seafood
meal_key = ['SEQN', 'DR1.030Z', 'DR1.020']

#Add meal key to FPED cols
fped_cols_meal_key.extend(meal_key)

#Add calories to FPED cols
fped_cols_meal_key.extend(['DR1IKCAL'])

#Remove the "DR1I_" prefix for simplification
nhanes_full.columns = nhanes_full.columns.str.replace('^DR1I_', '')


#Keep FPED cols,calories, and meal key
nhanes_full_filtered = nhanes_full[fped_cols_meal_key]
#Add calories to aggregated variables
fped_cols.extend(['DR1IKCAL'])
#Group by meal key and aggregate on FPED columns
nff_agg = nhanes_full_filtered.groupby(meal_key)[fped_cols].sum()

#Create dataframe that contains the eathome variable
df_eathome_key = ['SEQN', 'DR1.030Z', 'DR1.020', 'eathome']
df_eathome = nhanes_full[df_eathome_key]
#Group by unique meal and aggregate the eathome column
df_eathome = df_eathome.groupby(meal_key, as_index=False)['eathome'].sum()
#If eathome was 0, remains 0. Otherwise, convert it to 1
df_eathome['eathome'] = (df_eathome['eathome'] >= 1).astype(int)


#Merge in the eathome variable
df_final = nff_agg.merge(df_eathome, how='left', on=meal_key)


#Determine if the meal has seafood in it. If yes, variable = 1, 0 otherwise
df_final['seafood_meal'] = (df_final['PF_SEAFD_TOT'] >= 1).astype(int)


#Create meal name variable based on lookup, mapping from CDC source
meal_name_lookup = {1: 'Breakfast', 2: 'Lunch', 3: 'Dinner', 4: 'Supper', 5:'Brunch', 6:'Snack',
                    7: 'Drink', 8: 'Infant Feeding', 9: 'Extended consumption', 10: 'Desayano',
                    11: 'Almuerzo', 12: 'Comida', 13: 'Merienda', 14: 'Cena',15: 'Enter comida',
                    16: 'Botana', 17: 'Bocadillo', 18: 'Tentempie', 19:'Bebida', 91: 'Other'}

#Add meal name to dataframe
df_final['Meal_Name'] = df_final['DR1.030Z'].map(meal_name_lookup)

#Obtain the meals of interest
meal_name_filter = ['Lunch', 'Dinner', 'Supper', 'Brunch', 'Almuerzo', 'Comida', 'Cena', 'Enter comida']

#Keep only the meals of interest
df_final = df_final[df_final['Meal_Name'].isin(meal_name_filter)]

#Save pre-processed data
df_final.to_pickle('../Data/nhanes_full_pre_proc.pkl')
df_final.to_csv('../Data/nhanes_full_pre_proc.csv')
