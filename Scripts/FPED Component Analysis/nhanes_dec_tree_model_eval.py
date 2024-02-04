#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jorid Topi

This script defines a decision tree model and fits the NHANES data to it.
The model is evaluated over several runs.
The output products for the final report are generated here.
"""


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.tree import export_text


def tree_regressor(df, components, n_sfd, n_non_sfd, r_seed):
    '''
    Decision Tree fit. Performs the random sampling among the classes, creating a balanced
    training data set. 
    
    Returns the success rate for the training and test data sets. Also returns the tree rules 
    from each fit.
    '''
    df_non_sfd = df[df['seafood_meal']==0].sample(n=n_non_sfd, random_state = r_seed)
    df_sfd = df[df['seafood_meal']==1].sample(n=n_sfd, random_state = r_seed)
    df = pd.concat([df_non_sfd, df_sfd])
    df_x = df[components]
    df_y = df['seafood_meal']
    X_train, X_test, y_train, y_test = train_test_split(df_x, df_y, test_size=0.2, random_state = r_seed)
    decision_tree = DecisionTreeClassifier()
    decision_tree.fit(X_train, y_train)
    y_pred_tree = decision_tree.predict(X_test)
    y_pred_tree_train = decision_tree.predict(X_train)
    score = accuracy_score(y_test, y_pred_tree)
    score_train = accuracy_score(y_train, y_pred_tree_train)
    tree_rules = export_text(decision_tree, feature_names=list(X_train.columns))
    return score, score_train, tree_rules


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
Evaluation of the decision tree model, using all components.
Reproducible with same random seed over 100 runs
'''

tree_score_test = []
tree_score_train = []
for i in range(100):
    model_fit, train_results, tree_rules = tree_regressor(df, fped_components, 1000, 1000, r_seed=i)
    tree_score_test.append(model_fit)
    tree_score_train.append(train_results)

tree_score_test = pd.DataFrame(tree_score_test)
tree_score_train = pd.DataFrame(tree_score_train)


'''
Model test score distribution: Generates histogram and saves to figure
'''
ax = tree_score_test.plot.hist(title = 'Decision Tree: Test Score')
fig = ax.get_figure()
fig.savefig('../../Figures/Tree_Test_Score.png')
fig.clf()


'''
Model training score distribution: Generates histogram and saves to figure
'''
ax = tree_score_train.plot.hist(title = 'Decision Tree: Train Score')
fig = ax.get_figure()
fig.savefig('../../Figures/Tree_Train_Score.png')
fig.clf()


