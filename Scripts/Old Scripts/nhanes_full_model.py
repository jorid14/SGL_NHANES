#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 20:10:11 2021

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
    
    source: https://gist.github.com/rspeare/77061e6e317896be29c6de9a85db301d
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



def nhanes_full_log_reg(df, fped_vars, var_combinatorial, batch_run, batch_num, 
                        batch_step, non_sfd_class_n, sfd_class_n, test_ratio, dummy_run):
    
    #Model execution start time
    startTime = time.time()
    #Create list of all FPED variable combinations if desired    
    if (var_combinatorial == True):
        cmb_output = sum([list(map(list, combinations(fped_vars , i))) for i in range(len(fped_vars ) + 1)], [])
        cmb_output = cmb_output[1:]
    else: 
        cmb_output = fped_vars

    
    if (dummy_run == True):
        cmb_output = []
        
        a=[]
        
        for i in range(len(fped_vars)):
            if (re.match(r"(.*)_high", fped_vars[i])):
                a.append(fped_vars[i])
                
           
        cmb_output = sum([list(map(list, combinations(a , i))) for i in range(len(a ) + 1)], [])
        
        
        
        #print(cmb_output)
        
        for i in range(len(cmb_output)):
            low_vars = []
            
            for j in range(len(cmb_output[i])):
                low_vars.append(cmb_output[i][j].replace('_high', '')+'_low')
            for k in range(len(low_vars)):
                cmb_output[i].append(low_vars[k])  
        
        cmb_output = cmb_output[1:]

    #Partition the list of FPED variable combinations with batch parameters, if batch run desired
    if (batch_run == True):
        #Obtain batch length and step through the indecies of the variable list
        batch_len = int(len(cmb_output)/batch_num)
        idx1 = 0 + batch_len*int(batch_step)
        idx2 = batch_len + batch_len*int(batch_step)
        cmb_output = cmb_output[idx1:idx2]

    #print(len(cmb_output))
    #This is the model fitting loop if combinatorial variable model selection is desired
    if (var_combinatorial == True):
        #Lists for storing the model prediction success rate and variable list
        pred_sr = []
        var_list = []
        #Loops through the generate variable combinations
        for var in cmb_output:
            #Sample the seafood and non-seafood classes, create model input df
            df_non_sfd = df[df['seafood_meal']==0].sample(n=non_sfd_class_n)
            df_sfd = df[df['seafood_meal']==1].sample(n=sfd_class_n)
            df_mdl = pd.concat([df_non_sfd, df_sfd])
            #Add the classification target variable to the df input list
            var.append('seafood_meal')
            #Use variable combination selected by loop
            df_mdl = df_mdl[var]
            #Split the training and test data
            X_train, X_test, y_train, y_test = train_test_split(df_mdl.drop(['seafood_meal'], axis=1), df_mdl['seafood_meal'], test_size=test_ratio)
            #Fit the logistic regression model
            log_reg = LogisticRegression()
            log_reg.fit(X_train, y_train)
            #Obtain predictions on test set and calculate success rate
            y_pred = log_reg.predict(X_test)
            n_correct = sum(y_pred == y_test)
            sr = n_correct/len(y_pred)
            #Add success rate and variables used to list for storing outside loop
            pred_sr.append(sr)
            var.remove('seafood_meal')
            var_list.append(var)
            #var_idx = cmb_output.index(var)
            #progress_pct = round(100 * var_idx / len(cmb_output), 2)
            #if (progress_pct%1==0):
            #    print("Progress: "+str(progress_pct)+" %")
            print(var)
        
        #Calculate model execution time for combinatorial variable selection    
        cmb_time = time.time() - startTime  
        cmb_time_list = [cmb_time] * len(cmb_output)
        cmb_time_df = pd.DataFrame(cmb_time_list)
        cmb_time_df = cmb_time_df.rename({0: 'Runtime(Seconds)'}, axis=1)
        #Create a dataframe with variables used, their success rate , and runtime   
        pred_sr_df = pd.DataFrame(pred_sr)
        pred_sr_df = pred_sr_df.rename({0: 'Success Rate'}, axis=1)
        var_list_df = pd.DataFrame(var_list)
        model_result = pd.concat([var_list_df, pred_sr_df, cmb_time_df], axis=1)
        
        
        
    #Condition if variable combination is not desired  
    else:
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
        non_cmb_time = time.time() - startTime  
        non_cmb_time_df = pd.DataFrame([non_cmb_time ])
        non_cmb_time_df = non_cmb_time_df.rename({0: 'Runtime(Seconds)'}, axis=1)
        #Create a dataframe with variables used and their success rate    
        pred_sr_df = pd.DataFrame(pred_sr)
        pred_sr_df = pred_sr_df.rename({0: 'Success Rate'}, axis=1)
        fped_vars.remove('seafood_meal')
        var_list_df = pd.DataFrame([fped_vars])
        model_result = pd.concat([var_list_df, pred_sr_df, non_cmb_time_df], axis=1)
    
    #Returns result from model.     
    return model_result
 

