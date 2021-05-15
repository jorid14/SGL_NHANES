#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jorid Topi

This script generates EDA plots of the side dish text associations with each seafood species
"""
import pandas as pd


#Read the structured dataframe
df_sf_to_sd = pd.read_pickle('../../Data/sf_to_sd_association.pkl')

#Obtain number of unique side dishes for each seafood type
sf_type_unq_sd = df_sf_to_sd.groupby('sf_type')['sd_name'].nunique().sort_values(ascending=False)

#Obtain association statistics for the unique seafood species
sf_to_sd_num = df_sf_to_sd.groupby(['sf_type','sd_name']).size().reset_index(name='count').sort_values(by = 'count', ascending=False)

#Calculates the side dish total count for each seafood type, merges to association df
sd_tot = sf_to_sd_num.groupby('sf_type')['count'].sum()
sf_to_sd_num = pd.merge(sf_to_sd_num, sd_tot, how='left', on=['sf_type'])
#Calculate percetange of each side type as proportion to total side dishes for each seafood type
sf_to_sd_num['pct'] = (sf_to_sd_num['count_x']/sf_to_sd_num['count_y'])*100
sf_to_sd_num['pct'] = sf_to_sd_num['pct'].round(decimals = 2)
#Sort by highest percentage
sf_to_sd_num = sf_to_sd_num.sort_values(by=['sf_type', 'pct'], ascending=(True, False))


sf_to_sd_num_grouped = sf_to_sd_num.groupby('sf_type')

for name,group in sf_to_sd_num_grouped:
    group = group.head(15)
    group['sf_sd_pair'] = group['sf_type'] + ' - ' + group['sd_name']
    group_plot = group.plot.barh(x='sf_sd_pair', y='pct', rot=0)
    group_plot.invert_yaxis()

