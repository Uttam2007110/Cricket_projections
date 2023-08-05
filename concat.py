# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 18:03:49 2023
Concate single match data into 1 file
@author: Subramanya.Ganti
"""

import glob
import pandas as pd
from datetime import datetime
 
comp = 't20i'
if(comp == 'odiq'):
    path = "C:/Users/Subramanya.Ganti/Downloads/cricket/odi"
elif(comp == 't20iq'):
    path = "C:/Users/Subramanya.Ganti/Downloads/cricket/t20i"
else:
    path = f"C:/Users/Subramanya.Ganti/Downloads/cricket/{comp}"
output = f'{comp}.csv'
output2 = f'{comp}_GP.csv'
db_start = 2017
league = 0; check = 0
col_names = ["col1", "col2", "team", "player","id"]
excl_list = []; names_list=[]; i=0

file_list = glob.glob(path + "/*.csv")
if(comp == 'odiq'):
    countries = ["Zimbabwe","Netherlands","West Indies","Nepal","United States of America","Sri Lanka","Ireland","Scotland","Oman","United Arab Emirates"]
elif(comp == 't20iw'):
    countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Ireland","Scotland","West Indies","Pakistan","Bangladesh","Thailand","Zimbabwe"]
elif(comp == 'odiw'):
    countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Thailand","Ireland"]
elif(comp == 'odi'):
    countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Pakistan","Bangladesh","Afghanistan","West Indies","Netherlands"]
elif(comp == 't20i'):
    countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Ireland","Afghanistan","Zimbabwe","Scotland","Netherlands","Namibia","United Arab Emirates"]
elif(comp == 't20iq'):
    countries = ["Ireland","Scotland","Jersey","Italy","Germany","Denmark","Austria","France","Spain","Netherlands","Malta","Uganda","Malasiya","Kenya","Portugal","Belgium","Norway","Finland"]
elif(comp == 'tests'):
    countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Pakistan","West Indies"]
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
            
    if(file[-8:] == 'info.csv'):
        df = pd.read_csv(file, names=col_names)
        date = datetime.strptime(df.loc[df['col2']=='date','team'].values[0], '%Y/%m/%d')
        t1 = df.loc[(df['col2']=='team') | (df['col2']=='teams'),'team'].values[0]
        t2 = df.loc[(df['col2']=='team') | (df['col2']=='teams'),'team'].values[1]
        if(league == 0):check = t1 in countries and t2 in countries
        if(date.year>=db_start and (check or league)):
            names = df.loc[(df['col2']=='player') | (df['col2']=='players'),'player']
            names = pd.concat([names,pd.Series([t1,t2])])
            names = pd.DataFrame(names)
            names['season'] = date.year
            names = names.rename(columns={0: 'player'})
            if(i==0): names_list=names; i=1
            else: names_list = pd.concat([names_list,names])

print("data collected, concat starts")
excl_merged = pd.concat(excl_list, ignore_index=True)
excl_merged.to_csv(output, index=False)
names_list = names_list.groupby(['player', 'season']).size().reset_index()
names_list = names_list.rename(columns={0: 'GP'})
names_list.to_csv(output2, index=False)
print("concat done, file dumped, run generate.py")
