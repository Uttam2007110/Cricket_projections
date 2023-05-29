# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 18:03:49 2023
Concate single match data into 1 file
@author: Subramanya.Ganti
"""

# importing the required modules
import glob
import pandas as pd
from datetime import datetime
 
# specifying the path to csv files
path = "C:/Users/Subramanya.Ganti/Downloads/cricket/blast"
output = 'blast.csv'
db_start = 2017
 
# csv files in the path
file_list = glob.glob(path + "/*.csv")
 
# list of excel files we want to merge.
# pd.read_excel(file_path) reads the 
# excel data into pandas dataframe.
excl_list = []
countries = ["Afghanistan","Australia","Bangladesh","England","India","Ireland","Namibia","Netherlands","New Zealand","Pakistan","Scotland","South Africa","Sri Lanka","United Arab Emirates","West Indies","Zimbabwe"]
 
for file in file_list:
    if(file[-8:] != "info.csv"):
        df = pd.read_csv(file)
        date = datetime.strptime(df['start_date'][0], '%Y-%m-%d')        
        #if(df['batting_team'][0] in countries and df['bowling_team'][0] in countries):
        if(date.year>=db_start):
            df['season'] = date.year
            print(df['start_date'][0],df['batting_team'][0],df['bowling_team'][0])
            excl_list.append(df)
 
print("data collected, concat starts")
# concatenate all DataFrames in the list
# into a single DataFrame, returns new
# DataFrame.
excl_merged = pd.concat(excl_list, ignore_index=True)
# exports the dataframe into excel file
# with specified name.
print("concat done, file dumped")

excl_merged.to_csv(output, index=False)

