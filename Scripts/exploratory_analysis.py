#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 14:15:14 2021

@author: Jorid Topi

This script performs the data structuring tasks as identified by the project objectives


"""

import pandas as pd
import nltk



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
Find the number of instances of the words "and" and "with" in each description item.
Convert to dataframe join with seafood dataframe and then join with the seafood count 
table to form a tally. Save the table as .csv
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
seafood_df['DESCRIPTION'][(seafood_df.species == 'seafood')].to_csv('../Data/seafood_description.csv')

