#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 11:24:48 2021

@author: jori
"""
import pandas as pd
import re

#Read the structured dataframe
df_sf_to_sd = pd.read_pickle('../Data/df_sf_to_sd.pkl')


#Obtain number of unique side dishes for each seafood type
sf_type_unq_sd = df_sf_to_sd.groupby('sf_type')['sd_name'].nunique().sort_values(ascending=False)

#Obtain association statistics for the unique seafood species
sf_to_sd_num = df_sf_to_sd.groupby(['sf_type','sd_name']).size().reset_index(name='count').sort_values(by = 'count', ascending=False)

#Calculates the side dish total count for each seafood type, merges to association df
sd_tot = sf_to_sd_num.groupby('sf_type')['count'].sum()
sf_to_sd_num = pd.merge(sf_to_sd_num, sd_tot, how='left', on=['sf_type'])
#Calculate percetange of each side type as proportion to total side dishes for each seafood type
sf_to_sd_num['pct'] = (sf_to_sd_num['count_x']/sf_to_sd_num['count_y'])*100
#Sort by highest percentage
sf_to_sd_num = sf_to_sd_num.sort_values(by=['pct'], ascending=False)


#df_sf_to_sd2.to_json('../Data/df_sf_to_sd.json')

