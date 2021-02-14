#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 14:15:14 2021

@author: Jorid Topi

This script performs the data structuring tasks as identified by the project objectives


"""

import pandas as pd
import re


#Read filtered dataframe
nhanes = pd.read_pickle('../Data/nhanes_post.pkl')


#Obtain dataframe with seafood items
seafood_df = nhanes[nhanes['DR1I_PF_SEAFD_TOT'] > 0]
#Obtain dataframe with side dishes
side_dish_df = nhanes[nhanes['DR1I_PF_SEAFD_TOT'] == 0]

"""
Obtain initial test corpus for the whole meal, seafood item only, and side dishes only
Obtains the first word in the text description string before a comma, if comma exists.
Obtains the whole string in the text description if comma is not present.
"""
food_type_cps = nhanes['DESCRIPTION'].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)
seafood_cps = seafood_df['DESCRIPTION'].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)
side_dish_cps = side_dish_df['DESCRIPTION'].apply(lambda x: re.search(r'^([^,])+', x).group(0) if re.search((r','), x) else x)


"""
Create a dataframe that joins the seafood corpus with seafood df
"""
seafood_cps_key = pd.DataFrame(seafood_cps)
seafood_cps_key.columns = ['Seafood_CPS']
seafood_df = seafood_df.join(seafood_cps_key, how='outer')


#Save pipeline output
food_type_cps.to_pickle('../Data/food_type_cps.pkl')
seafood_cps.to_pickle('../Data/seafood_cps.pkl')
side_dish_cps.to_pickle('../Data/side_dish_cps.pkl')
seafood_df.to_pickle('../Data/seafood_df.pkl')
