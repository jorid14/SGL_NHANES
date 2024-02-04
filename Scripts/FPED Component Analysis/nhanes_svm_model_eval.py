#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jorid Topi

This script defines a SVM model and fits the NHANES data to it.
The model is evaluated over several runs.
The output products for the final report are generated here.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

def svm_regressor(df, variables, n_sfd, n_non_sfd, param, r_seed):
    '''
    SVM fit. Performs the random sampling among the classes, creating a balanced
    training data set. 
    
    Returns the success rate for the training and test data sets.
    '''
    df_non_sfd = df[df['seafood_meal']==0].sample(n=n_non_sfd, random_state = r_seed)
    df_sfd = df[df['seafood_meal']==1].sample(n=n_sfd, random_state = r_seed)
    df = pd.concat([df_non_sfd, df_sfd])
    X = df[variables]
    Y = df['seafood_meal']
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state = r_seed)
    svm_nhanes = Pipeline([
        ("scaler", StandardScaler()),
        ("linear_svc", LinearSVC(C=param, loss="hinge"))
    ])
    svm_nhanes.fit(X_train, y_train)
    y_pred_svm = svm_nhanes.predict(X_test)
    score = accuracy_score(y_test, y_pred_svm)
    y_pred_svm_train = svm_nhanes.predict(X_train)
    score_train = accuracy_score(y_train, y_pred_svm_train)
    return score, score_train


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

'''
Evaluation of the SVM model, using all components.
Reproducible with same random seed over 100 runs
'''

svm_score_test = []
svm_score_train = []
for i in range(100):
    model_fit, train_result = svm_regressor(df, fped_components, 1000, 1000, 1, r_seed=i)
    svm_score_test.append(model_fit)
    svm_score_train.append(train_result)

svm_score_test = pd.DataFrame(svm_score_test)
svm_score_train = pd.DataFrame(svm_score_train)

'''
Model test score distribution: Generates histogram and saves to figure
'''

ax = svm_score_test.plot.hist(title = 'SVM: Test Score')
fig = ax.get_figure()
fig.savefig('../../Figures/SVM_Test_Score.png')
fig.clf()

'''
Model training score distribution: Generates histogram and saves to figure
'''

ax = svm_score_train.plot.hist(title = 'SVM: Train Score')
fig = ax.get_figure()
fig.savefig('../../Figures/SVM_Train_Score.png')
fig.clf()