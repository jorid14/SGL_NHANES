#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 20:10:11 2021

"""


import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from itertools import combinations
import time 
import matplotlib as plt

def nhanes_full_log_reg(df, fped_vars, var_combinatorial, batch_run, batch_num, 
                        batch_step, non_sfd_class_n, sfd_class_n, test_ratio):
    
    #Model execution start time
    startTime = time.time()
    #Create list of all FPED variable combinations if desired    
    if (var_combinatorial == True):
        cmb_output = sum([list(map(list, combinations(fped_vars , i))) for i in range(len(fped_vars ) + 1)], [])
        cmb_output = cmb_output[1:]
    else: 
        cmb_output = fped_vars

    #Partition the list of FPED variable combinations with batch parameters, if batch run desired
    if (batch_run == True):
        #Obtain batch length and step through the indecies of the variable list
        batch_len = int(len(cmb_output)/batch_num)
        idx1 = 0 + batch_len*int(batch_step)
        idx2 = batch_len + batch_len*int(batch_step)
        cmb_output = cmb_output[idx1:idx2]

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
            var_idx = cmb_output.index(var)
            progress_pct = round(100 * var_idx / len(cmb_output), 2)
            if (progress_pct%1==0):
                print("Progress: "+str(progress_pct)+" %")
        
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
 

def model_sel(df_sel, var_level, top_n_sel):
    top_n_sel = var_level.sort_values(by = 'Success Rate', ascending=False).head(top_n_sel)
    top_n_sel_vars = top_n_sel.drop(['Success Rate', 'Runtime(Seconds)'], axis=1)
    top_n_sel_vars = top_n_sel_vars.reset_index()
    result = pd.DataFrame([])
    for index, row in top_n_sel_vars.iterrows():
        model_sel_var_list = top_n_sel_vars.loc[index].to_list()
        model_sel_var_list = model_sel_var_list[2:]
        model_sel_var_list_final = []
        for x in model_sel_var_list: 
            if str(x) != 'nan': model_sel_var_list_final.append(x)
        d = nhanes_full_log_reg(df = df_sel,
                                fped_vars = model_sel_var_list_final, 
                                var_combinatorial = False, 
                                batch_run = False, 
                                batch_num = 2, 
                                batch_step = 1, 
                                non_sfd_class_n = 1000, 
                                sfd_class_n = 1000, 
                                test_ratio = 0.2)
        result = result.append(d)
        
    result['Success Rate'] = result['Success Rate'].astype(float)
    return result
    


#Read model evaluation results
model_res_df_L2 = pd.read_csv('../Model_Results/model_res_df_L2.csv')
model_res_df_L3 = pd.read_csv('../Model_Results/model_res_df_L3.csv')
#Read data frame and add plant pf total variable
df = pd.read_csv('../Data/nhanes_full_pre_proc.csv')
df['PF_PLANT_D_TOTAL'] = df['PF_EGGS']+df['PF_SOY']+df['PF_NUTSDS']+df['PF_LEGUMES']
#Run model selection
model_sel = model_sel(df, model_res_df_L3, 100)


#Plot and compare to all variable input combinations
model_sel['Top Models SR'] = model_sel['Success Rate']
model_sel['Top Models SR'].plot.kde(legend="L4")
model_res_df_L3['All Models SR'] = model_res_df_L3['Success Rate']
model_res_df_L3['All Models SR'].plot.kde(legend="L3")



model_sel_count = model_sel.drop(['Success Rate', 'Runtime(Seconds)', 'Top Models SR'], axis =1).count()
plt.pyplot.clf()
model_sel_count.plot.bar()