#Contains list of all FPED variable plus seafood meal classification target
all_vars = ['F_CITMLB', 'F_OTHER', 'F_JUICE', 'F_TOTAL', 
            'V_DRKGR', 'V_REDOR_TOMATO', 'V_REDOR_OTHER', 'V_REDOR_TOTAL', 
            'V_STARCHY_POTATO', 'V_STARCHY_OTHER', 'V_STARCHY_TOTAL', 'V_OTHER', 
            'V_TOTAL', 'V_LEGUMES', 
            'G_WHOLE', 'G_REFINED', 'G_TOTAL', 
            'PF_EGGS', 'PF_SOY', 'PF_NUTSDS', 'PF_LEGUMES', 
            'D_MILK', 'D_YOGURT', 'D_CHEESE', 'D_TOTAL', 
            'OILS', 'SOLID_FATS', 'ADD_SUGARS', 'A_DRINKS', 
            'seafood_meal']


#Create a list of the high level food components, as defined in the FPED
#Fruit, Vegetables, Grains, Protein Foods, and Dairy components
#Include oils, fats, and sugars at this level.
food_cmp_level1 = ['F_TOTAL','V_TOTAL','G_TOTAL','D_TOTAL','OILS', 
                   'SOLID_FATS', 'ADD_SUGARS']

food_cmp_level1x = ['F_TOTAL','V_DRKGR', 'V_REDOR_TOMATO','V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'G_TOTAL','D_TOTAL','OILS', 
                   'SOLID_FATS', 'ADD_SUGARS']

#Level 2 contains the subcomponents of vegetables, grains, and dairy 
#Keep fruits at total level
#Include oils, fats, and sugars at this level.
food_cmp_level2 = ['F_TOTAL', 
                   'V_DRKGR', 'V_REDOR_TOMATO','V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'V_LEGUMES', 
                   'G_WHOLE','G_REFINED', 
                   'D_MILK', 'D_YOGURT','D_CHEESE', 
                   'OILS', 'SOLID_FATS', 'ADD_SUGARS'] 

#Level 3 has all components from level2, 
#adding a generated total protein component other than meat and seafood
food_cmp_level3 = ['F_TOTAL', 
                   'V_DRKGR', 'V_REDOR_TOMATO','V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'V_LEGUMES', 
                   'G_WHOLE','G_REFINED', 
                   'PF_PLANT_D_TOTAL', 
                   'D_MILK', 'D_YOGURT','D_CHEESE', 
                   'OILS', 'SOLID_FATS', 'ADD_SUGARS'] 

#Level 4 has all components from level3, 
#breaking down the total protein component
food_cmp_level4 = ['F_TOTAL', 
                   'V_DRKGR', 'V_REDOR_TOMATO','V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'V_LEGUMES', 
                   'G_WHOLE','G_REFINED', 
                   'PF_EGGS', 'PF_SOY', 'PF_NUTSDS', 'PF_LEGUMES', 
                   'D_MILK', 'D_YOGURT','D_CHEESE', 
                   'OILS', 'SOLID_FATS', 'ADD_SUGARS'] 

