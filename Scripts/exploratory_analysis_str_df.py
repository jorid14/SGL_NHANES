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

'''
#Read corpora
food_type_cps= pd.read_pickle('../Data/food_type_cps.pkl')
seafood_cps = pd.read_pickle('../Data/seafood_cps.pkl')
side_dish_cps = pd.read_pickle('../Data/side_dish_cps.pkl')


#Read Seafood DF
seafood_df = pd.read_pickle('../Data/seafood_df.pkl')


#Obtain and plot frequency distribution of the side dish words
side_dish_fdist = nltk.FreqDist(side_dish_cps)
side_dish_fdist.plot(30)


#Obtain and plot frequency distribution of the seafood dish items
seafood_cps_fdist = nltk.FreqDist(seafood_df['species'])
seafood_cps_fdist.plot(30)


#Seafood type count based on species, convert to dataframe
seafood_species_count = seafood_df['species'].value_counts()
seafood_species_count = pd.DataFrame(seafood_species_count)


#Group by species, description
seafood_species_desc = seafood_df.groupby(['species', 'DESCRIPTION']).count()

#Obtain unique description count for each seafood species group
seafood_species_desc_count = seafood_df.groupby('species')['DESCRIPTION'].nunique().sort_values(ascending=False)

#Join the frames to have unique species count and unique description in one table
seafood_species_count = seafood_species_count.join(seafood_species_desc_count, how='outer')
#Sort by species count, rename columns
seafood_species_count = seafood_species_count.sort_values(by = 'species', ascending=False)
seafood_species_count = seafood_species_count.rename(columns={"Index": "species", "species": "species_count", "DESCRIPTION": "unique_description_count"})

'''
'''
Find the number of instances of the words "and" and "with" in each description item.
Convert to dataframe join with seafood dataframe and then join with the seafood count 
table to form a tally. Save the table as .csv
'''
'''
seafood_description_contains_with = seafood_df['DESCRIPTION'].str.count(' with ')
seafood_description_contains_with = pd.DataFrame(seafood_description_contains_with)
seafood_description_contains_with = seafood_description_contains_with.rename(columns={"DESCRIPTION": "contains_with_count"})

seafood_description_contains_and = seafood_df['DESCRIPTION'].str.count(' and ')
seafood_description_contains_and = pd.DataFrame(seafood_description_contains_and)
seafood_description_contains_and = seafood_description_contains_and.rename(columns={"DESCRIPTION": "contains_and_count"})

seafood_description_contains_with = seafood_description_contains_with.join(seafood_df, how='outer')
seafood_description_contains_with = seafood_description_contains_with.groupby(['species'])['contains_with_count'].agg('sum')
seafood_description_contains_with = pd.DataFrame(seafood_description_contains_with)

seafood_description_contains_and = seafood_description_contains_and.join(seafood_df, how='outer')
seafood_description_contains_and = seafood_description_contains_and.groupby(['species'])['contains_and_count'].agg('sum')
seafood_description_contains_and = pd.DataFrame(seafood_description_contains_and)

seafood_species_count.reset_index(inplace=True)
seafood_species_count = pd.merge(seafood_species_count, seafood_description_contains_with, how='left', left_on=['index'], right_on=['species'])
seafood_species_count = pd.merge(seafood_species_count, seafood_description_contains_and, how='left', left_on=['index'], right_on=['species'])

seafood_species_count.to_csv('../Data/seafood_species_count.csv')
seafood_df['DESCRIPTION'][(seafood_df.DR1I_PF_SEAFD_TOT > 0) & (seafood_df.species == 'seafood')].to_csv('../Data/seafood_description.csv')
seafood_df.to_csv('../Data/seafood_df.csv')


tokenizer = nltk.RegexpTokenizer(r"\w+")

new_words = []
for index, row in seafood_df.iterrows():
    new_words_temp = tokenizer.tokenize(seafood_df['DESCRIPTION'][index])
    for i in new_words_temp:
        new_words.append(i)
        
counts = Counter(new_words)
print(counts)

#counts = pd.DataFrame(counts)
counts = dict(counts)
df = pd.DataFrame.from_dict(counts, orient = 'index')
df = df.sort_values(by = 0, ascending=False)
    
df.to_csv('../Data/counts.csv')    
'''

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




side_dish_count[3:].plot.bar(x='SD_Num', y='pct', rot=90)
meal_sf_count[4:].plot.bar(x='SF_Num', y='pct', rot=90)







