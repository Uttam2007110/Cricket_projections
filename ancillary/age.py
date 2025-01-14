# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 12:59:57 2023
finding the effects of aging on player skill
@author: Subramanya.Ganti
"""

#%% import libraries
import pandas as pd
import numpy as np
import urllib.request, json
from urllib.error import HTTPError
from datetime import datetime
from scipy import stats
pd.options.mode.chained_assignment = None  # default='warn'

path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'

#%% read the relevant files
file_name = f'{path}/summary/full/blast_summary_full.xlsx'
batting_blast = pd.read_excel(file_name,'batting seasons')
batting_blast = batting_blast.fillna(0)
bowling_blast = pd.read_excel(file_name,'bowling seasons')
bowling_blast = bowling_blast.fillna(0)
file_name = f'{path}/summary/full/bbl_summary_full.xlsx'
batting_bbl = pd.read_excel(file_name,'batting seasons')
batting_bbl = batting_bbl.fillna(0)
bowling_bbl = pd.read_excel(file_name,'bowling seasons')
bowling_bbl = bowling_bbl.fillna(0)
file_name = f'{path}/summary/full/ipl_summary_full.xlsx'
batting_ipl = pd.read_excel(file_name,'batting seasons')
batting_ipl = batting_ipl.fillna(0)
bowling_ipl = pd.read_excel(file_name,'bowling seasons')
bowling_ipl = bowling_ipl.fillna(0)
file_name = f'{path}/summary/full/t20i_summary_full.xlsx'
batting_t20i = pd.read_excel(file_name,'batting seasons')
batting_t20i = batting_t20i.fillna(0)
bowling_t20i = pd.read_excel(file_name,'bowling seasons')
bowling_t20i = bowling_t20i.fillna(0)
reference = pd.read_csv(f'{path}/people.csv',sep=',',low_memory=False)
reference = reference.fillna(0)

#%% extract DOBs for every player
def age(key,start):
    p_age = 0; dob = datetime(1,1,1); bat_type = ''; bowl_type = ''
    try:
        with urllib.request.urlopen(f'http://core.espnuk.org/v2/sports/cricket/athletes/{key}') as url:
            try:
                data = json.load(url)
                try:
                    name = data['battingName']
                    dob = data['dateOfBirth']
                    dob = dob.replace('T00:00Z','')
                    try:
                        dob = datetime.strptime(dob, '%Y-%m-%d')
                        p_age = int((start - dob).days/365)    #start is in this format datetime(2023,4,1)
                        print(name,p_age,dob)
                    except ValueError:
                        print(name,"issue with dob",dob)
                        p_age = 100
                    try:
                        bat_type = data['style'][0]['description']
                    except IndexError:
                        bat_type = 'NA'
                    try:
                        bowl_type = data['style'][1]['description']
                    except IndexError:
                        bowl_type = 'NA'
                except KeyError:
                    print(key,"API label mismatch")
                    p_age = 100
            except:
                print(key,"JSONDecodeError: Invalid control character at")
                p_age = 100
    except HTTPError:
        print(key,"id not in cricinfo")
        p_age = 100
    return (age,dob,bat_type,bowl_type)

def names_list(batting,bowling,reference):
    bat = batting['batsman'].to_list()
    bowl = bowling['bowler'].to_list()
    names = bat + bowl
    names = list(set(names))
    df = pd.DataFrame(columns=['name','ID','DOB','batType','bowlType'])
    df['name'] = names
    
    for x0 in df.values:
        #print(x0)
        pid = int(reference.loc[reference['unique_name']==x0[0],'key_cricinfo'].sum())
        df.loc[df['name']==x0[0],'ID'] = pid
        p_age,dob,bat_type,bowl_type = age(pid,datetime(2024,4,1))
        df.loc[df['name']==x0[0],'DOB'] = dob
    return df

def names_list_full(sheet):
    reference = pd.read_excel(f'{path}/excel/people.xlsx',f'{sheet}')
    #reference['batType'] = ''
    #reference['bowlType'] = ''
    #reference = reference.fillna(0)
    #reference['dob'] = age(int(reference['key_cricinfo']),datetime(2023,4,1))[1]
    for x in reference.values:
        p_key = reference.loc[reference['unique_name']==x[2],'key_cricinfo'].sum()
        p_age,p_dob,bat_type,bowl_type = age(int(p_key),datetime(2024,4,1))
        reference.loc[reference['unique_name']==x[2],'dob'] = p_dob
        reference.loc[reference['unique_name']==x[2],'batType'] = bat_type
        reference.loc[reference['unique_name']==x[2],'bowlType'] = bowl_type
    return reference

#names = names_list(batting_bbl,bowling_bbl,reference)
names = names_list_full('new')

#%% season age calculation for every player 
batting_blast['Age'] = 0
bowling_blast['Age'] = 0
batting_bbl['Age'] = 0
bowling_bbl['Age'] = 0
batting_ipl['Age'] = 0
bowling_ipl['Age'] = 0
batting_t20i['Age'] = 0
bowling_t20i['Age'] = 0

def season_age(batting,bowling):
    for x in batting.values:
        dob = names.loc[names['name']==x[0],'DOB'].sum()
        try: p_age = int((datetime(x[1],4,1) - dob).days/365)
        except TypeError: p_age = 0
        batting.loc[(batting['batsman']==x[0]) & (batting['season']==x[1]),'Age'] = p_age
        
    for x in bowling.values:
        dob = names.loc[names['name']==x[0],'DOB'].sum()
        try: p_age = int((datetime(x[1],4,1) - dob).days/365)
        except TypeError: p_age = 0
        bowling.loc[(bowling['bowler']==x[0]) & (bowling['season']==x[1]),'Age'] = p_age
        
    with pd.ExcelWriter(file_name) as writer:
        batting.to_excel(writer, sheet_name="batting seasons", index=False)
        bowling.to_excel(writer, sheet_name="bowling seasons", index=False)
    return batting,bowling

batting_blast,bowling_blast = season_age(batting_blast,bowling_blast)
batting_bbl,bowling_bbl = season_age(batting_bbl,bowling_bbl)
batting_ipl,bowling_ipl = season_age(batting_ipl,bowling_ipl)
batting_t20i,bowling_t20i = season_age(batting_t20i,bowling_t20i)
    
#%% age curve analysis on performance
def batter_aging(batting,skill):
    #batting = batting[batting['balls_batsman'] >= 50]
    df = batting[['batsman','batting_team','Age','balls_batsman',f'{skill}']]
    df['Age +1'] = df['Age'] + 1
    df['balls_batsman +1'] = np.nan
    df[f'{skill} +1'] = np.nan
    for z in df.values:
        df.loc[(df['batsman']==z[0])&(df['Age']==z[2]),'balls_batsman +1'] = batting.loc[(batting['batsman']==z[0])&(batting['Age']==z[2]+1),'balls_batsman'].sum()
        df.loc[(df['batsman']==z[0])&(df['Age']==z[2]),f'{skill} +1'] = batting.loc[(batting['batsman']==z[0])&(batting['Age']==z[2]+1),f'{skill}'].sum()
    df = df[df['balls_batsman +1'] != 0]
    df['harmonic balls'] = stats.hmean([ df['balls_batsman'] , df['balls_batsman +1'] ])
    df['delta'] = df[f'{skill} +1'] - df[f'{skill}']
    df['weighted delta'] = df['delta']*df['harmonic balls']
    data = pd.pivot_table(df,values=['weighted delta','harmonic balls'],index=['Age +1'],aggfunc=np.sum)
    data[f'{skill} delta'] = data['weighted delta']/data['harmonic balls']
    #data = data[data['harmonic balls'] >= 200]
    return data

def bowler_aging(bowling,skill):
    #bowling = bowling[bowling['balls_bowler'] >= 50]
    df = bowling[['bowler','bowling_team','Age','balls_bowler',f'{skill}']]
    df['Age +1'] = df['Age'] + 1
    df['balls_bowler +1'] = np.nan
    df[f'{skill} +1'] = np.nan
    for z in df.values:
        df.loc[(df['bowler']==z[0])&(df['Age']==z[2]),'balls_bowler +1'] = bowling.loc[(bowling['bowler']==z[0])&(bowling['Age']==z[2]+1),'balls_bowler'].sum()
        df.loc[(df['bowler']==z[0])&(df['Age']==z[2]),f'{skill} +1'] = bowling.loc[(bowling['bowler']==z[0])&(bowling['Age']==z[2]+1),f'{skill}'].sum()
    df = df[df['balls_bowler +1'] != 0]
    df['harmonic balls'] = stats.hmean([ df['balls_bowler'] , df['balls_bowler +1'] ])
    df['delta'] = df[f'{skill} +1'] - df[f'{skill}']
    df['weighted delta'] = df['delta']*df['harmonic balls']
    data = pd.pivot_table(df,values=['weighted delta','harmonic balls'],index=['Age +1'],aggfunc=np.sum)
    data[f'{skill} delta'] = data['weighted delta']/data['harmonic balls']
    #data = data[data['harmonic balls'] >= 200]
    return data

def deltas(bat_bowl,skill):
    if(bat_bowl == 1):
        final = batter_aging(batting_blast,skill)
        final = final.add(batter_aging(batting_bbl,skill),fill_value = 0)
        final = final.add(batter_aging(batting_ipl,skill),fill_value = 0)
        final = final.add(batter_aging(batting_t20i,skill),fill_value = 0)
        final[f'{skill} delta'] = final['weighted delta']/final['harmonic balls']
        final = final[final['harmonic balls'] >= 5000]
    else:
        final = bowler_aging(bowling_blast,skill)
        final = final.add(bowler_aging(bowling_bbl,skill),fill_value = 0)
        final = final.add(bowler_aging(bowling_ipl,skill),fill_value = 0)
        final = final.add(bowler_aging(bowling_t20i,skill),fill_value = 0)
        final[f'{skill} delta'] = final['weighted delta']/final['harmonic balls']
        final = final[final['harmonic balls'] >= 5000]
    return final

final = deltas(0,'extras/ball')