#Level 5 has all components of level4, but breaks the total fruit into subcomponents
food_cmp_level5 = ['F_CITMLB', 'F_OTHER', 'F_JUICE', 
                   'V_DRKGR', 'V_REDOR_TOMATO', 'V_REDOR_OTHER', 'V_STARCHY_POTATO', 
                   'V_STARCHY_OTHER', 'V_OTHER', 'V_LEGUMES', 
                   'G_WHOLE','G_REFINED', 
                   'PF_EGGS', 'PF_SOY', 'PF_NUTSDS', 'PF_LEGUMES', 
                   'D_MILK', 'D_YOGURT', 'D_CHEESE', 
                   'OILS', 'SOLID_FATS', 'ADD_SUGARS', 'A_DRINKS']  

'''
#If running by script with arguments
if len(sys.argv) > 1:
    #Read the pre-processed dataframe.
    df = pd.read_csv('nhanes_full_pre_proc.csv')
    df['PF_PLANT_D_TOTAL'] = df['PF_EGGS']+df['PF_SOY']+df['PF_NUTSDS']+df['PF_LEGUMES']
    model_res_df = nhanes_full_log_reg(df = df,
                                       fped_vars = food_cmp_level1, 
                                        var_combinatorial = True, 
                                        batch_run = False, 
                                        batch_num = sys.argv[2], 
                                        batch_step = sys.argv[1], 
                                        non_sfd_class_n = 1000, 
                                        sfd_class_n = 1000, 
                                        test_ratio = 0.2)
    
    model_res_df.to_csv('model_res_df_'+sys.argv[1]+'.csv')
#If running with no script arguments    
else:
'''
'''
if (sys.argv[1] == 'L1'):
    fped_vars = food_cmp_level1
elif (sys.argv[1] == 'L2'):
    fped_vars = food_cmp_level2
elif (sys.argv[1] == 'L3'):
    fped_vars = food_cmp_level3
elif (sys.argv[1] == 'L4'):
    fped_vars = food_cmp_level4
'''
#Read the pre-processed dataframe.
df = pd.read_csv('../Data/nhanes_full_pre_proc.csv')
df = df[(df['meal_energy']=='Low')]
#df = df[df['eathome']==1]
df = df[df['age']>18]

'''
dummy_total = []
for var in food_cmp_level5:
    bins = [-np.inf, 0, np.inf]
    labels=['low','high']
    df[var] = pd.cut(df[var], bins=bins, labels=labels)
    dummies = pd.get_dummies(df[var], prefix=var)
    dummy_total.append(dummies.columns[0])
    dummy_total.append(dummies.columns[1])
    for dummy in dummies.columns:
        df[dummy] = dummies[dummy]
'''
#for var in food_cmp_level2:
#    df.loc[df[var] > 0, var] = 1
#df.loc[df['F_TOTAL'] != 'None', 'F_TOTAL'] = "Some"
#df = df[df['eathome']==1]

sr_tot=[]
for i in range(100):
    model_res_df_x = nhanes_full_log_reg(df = df,
                                   fped_vars = food_cmp_level5, 
                                    var_combinatorial = False, 
                                    batch_run = False, 
                                    batch_num = 2, 
                                    batch_step = 1, 
                                    non_sfd_class_n = 500, 
                                    sfd_class_n = 500, 
                                    test_ratio = 0.2, 
                                    dummy_run = False)
    sr_tot.append(model_res_df_x['Success Rate'][0])

sr_tot = pd.DataFrame(sr_tot)
sr_tot = sr_tot[0].astype(float)
print(sr_tot.describe())


#model_res_df.to_csv('model_res_df_'+sys.argv[1]+'.csv')

#print(sys.argv[1])
    
