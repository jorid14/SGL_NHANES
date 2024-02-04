#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jorid Topi

This script defines a logistic regression model and fits the NHANES data to it.
The model is evaluated over several runs.
A PCA analysis is also performed. 
The output products for the final report are generated here.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import linear_model
import numpy as np
import scipy.stats as stat
import dataframe_image as dfi
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt



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


def nhanes_full_log_reg(df, fped_vars, non_sfd_class_n, sfd_class_n, test_ratio, r_seed):
    
    '''
    Logistic regression fit. Performs the random sampling among the classes, creating a balanced
    training data set. 
    
    Returns the success rate for the training and test data sets. Also returns the coefficients
    from each fit and the p-values for those coefficients.
    '''
    
    #Sample the seafood and non-seafood classes, create model input df
    df_non_sfd = df[df['seafood_meal']==0].sample(n=non_sfd_class_n, random_state = r_seed)
    df_sfd = df[df['seafood_meal']==1].sample(n=sfd_class_n, random_state = r_seed)
    df_mdl = pd.concat([df_non_sfd, df_sfd])
    #Add the classification target variable to the df input list
    fped_vars.append('seafood_meal')
    #Use variable combination selected by loop
    df_mdl = df_mdl[fped_vars]
    #Split the training and test data
    X_train, X_test, y_train, y_test = train_test_split(df_mdl.drop(['seafood_meal'], axis=1), df_mdl['seafood_meal'], test_size=test_ratio, random_state = r_seed)
    #Fit the logistic regression model for the regression and p-value classes
    log_reg = LogisticRegression()
    log_reg.fit(X_train, y_train)
    log_reg_p_values = LogisticReg()
    log_reg_p_values.fit(X_train, y_train)
    #Obtain predictions on test set and calculate success rate for both test and training sets
    y_pred = log_reg.predict(X_test)
    y_pred_train = log_reg.predict(X_train)
    n_correct = sum(y_pred == y_test)
    pred_sr = [str(n_correct/len(y_pred))]
    n_correct_train = sum(y_pred_train == y_train)
    pred_sr_train = [str(n_correct_train/len(y_pred_train))]
    fped_vars.remove('seafood_meal')
    return pred_sr, pred_sr_train, log_reg.coef_, log_reg.intercept_, log_reg_p_values
    

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
Evaluation of the logistic regression model, using all components.
Reproducible with same random seed over 100 runs
'''

#Create lists to be populated from the collection of the model fit outputs: score, coefficients, p-values
test_pred_sr_tot=[]
train_pred_sr_tot=[]
model_coeff = []
model_intercept = []
model_p_values = []

#Fit the model 100 times using a random seed of 1-100. Collect the outputs.
for i in range(100):
    test_pred_sr, train_pred_sr, log_reg_coefficients, log_reg_intercept, p_values = nhanes_full_log_reg(df = df,
                                       fped_vars = fped_components, 
                                       non_sfd_class_n = 1000, 
                                       sfd_class_n = 1000, 
                                       test_ratio = 0.2,
                                       r_seed = i)
    model_p_values.append(p_values.p_values)
    test_pred_sr_tot.append(test_pred_sr)
    train_pred_sr_tot.append(train_pred_sr)
    model_coeff.append(log_reg_coefficients)
    model_intercept.append(log_reg_intercept)

#Create a model evaluation dataframe for the 100 runs, with scores and coefficients
test_pred_sr_tot = pd.DataFrame(test_pred_sr_tot)
test_pred_sr_tot = test_pred_sr_tot.astype(float)
test_pred_sr_tot = test_pred_sr_tot.rename({0: 'Test SR'}, axis=1)
train_pred_sr_tot = pd.DataFrame(train_pred_sr_tot)
train_pred_sr_tot = train_pred_sr_tot.astype(float)
train_pred_sr_tot = train_pred_sr_tot.rename({0: 'Train SR'}, axis=1)
model_eval_df = pd.concat((test_pred_sr_tot, train_pred_sr_tot), axis = 1)
model_intercept = pd.DataFrame(model_intercept)
model_intercept = model_intercept.astype(float)
model_intercept =  model_intercept.rename({0: 'Itercept'}, axis=1)
model_eval_df = pd.concat((model_eval_df, model_intercept), axis = 1)
model_coeff = pd.DataFrame(np.concatenate(model_coeff))
model_coeff.columns = fped_components
model_eval_df = pd.concat((model_eval_df, model_coeff), axis = 1)

#Obtain the means of the p-values and the model coefficients
model_p_values = pd.DataFrame(model_p_values)
model_p_values.columns = fped_components
model_p_values_mean = model_p_values.mean(axis=0)
model_p_values_mean = model_p_values_mean.sort_values()
model_coeff_values = pd.DataFrame(model_coeff)
model_coeff_values.columns = fped_components
model_coeff_values_mean = model_coeff_values.mean(axis=0)
model_coeff_values_mean = model_coeff_values_mean.sort_values()


'''
Figure outputs for reports and presentations.
'''

'''
Model training score distribution: Generates histogram and saves to figure
'''

ax = model_eval_df['Train SR'].plot.hist(title = 'Logistic Regression: Training Score')
fig = ax.get_figure()
fig.savefig('../../Figures/Log_Reg_Train_Score.png')
fig.clf()

'''
Model test score distribution: Generates histogram and saves to figure
'''

model_eval_df['Test SR'].plot.hist(title = 'Logistic Regression: Test Score')
fig = ax.get_figure()
fig.savefig('../../Figures/Log_Reg_Test_Score.png')
fig.clf()

'''
Find the top 10 p-value means, create a table with them and save the table as a figure
'''

model_p_values_mean_10 = model_p_values_mean.head(10)
model_p_values_mean_10 = pd.DataFrame(model_p_values_mean_10).reset_index()
model_p_values_mean_10 = model_p_values_mean_10.rename({'index': '', 0: 'Mean P'}, axis=1)
model_p_values_mean_10.set_index('', inplace=True)
model_p_values_mean_10 = model_p_values_mean_10.round(5)
dfi.export(model_p_values_mean_10,"../../Figures/P_Value_Means_Top10.png")

'''
Plot the distribution of coefficient estimates for the coefficients with top 10 p-values
'''

top_p_values = model_p_values_mean_10.index.values.tolist()
model_eval_df_top_p = model_eval_df[top_p_values]
ax = model_eval_df_top_p.plot.box(rot=90, title="Logistic Regression Coefficient Distribution: \nMost Significant Components")
plt.axhline(0, c='r')
fig = ax.get_figure()
fig.savefig('../../Figures/Coeff_Est_Top10_P.png', bbox_inches = "tight")
fig.clf()


'''
Find the coefficient means of the coefficients with top 10 p-value means.
Create a table with them and save the table as a figure.
'''

model_coeff_values_mean_10 = model_coeff_values_mean[top_p_values]
model_coeff_values_mean_10 = pd.DataFrame(model_coeff_values_mean_10).reset_index()
model_coeff_values_mean_10 = model_coeff_values_mean_10.rename({'index': '', 0: 'Mean Coeff'}, axis=1)
model_coeff_values_mean_10.set_index('', inplace=True)
model_coeff_values_mean_10 = model_coeff_values_mean_10.round(5)
dfi.export(model_coeff_values_mean_10,"../../Figures/Coeff_Values_Top10.png")

'''
Find the coefficients with the least 10 significant p-value means
Plot the distribution of coefficient estimates for the coefficients with 10 least significant p-values
'''

model_p_values_mean_tail_10 = model_p_values_mean.tail(10)
model_p_values_mean_tail_10 = pd.DataFrame(model_p_values_mean_tail_10).reset_index()
model_p_values_mean_tail_10 = model_p_values_mean_tail_10.rename({'index': '', 0: 'Mean P'}, axis=1)
model_p_values_mean_tail_10.set_index('', inplace=True)
model_p_values_mean_tail_10 = model_p_values_mean_tail_10.round(5)

tail_p_values = model_p_values_mean_tail_10.index.values.tolist()
model_eval_df_tail_p = model_eval_df[tail_p_values]
ax = model_eval_df_tail_p.plot.box(rot=90, title="Logistic Regression Coefficient Distribution: \nLeast Significant Components")
plt.axhline(0, c='r')
fig = ax.get_figure()
fig.savefig('../../Figures/Coeff_Est_Tail10_P.png', bbox_inches = "tight")
fig.clf()


'''
Model diagnostics exploration
Logistic regression evaluation with PCA components
'''

'''
Plot the distribution of the components with most significant p-value means (top 10)
within the seafood meal groups.
'''
for var in top_p_values:
    ax = df.boxplot(column=var,by=['seafood_meal'])
    fig = ax.get_figure()
    fig.savefig('../../Figures/'+var+'_box_plot.png')
    fig.clf()

'''
Generate a correlation matrix heatmap and save the figure
'''

corr = df[fped_components].corr()
ax = plt.matshow(corr)
fig = ax.get_figure()
fig.savefig('../../Figures/Corr_Matrix.png')
fig.clf()

'''
Perform a PCA transformation of the FPED components and select top 5 principal components
'''

X = df[fped_components]
pca = PCA(n_components=5)
pca_x = pca.fit(X)
df_pca = pca_x.transform(X)
df_new = pd.DataFrame(df_pca)
df_new['seafood_meal'] = df['seafood_meal']
var_sel = [0,1,2,3,4]


'''
Evaluation of the logistic regression model, using top 5 principal components.
Reproducible with same random seed over 100 runs
'''

#Create lists to be populated from the collection of the model fit outputs for training and test scores
sr_tot_pca=[]
sr_tot_train_pca=[]

#Fit the model 100 times using a random seed of 1-100. Collect the outputs.
for i in range(100):
    test_pred_sr, train_pred_sr, log_reg_coefficients, log_reg_intercept, p_values = nhanes_full_log_reg(df = df_new,
                fped_vars = var_sel,
                non_sfd_class_n = 1000,
                sfd_class_n = 1000,
                test_ratio = 0.2,
                r_seed = i)
    sr_tot_pca.append(test_pred_sr)
    sr_tot_train_pca.append(train_pred_sr)

#Create dataframes with training and test scores of model fit with PCA
sr_tot_pca = pd.DataFrame(sr_tot_pca)
sr_tot_pca = sr_tot_pca[0].astype(float)
sr_tot_train_pca = pd.DataFrame(sr_tot_train_pca)
sr_tot_train_pca = sr_tot_train_pca[0].astype(float)

'''
PCA Model training score distribution: Generates histogram and saves to figure
'''

ax = sr_tot_pca.plot.hist(title = 'Logistic Regression - PCA: Training Score')
fig = ax.get_figure()
fig.savefig('../../Figures/Log_Reg_PCA_Training_Score.png')
fig.clf()

'''
PCA Model test score distribution: Generates histogram and saves to figure
'''

ax = sr_tot_pca.plot.hist(title = 'Logistic Regression - PCA: Test Score')
fig = ax.get_figure()
fig.savefig('../../Figures/Log_Reg_PCA_Test_Score.png')
fig.clf()


'''
Generate a cumulative sum plot of PCA components for the % variation explained.
Save this plot as a figure.
'''

pca_var_cum_sum = np.cumsum(pca_x.explained_variance_ratio_)
pca_var_cum_sum = pd.DataFrame(pca_var_cum_sum)
pca_var_cum_sum[0] = pca_var_cum_sum[0]*100
pca_var_cum_sum.index = pca_var_cum_sum.index + 1
plt.plot(pca_var_cum_sum)
plt.ylabel('% Variation Explained')
plt.xlabel('Number of Components')
plt.title('PCA Analysis')
plt.savefig('../../Figures/PCA_Analysis.png')
plt.clf()


'''
Plot the density of the top principal component among the two seafood meal groups, save the figure
'''

z = df_new.groupby('seafood_meal')[0].plot.kde(title = 'PC = 0',legend='x')[0].set_xlim(-30, 30)
plt.show(z)
plt.savefig('../../Figures/PCA_Component_0.png')
plt.clf()




