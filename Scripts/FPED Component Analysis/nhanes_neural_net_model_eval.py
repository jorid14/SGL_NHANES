#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jorid Topi

This script defines a simple neural network deep learning model and fits the NHANES data to it.
The model is evaluated over 1000 epochs.
The output products for the final report are generated here.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from tensorflow import keras
import matplotlib.pyplot as plt


#Read the pre-processed data
df = pd.read_csv('../../Data/nhanes_full_pre_proc.csv')

#Define the FPED components to be used for the fit. Uses the lowest level FPED components.
#Excludes meat and fish proteins
fped_components = ['F_CITMLB', 'F_OTHER', 'F_JUICE', 
                   'V_DRKGR', 'V_REDOR_TOMATO', 'V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'V_LEGUMES', 
                   'G_WHOLE','G_REFINED', 
                   'PF_EGGS', 'PF_SOY', 'PF_NUTSDS', 
                   'D_MILK', 'D_YOGURT', 'D_CHEESE', 
                   'OILS', 'SOLID_FATS', 'ADD_SUGARS', 'A_DRINKS']  

#Sample the training data equally among the two classes
df_non_sfd = df[df['seafood_meal']==0].sample(n=1000)
df_sfd = df[df['seafood_meal']==1].sample(n=1000)
df = pd.concat([df_non_sfd, df_sfd])
X = df[fped_components]
Y = df['seafood_meal']

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

#Create a 7 layer neural network and compile
model = keras.models.Sequential([
    keras.layers.Dense(536, activation="relu"),
    keras.layers.Dense(184, activation="relu"),
    keras.layers.Dense(368, activation="relu"),
    keras.layers.Dense(184, activation="relu"),
    keras.layers.Dense(92, activation="relu"),
    keras.layers.Dense(46, activation="relu"),
    keras.layers.Dense(23, activation="relu"),
    keras.layers.Dense(2, activation="softmax")
])

#Compile the neural network defined above
model.compile(loss="sparse_categorical_crossentropy",
              optimizer="sgd",
              metrics=["accuracy"])

#Fit the model with 1000 epochs and save the training history data
history = model.fit(X_train, y_train, epochs=1000,
                    validation_data=(X_test, y_test))


#Plot the training history data and save the figure
pd.DataFrame(history.history).plot(figsize=(8, 5))
plt.grid(True)
plt.gca().set_ylim(0, 1)
plt.title('Neural Network History: 7 Hidden Layers')
plt.savefig('../../Figures/Neural_Net.png')

