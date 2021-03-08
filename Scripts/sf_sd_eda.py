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

df_sf_to_sd2 = df_sf_to_sd.groupby(['sf_type','sd_name']).size().reset_index(name='count').sort_values(by = 'count', ascending=False)

df_sf_to_sd2.to_json('../Data/df_sf_to_sd.json')

