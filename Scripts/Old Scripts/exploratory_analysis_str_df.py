#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 14:15:14 2021

@author: Jorid Topi

This script performs the data structuring tasks as identified by the project objectives


"""

import pandas as pd
import nltk
from collections import Counter


df = pd.read_pickle('../Data/df_final.pkl')


#Obtain only required variables
meal_key = ['SEQN', 'DR1.030Z', 'DR1.020']

#List of side dish columns for isolating side dishes
side_dish_column_list = ['SD1', 'SD2', 'SD3', 'SD4', 'SD5', 'SD6', 'SD7', 'SD8', 
                         'SD9', 'SD10', 'SD11', 'SD12', 'SD13', 'SD14', 'SD15', 
                         'SD16', 'SD17', 'SD18', 'SD19', 'SD20', 'SD21', 'SD22']


#Isolate the side dish subset for analysis
#Obtain the side dish and meal key columns
side_dish_subset = df[meal_key + side_dish_column_list]
#Obtain count of side dish item in each column. This can be used as a statistic to describe
#the number of side dishes per meal.
side_dish_count = side_dish_subset.count()
#Melt the df on meal
sd_melted = pd.melt(side_dish_subset, id_vars=meal_key)
#Remove rows that are NaN
side_dish_subset = sd_melted[sd_melted['value'].notna()]
#Obtain and plot frequency distribution of the side dish words
side_dish_fdist = nltk.FreqDist(side_dish_subset['value'])
side_dish_fdist.plot(30)


#List of side dish columns for isolating seafood items
sf_column_list = ['SF1', 'SF2', 'SF3', 'SF4', 'SF5', 'SF6', 'SF7']
#Isolate the seafood subset for analysis
#Obtain the seafood item and meal key columns
side_dish_subset = df[meal_key + sf_column_list]
#Obtain the seafood item count in each column. Result can be used as a statistic to count
#the number of seafood species per meal
meal_sf_count = side_dish_subset.count()



#List of seafood item description columns for isolating seafood item descriptions
sf_desc_column_list = ['SFD1', 'SFD2', 'SFD3', 'SFD4', 'SFD5', 'SFD6', 'SFD7', 'SFD8', 'SFD9']
sf_desc_subset = df[meal_key + sf_desc_column_list]


sf_desc_melted = pd.melt(sf_desc_subset, id_vars=meal_key)
sf_desc_subset = sf_desc_melted[sf_desc_melted['value'].notna()]


#Build tokenizer for finding unique words
tokenizer = nltk.RegexpTokenizer(r"\w+")

#Obtain a list of all the words in the seafood item descriptions
new_words = []
for index, row in sf_desc_subset.iterrows():
    new_words_temp = tokenizer.tokenize(sf_desc_subset['value'][index])
    for i in new_words_temp:
        new_words.append(i)
        
#Obtain word count and arrange by descending order
sf_desc_wrd_counts = nltk.FreqDist(new_words)
sf_desc_wrd_counts.plot(40)


    
#Obtain the seafood item counts per meal as a percentage of seafood meals
meal_sf_count = meal_sf_count.apply(pd.Series)
meal_sf_count = meal_sf_count.rename({0: 'Count'}, axis=1)
#meal_sf_count.reset_index(level=0, inplace=True)
meal_sf_count["pct"] = (meal_sf_count["Count"] / meal_sf_count.iloc[0][0]) * 100
meal_sf_count['SF_Num'] = meal_sf_count.index


#Obtain the side dish item counts per meal as a percentage of seafood meals
side_dish_count = side_dish_count.apply(pd.Series)
side_dish_count = side_dish_count.rename({0: 'Count'}, axis=1)
#side_dish_count.reset_index(level=0, inplace=True)
side_dish_count["pct"] = (side_dish_count["Count"] / side_dish_count.iloc[0][0]) * 100
side_dish_count['SD_Num'] = side_dish_count.index



#Plot the side dish count and seafood item count as percentage of total seafood meals
side_dish_count[3:].plot.bar(x='SD_Num', y='pct', rot=90)
meal_sf_count[4:].plot.bar(x='SF_Num', y='pct', rot=90)



#Obtain a table of all the side dish extracted names and their counts per meal
item = []
item_count = []
for k,v in side_dish_fdist.items():
    item.append(k)
    item_count.append(v)

side_dish_fdist_table = pd.DataFrame(item_count, item, columns=['Count'])  
side_dish_fdist_table = side_dish_fdist_table.sort_values('Count', ascending = False)
#side_dish_fdist_table.to_csv('../Data/side_dish_fdist_table.csv')


