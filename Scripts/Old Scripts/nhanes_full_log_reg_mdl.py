#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 11:59:31 2021

@author: Jorid Topi
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import linear_model
from itertools import combinations
import numpy as np
import scipy.stats as stat
import sys
import time 
import regex as re

def nhanes_full_log_reg(df, fped_vars, non_sfd_class_n, sfd_class_n, test_ratio):
    
    #Sample the seafood and non-seafood classes, create model input df
    df_non_sfd = df[df['seafood_meal']==0].sample(n=non_sfd_class_n)
    df_sfd = df[df['seafood_meal']==1].sample(n=sfd_class_n)
    df_mdl = pd.concat([df_non_sfd, df_sfd])
    #Add the classification target variable to the df input list
    fped_vars.append('seafood_meal')
    #Use variable combination selected by loop
    df_mdl = df_mdl[fped_vars]
    #Split the training and test data
    X_train, X_test, y_train, y_test = train_test_split(df_mdl.drop(['seafood_meal'], axis=1), df_mdl['seafood_meal'], test_size=test_ratio)
    #Fit the logistic regression model
    log_reg = LogisticRegression()
    log_reg.fit(X_train, y_train)
    #Obtain predictions on test set and calculate success rate
    y_pred = log_reg.predict(X_test)
    n_correct = sum(y_pred == y_test)
    pred_sr = [str(n_correct/len(y_pred))]
    #Calculate model execution time for combinatorial variable selection    
    #non_cmb_time = time.time() - startTime  
    #non_cmb_time_df = pd.DataFrame([non_cmb_time ])
    #non_cmb_time_df = non_cmb_time_df.rename({0: 'Runtime(Seconds)'}, axis=1)
    #Create a dataframe with variables used and their success rate    
    pred_sr_df = pd.DataFrame(pred_sr)
    pred_sr_df = pred_sr_df.rename({0: 'Success Rate'}, axis=1)
    fped_vars.remove('seafood_meal')
    var_list_df = pd.DataFrame([fped_vars])
    #model_result = pd.concat([var_list_df, pred_sr_df, non_cmb_time_df], axis=1)
    model_result = pd.concat([var_list_df, pred_sr_df], axis=1)
    return model_result


#Level 5 has all components of level4, but breaks the total fruit into subcomponents
food_cmp_level5 = ['F_CITMLB', 'F_OTHER', 'F_JUICE', 
                   'V_DRKGR', 'V_REDOR_TOMATO', 'V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'V_LEGUMES', 
                   'G_WHOLE','G_REFINED', 
                   'PF_EGGS', 'PF_SOY', 'PF_NUTSDS', 'PF_LEGUMES', 
                   'D_MILK', 'D_YOGURT', 'D_CHEESE', 
                   'OILS', 'SOLID_FATS', 'ADD_SUGARS', 'A_DRINKS']  



#Read the pre-processed dataframe.
df = pd.read_csv('../Data/nhanes_full_pre_proc.csv')
#df = df[(df['meal_energy']=='Low')]
#df = df[df['eathome']==1]
#df = df[df['age']>18]


'''
Combinations to try:
    
    - Age factor: (1) Keep only adults (2) Keep whole population
    - Meal size: Try all 4 meal size category combinations
    - Eat home: Meals at home, meals out, all meals
    - Seafood meal threshold: (1) Keep old option (2) Re-categorize meals with both
    - Vegetarian option: (1) Include all (2) Exclude vegeterian meals

'''

def df_filter(df, age , eathome, meal_size_low, meal_size_med_low, meal_size_med_high, meal_size_high):
    if (age == True):
        df = df[df['age'] >= 18]
    if (eathome == True):
        df = df[df['eathome']==1]
    if (meal_size_low == True & meal_size_med_low == False & meal_size_med_high == False & meal_size_high == False):
        df = df[(df['meal_energy']=='Low')]
    elif (meal_size_low == False & meal_size_med_low == True & meal_size_med_high == False & meal_size_high == False):
        df = df[(df['meal_energy']=='Medium-Low')]
    elif (meal_size_low == False & meal_size_med_low == False & meal_size_med_high == True & meal_size_high == False):
        df = df[(df['meal_energy']=='Medium-High')]
    elif (meal_size_low == False & meal_size_med_low == False & meal_size_med_high == False & meal_size_high == True):
        df = df[(df['meal_energy']=='High')]
    elif (meal_size_low == True & meal_size_med_low == True & meal_size_med_high == False & meal_size_high == False):
       df = df[(df['meal_energy']== 'Low' | df['meal_energy']=='Medium-Low')]
       print('hey')
        

    return df
    
    




sr_tot=[]
for i in range(1):
    model_res_df_x = nhanes_full_log_reg(df = df,
                                   fped_vars = food_cmp_level5, 
                                   non_sfd_class_n = 500, 
                                   sfd_class_n = 500, 
                                   test_ratio = 0.2, )
    sr_tot.append(model_res_df_x['Success Rate'][0])


sr_tot = pd.DataFrame(sr_tot)
sr_tot = sr_tot[0].astype(float)
print(sr_tot.describe())



