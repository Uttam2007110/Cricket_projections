# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 15:59:59 2025
TF-IDF vectorization + random forest regression approach to classify curves by their name
@author: Subramanya.Ganti
"""
#%% initialize variables
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import os

grp_choice = 2

def derive_paths():
    user = os.getenv('username').lower() #.replace(".", "_")
    #mr-quant-risk-library\MR_Quant_Risk\Data_Connection\Excel_Connection\GLNG_3x_scenarios
    file_path = os.path.join(r'C:\Users', user, 'OneDrive - Shell', 'Quantitative Risk Team','Projects','Risk Factor Mapping')
    return file_path

path = derive_paths()
#path = 'C:/Users/Subramanya.Ganti/Downloads'

#%% train the model
#data = pd.read_excel(f'{path}/tf_idf.xlsx','mapped')
data = pd.read_excel(f'{path}/SLMT_group_classification_draft_V2.xlsx','X-COM_MAPPING')
data[['COMMODITY_GRP_0','COMMODITY_GRP_1','COMMODITY_GRP_2','REGION_1','REGION_2']] = data[['COMMODITY_GRP_0','COMMODITY_GRP_1','COMMODITY_GRP_2','REGION_1','REGION_2']].replace({0: '-'})
data['Input'] = data[['CURVE_NAME_VAR','COMMODITY_GRP_1','REGION_1']].agg('_'.join, axis=1)

i=1; data['Output'] = data['COMMODITY_GROUP']
while(i<=grp_choice):
    if(i==1): add = 'PRODUCT_CATEGORY'
    if(i==2): add = 'PRODUCT_NAME'
    #if(i==6): add = 'PRODUCT_SPECIFICATION'
    if(i==3): add = 'GEOGRAPHY_MACRO'
    if(i==4): add = 'GEOGRAPHY_COUNTRY'
    if(i==5): add = 'GEOGRAPHY_LOCATION_DETAIL'
    data['Output'] = data['Output'] + " / " +  data[f'{add}'] #data[f'Revised commodity group {i}']
    i+=1

#data = data[['Input',f'Revised commodity group {grp_choice}']]
#data.rename(columns={ f'Revised commodity group {grp_choice}': 'Output'}, inplace=True)
data = data[['Input','Output']]
data = data.dropna(how='any')
data = data.map(str)

data['Input'] = data['Input'].str.replace('_-','')
data['Input'] = data['Input'].str.replace('_',' ')
data['Input'] = data['Input'].str.replace(r'(\D+)(\d+)',r'\1 \2', regex=True)
data['Input'] = data['Input'].str.replace('-',' ')
data['Input'] = data['Input'].str.replace('&','')
data['Input'] = data['Input'].str.replace('/',' ')
data['Input'] = data['Input'].replace(r'\s+', ' ', regex=True)
data['Input'] = data['Input'].str.upper()

def reduce_size(data):
    #drop groups which have only 1 curve
    size_data = data.groupby('Output', as_index=False).size()
    size_data = size_data[size_data['size']>=2]
    for x in data['Output']:
        if((x in size_data['Output'].values) == False):
            #print(x,'dropped')
            data = data[data['Output'] != x]
    return data

def grid_search(X, y):
    pipeline = Pipeline([('tfidf', TfidfVectorizer(stop_words='english')),('clf', RandomForestClassifier()),])
    param_grid = {
        #'tfidf__lowercase': [True, False],
        #'tfidf__analyzer': ['word', 'char', 'char_wb'],
        'clf__n_estimators': [20,50,100],
        'clf__max_depth': [None,2,5,10],
        'clf__min_samples_split': [2,5,10,15],
        'clf__min_samples_leaf':[1,5,10]}
    # Perform time series cross-validation on the remaining 80%
    tscv = TimeSeriesSplit(n_splits=2)
    # Perform GridSearchCV with time series cross-validation    
    grid_search = GridSearchCV(pipeline, param_grid, scoring='accuracy', cv=tscv)
    grid_search.fit(X, y)
    # Get the best hyperparameters from the grid search
    best_rf_model = grid_search.best_estimator_
    print("best pipeline",best_rf_model)
    print("score",grid_search.score(X,y))
    return grid_search

def train_test(data):
    # Split the dataset into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(data['Input'], data['Output'], test_size=0.2, stratify=data[["Output"]])
    #grid_search = grid_search(X_train, y_train)
    # Create a pipeline
    pipeline = Pipeline([('tfidf', TfidfVectorizer(stop_words='english')),('clf', RandomForestClassifier()),])
    #pipeline = grid_search.best_estimator_
    # Train the model
    pipeline.fit(X_train, y_train)
    
    predictions = pipeline.predict(X_test)
    probability = pipeline.predict_proba(X_test)
    probability = pd.DataFrame(probability, index=X_test, columns=data['Output'].drop_duplicates())
    
    # Evaluate the model
    print(classification_report(y_test, predictions))
    print(f"Accuracy: {accuracy_score(y_test, predictions)}")
    print("training score",pipeline.score(X_train,y_train))
    
    return pipeline

#remove rows with only 1 unique value
data = reduce_size(data)
pipeline = train_test(data)

#%% Predictions for missing curves
#unmapped_curves = pd.read_excel(f'{path}/tf_idf.xlsx','unmapped')
unmapped_curves = pd.read_excel(f'{path}/SLMT_group_classification_draft_V2.xlsx','unmapped')
#filtering out curves without stress test mapping
unmapped_curves = unmapped_curves[unmapped_curves['COMMODITY_GRP_0'] != '-']
unmapped_curves['vector'] = unmapped_curves[['CURVE_NAME_VAR','COMMODITY_GRP_1','REGION_1']].agg('_'.join, axis=1)

unmapped_curves['vector'] = unmapped_curves['vector'].str.replace('_-','')
unmapped_curves['vector'] = unmapped_curves['vector'].str.replace('_',' ')
unmapped_curves['vector'] = unmapped_curves['vector'].str.replace(r'(\D+)(\d+)',r'\1 \2', regex=True)
unmapped_curves['vector'] = unmapped_curves['vector'].str.replace('-',' ')
unmapped_curves['vector'] = unmapped_curves['vector'].str.replace('&','')
unmapped_curves['vector'] = unmapped_curves['vector'].str.replace('/',' ')
unmapped_curves['vector'] = unmapped_curves['vector'].replace(r'\s+', ' ', regex=True)
unmapped_curves['vector'] = unmapped_curves['vector'].str.upper()

reference = unmapped_curves[['CURVE_NAME_VAR','vector']]
unmapped_curves = unmapped_curves['vector']
unmapped_curves = unmapped_curves.drop_duplicates()
unmapped_predictions = pipeline.predict(unmapped_curves)
unmapped_probability = pipeline.predict_proba(unmapped_curves)
unmapped_probability = pd.DataFrame(unmapped_probability, index=unmapped_curves, columns=data['Output'].sort_values().drop_duplicates())

def unmapped_rankings(unmapped_probability):
    unmapped_rank = pd.DataFrame(index=unmapped_probability.index, columns=range(1,len(unmapped_probability.T)+1))
    unmapped_p = pd.DataFrame(index=unmapped_probability.index, columns=range(1,len(unmapped_probability.T)+1))
    unmapped_rank = unmapped_rank.T
    unmapped_p = unmapped_p.T
    unmapped_probability = unmapped_probability.T
    
    for x in unmapped_probability.columns:
        unmapped_probability = unmapped_probability.sort_values(by=x, ascending=False)
        unmapped_rank[x] = unmapped_probability[x].index
        unmapped_p[x] = unmapped_probability[x].values
    
    unmapped_rank = unmapped_rank.T
    unmapped_p = unmapped_p.T
    return unmapped_rank,unmapped_p

unmapped_predictions,unmapped_probability = unmapped_rankings(unmapped_probability)
#probability = probability.T
#unmapped_probability = unmapped_probability.T
