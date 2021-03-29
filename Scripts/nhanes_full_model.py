#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 20:10:11 2021

@author: jori
"""


from sklearn import linear_model
import numpy as np
import scipy.stats as stat

class LogisticReg:
    """
    Wrapper Class for Logistic Regression which has the usual sklearn instance 
    in an attribute self.model, and pvalues, z scores and estimated 
    errors for each coefficient in 
    
    self.z_scores
    self.p_values
    self.sigma_estimates
    
    as well as the negative hessian of the log Likelihood (Fisher information)
    
    self.F_ij
    """
    
    def __init__(self,*args,**kwargs):#,**kwargs):
        self.model = linear_model.LogisticRegression(*args,**kwargs)#,**args)

    def fit(self,X,y):
        self.model.fit(X,y)
        #### Get p-values for the fitted model ####
        denom = (2.0*(1.0+np.cosh(self.model.decision_function(X))))
        denom = np.tile(denom,(X.shape[1],1)).T
        F_ij = np.dot((X/denom).T,X) ## Fisher Information Matrix
        Cramer_Rao = np.linalg.inv(F_ij) ## Inverse Information Matrix
        sigma_estimates = np.sqrt(np.diagonal(Cramer_Rao))
        z_scores = self.model.coef_[0]/sigma_estimates # z-score for eaach model coefficient
        p_values = [stat.norm.sf(abs(x))*2 for x in z_scores] ### two tailed test for p-values
        
        self.z_scores = z_scores
        self.p_values = p_values
        self.sigma_estimates = sigma_estimates
        self.F_ij = F_ij




import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

df = pd.read_pickle('../Data/nhanes_full_pre_proc.pkl')


#Create a list of the high level food components, as defined in the FPED
#Fruit, Vegetables, Grains, Protein Foods, and Dairy components
food_cmp_level1 = [
    'F_TOTAL',
    'V_TOTAL',
    'G_TOTAL',
    'D_TOTAL',
    'seafood_meal']

food_cmp_oils_fats = [
    'OILS',
    'SOLID_FATS',
    'PF_SEAFD_TOT']

pvs = []
log1_pred_sr = []

for i in range(10):
    df_non_sfd = df[df['seafood_meal']==0].sample(frac=0.061480111199528745)
    df_sfd = df[df['seafood_meal']==1]
    df = pd.concat([df_non_sfd, df_sfd])
    
    df = df[food_cmp_level1]
    
    X_train, X_test, y_train, y_test = train_test_split(df.drop(['seafood_meal'], axis=1), df['seafood_meal'], test_size=0.2)
    
    
    log_reg = LogisticReg()
    log_reg.fit(X_train, y_train)
    
    log_reg1 = LogisticRegression()
    log_reg1.fit(X_train, y_train)
    
    
    y_pred = log_reg1.predict(X_test)
    n_correct = sum(y_pred == y_test)
    sr = n_correct/len(y_pred)
    log1_pred_sr.append(sr)
    
    pvs.append(log_reg.p_values)
    df = pd.read_pickle('../Data/nhanes_full_pre_proc.pkl')


df_train = pd.concat([X_train, y_train], axis=1)
#df_train['V_TOTAL'].hist(by=df_train['seafood_meal'], bins=150)
#df_train['G_TOTAL'].hist(by=df_train['seafood_meal'], bins=150)
#df_train['D_TOTAL'].hist(by=df_train['seafood_meal'], bins=150)
#df_train['F_TOTAL'].hist(by=df_train['seafood_meal'], bins=150)

pvs_df = pd.DataFrame(pvs)
pvs_df.columns = X_train.columns.values.tolist()
log1_pred_sr_df = pd.DataFrame(log1_pred_sr)
model_metrics = pd.concat([pvs_df, log1_pred_sr_df], axis=1)
model_metrics = model_metrics.rename({0:'Succes Rate'},axis=1)

#pvs_df.columns = X_train.columns.values.tolist()

#pvs_df.drop([0], axis=1).plot.line()



#v_total_plot = df_train.groupby('seafood_meal')['V_TOTAL'].plot(kind='kde',xlim=(0,3),title='V_TOTAL',legend=True)
#g_total_plot = df_train.groupby('seafood_meal')['G_TOTAL'].plot(kind='kde',xlim=(0,5),title='G_TOTAL',legend=True)
#d_total_plot = df_train.groupby('seafood_meal')['D_TOTAL'].plot(kind='kde',xlim=(0,2),title='D_TOTAL',legend=True)
#f_total_plot = df_train.groupby('seafood_meal')['F_TOTAL'].plot(kind='kde',xlim=(0,1),title='F_TOTAL',legend=True)
