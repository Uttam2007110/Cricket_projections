# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 18:03:49 2023
Concate single match data into 1 file
@author: Subramanya.Ganti
"""

import glob
import pandas as pd
from datetime import datetime
 
comp = 'blast'
path = f"C:/Users/Subramanya.Ganti/Downloads/cricket/{comp}"
output = f'{comp}.csv'
db_start = 2017
league = 0; check = 0
 
file_list = glob.glob(path + "/*.csv")
excl_list = []
if(comp == 'odiq'):
    countries = ["Zimbabwe","Netherlands","West Indies","Nepal","United States of America","Sri Lanka","Ireland","Scotland","Oman","United Arab Emirates"]
elif(comp == 't20w'):
    countries = ["Australia","England","New Zeland","India","South Africa","Sri Lanka","Ireland","Scotland","West Indies","Pakistan","Bangladesh","Thailand","Zimbabwe"]
elif(comp == 'odiw'):
    countries = ["Australia","England","New Zeland","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Thailand"]
elif(comp == 'odi'): 
    countries = ["Australia","England","New Zeland","India","South Africa","Sri Lanka","Pakistan","Bangladesh","Afghanistan","West Indies"]
elif(comp == 't20i'):
    countries = ["Australia","England","New Zeland","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Ireland","Afghanistan","Zimbabwe","Scotland","Netherlands","Namibia","United Arab Emirates"]
else:
    league = 1

for file in file_list:
    if(file[-8:] != "info.csv"):
        df = pd.read_csv(file)
        date = datetime.strptime(df['start_date'][0], '%Y-%m-%d')
        if(league == 0):check = df['batting_team'][0] in countries and df['bowling_team'][0] in countries
        if(date.year>=db_start and (check or league)):
            df['season'] = date.year
            print(df['start_date'][0],df['batting_team'][0],df['bowling_team'][0])
            excl_list.append(df)
 
print("data collected, concat starts")
excl_merged = pd.concat(excl_list, ignore_index=True)
excl_merged.to_csv(output, index=False)
print("concat done, file dumped")
