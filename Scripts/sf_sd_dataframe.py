#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  7 08:39:16 2021

@author: jori
"""

import pandas as pd
import re



#Read the structured dataframe
df_final = pd.read_pickle('../Data/df_final.pkl')
df_final_cols = df_final.columns.values.tolist()

#Create a list of all the "SFx" columns, where x is a digit. This pulls in the columns containing the 
#seafood type from the structured database. 
#The regular expression looks for two digits after "SF" first, then it looks for one digit. 
#This will only work for SF0-SF99, and will break if there are more than 99 seafood dishes in one meal (unlikely)
sf_cols = []
for i in range(len(df_final_cols)):
    if (re.match(r"SF\d\d", df_final_cols[i])):
        sf_cols.append(re.findall(r"SF\d\d", df_final_cols[i])[0])
    elif (re.match(r"SF\d", df_final_cols[i])):
        sf_cols.append(re.findall(r"SF\d", df_final_cols[i])[0])
 
#Create a list of all the "SDx" columns, where x is a digit. This pulls in the columns containing the 
#side dish type from the structured database. 
#The regular expression looks for three digits after "SD" first, then it looks for two digits, then one. 
#This will only work for SD0-SD999, and will break if there are more than 999 seafood side dishes in one meal (unlikely)
sd_cols = []
for i in range(len(df_final_cols)):
    if (re.match(r"SD\d\d\d", df_final_cols[i])):
        sd_cols.append(re.findall(r"SD\d\d\d", df_final_cols[i])[0])
    elif (re.match(r"SD\d\d", df_final_cols[i])):
        sd_cols.append(re.findall(r"SD\d\d", df_final_cols[i])[0])
    elif (re.match(r"SD\d", df_final_cols[i])):
        sd_cols.append(re.findall(r"SD\d", df_final_cols[i])[0])

#Create the seafood to side dish associations by sequentially melting the dataframe, pivoting on each SF column
df_sf_to_sd = pd.DataFrame()
#Loop over the SF columns to pivot the associations
for i in sf_cols:
    #Temporary storage of the Df columns. The columns will be used to filter the DF
    #This line is used to reset at start of loop.
    df_cols_temp = [] 
    #Append the DF columns with the SD columns
    for j in range(len(sd_cols)):
        df_cols_temp.append(sd_cols[j]) 
    #Append the DF columns with the SF pivot column
    df_cols_temp.append(i)
    #Include only SF pivot column and all SD columns
    df_temp = df_final[df_cols_temp]
    #Melt the dataframe by the SF pivot column
    df_temp = pd.melt(df_temp, id_vars=i)
    #Rename the the SF pivot column to a common name to be used in all loop iterations
    #Rename variable to the sd_n, to indicate the number of side dishes for the seafod type
    df_temp.rename({i: 'sf_type', 'variable': 'sd_n', 'value': 'sd_name'}, axis=1, inplace=True)
    #Append the result of each loop to the final dataframe
    df_sf_to_sd = df_sf_to_sd.append(df_temp) 
    df_sf_to_sd = df_sf_to_sd.reset_index(drop=True)
    
#Remove rows that are NaN
df_sf_to_sd = df_sf_to_sd[df_sf_to_sd['sf_type'].notna()]
df_sf_to_sd = df_sf_to_sd[df_sf_to_sd['sd_name'].notna()]

df_sf_to_sd.to_pickle('../Data/df_sf_to_sd.pkl')



