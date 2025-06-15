# -*- coding: utf-8 -*-
"""
Created on Mon Jun  9 19:20:46 2025
code to extract european basketball stats from RealGM
@author: Subramanya.Ganti
"""

#%% imports
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import datetime

#%% functions
def league_mapping():
    league_code = {
        18:'Adriatic-League-Liga-ABA', 5:'Australian-NBL', 2:'Eurocup', 1:'Euroleague', 12:'French-Jeep-Elite', 15:'German-BBL', 8:'Greek-HEBA-A1',
        11:'Israeli-BSL', 6:'Italian-Lega-Basket-Serie-A', 10:'Lithuanian-LKL', 4:'Spanish-ACB', 7:'Turkish-BSL', 35:'VTB-United-League'}
    return league_code
    
def player_dob_height(url):
    url = f"https://basketball.realgm.com/{url}"
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    player = soup.find_all('div', class_='wrapper clearfix container')[0]
    playerprofile = re.sub(r'\n\s*\n', r'\n', player.get_text().strip(), flags=re.M)
    output = playerprofile + "\n"
    output = output.splitlines()
    
    try:
        height = output[1].replace('Height:','').split('(')[0].strip().split('-')
        height = int(height[0])*12 + int(height[1])
        dob = output[3].replace('Born:','').replace(',','').split('(')[0].strip().split(' ')
        dob = dob[1]+'-'+dob[0]+'-'+dob[2]
    except ValueError: 
        try:
            height = output[2].replace('Height:','').split('(')[0].strip().split('-')
            height = int(height[0])*12 + int(height[1])
            dob = output[4].replace('Born:','').replace(',','').split('(')[0].strip().split(' ')
            dob = dob[1]+'-'+dob[0]+'-'+dob[2]
        except:
            height = 0 
            dob = ""
    except IndexError: 
        try:
            height = output[1].replace('Height:','').split('(')[0].strip().split('-')
            height = int(height[0])*12 + int(height[1])
            dob = output[2].replace('Born:','').replace(',','').split('(')[0].strip().split(' ')
            dob = dob[1]+'-'+dob[0]+'-'+dob[2]
        except:
            height = 0 
            dob = ""
    except:
        height = 0 
        dob = ""
        
    return height,dob

def extract_table_data(code,league,season,data_type,data_filter):

    if(data_filter == ''): 
        url = f"https://basketball.realgm.com/international/league/{code}/{league}/team-stats/{season}/{data_type}"
    else: url = f"https://basketball.realgm.com/international/league/{code}/{league}/stats/{season}/{data_type}/{data_filter}/All/points/All/desc/1/Regular_Season"
    
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    #tables = soup.find_all('table')
    
    table = soup.find('table')
    table_data = []
    for row in table.find_all('tr'):
        row_data = []; links = []
        for cell in row.find_all('td'):
            link = cell.find('a')
            if link:
                href = link.get('href')
                text = link.get_text(strip=True)
                #row_data.append({'text': text, 'link': href})
                row_data.append(text)
                links.append(href)
            else:
                text = cell.get_text(strip=True)
                #row_data.append({'text': text, 'link': None})
                row_data.append(text)
        row_data = row_data + links
        
        for cell in row.find_all('th'):
            text = cell.get_text(strip=True)
            #row_data.append({'text': text, 'link': None})
            row_data.append(text)
            
        table_data.append(row_data)
           
    diff = len(table_data[1]) - len(table_data[0])
    i=1
    while(i<=diff):
        table_data[0].append(f'link_{i}')
        i+=1
        
    df = pd.DataFrame(table_data[1:], columns = table_data[0])
    return df

def derive_player_stats_league(code,league,season):
    totals = extract_table_data(code,league,season,'Totals','All')
    advanced = extract_table_data(code,league,season,'Advanced_Stats','All')
    team = extract_table_data(code,league,season,'Totals','')
    team = team[['GP','MIN','STL','BLK','link_1']]
    team['team_full'] = team['link_1'].str.split('/').str[7]
    
    p_stats = advanced.merge(totals, left_on=['Player','Team','link_1','link_2'], right_on=['Player','Team','link_1','link_2'])
    p_stats['team_full'] = p_stats['link_2'].str.split('/').str[7]
    
    p_stats = p_stats.merge(team, left_on=['team_full'], right_on=['team_full'])
    #numbers greater than 1000 have commas
    p_stats['MIN_x'] = p_stats['MIN_x'].replace(r',', '', regex=True)
    p_stats['ORtg'] = p_stats['ORtg'].replace(r',', '', regex=True)
    
    p_stats = p_stats.apply(pd.to_numeric, errors='ignore')
    p_stats['mp'] = p_stats['MIN_x'] / p_stats['GP_x']
    p_stats['3par'] = p_stats['3PA'] / p_stats['FGA']
    #review this
    p_stats['blk_share'] = ((p_stats['BLK_x']/p_stats['GP_x'])*40/p_stats['mp']) / (p_stats['BLK_y']/p_stats['GP_y'])
    p_stats['stl_share'] = ((p_stats['STL_x']/p_stats['GP_x'])*40/p_stats['mp']) / (p_stats['STL_y']/p_stats['GP_y'])
    p_stats['ast/tov'] = p_stats['AST'] / p_stats['TOV']
    p_stats['ftr'] = p_stats['FTA'] / p_stats['FGA']
    # review this
    p_stats['pfr'] = (p_stats['PF'] / p_stats['GP_x']) * (40 / p_stats['mp'])
    p_stats['season'] = season
    
    p_stats = p_stats[['Player','TS%','ORB%', 'DRB%', 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%','ORtg','DRtg','GP_x','mp','3par',
    'blk_share','stl_share','ast/tov','ftr','3P%','FT%','link_1_x','MIN_x','season']]
    p_stats[['pid','hgt','dunkar','rimar','rim%','midar','mid%','bpm','class']] = np.nan
    p_stats = p_stats.rename(columns={'Player': 'player', 'team_full': 'team', 'GP_x':'GP', 'USG%':'usg', 'TOV%':'TO%', 'DRtg':'drtg'})
    
    p_stats = p_stats[['player','pid','team','season','class','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%','blk_share',
                     'STL%','stl_share','pfr','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','bpm','link_1_x','MIN_x']]
    return p_stats

def aggregate_stats_seasons(code,league,i):
    concat_list = []; exceptions = []
    while(i<2026):
        try:
            player_stats = derive_player_stats_league(code,league,i)
            concat_list.append(player_stats)
        except:
            exceptions.append({league,i})
        i+=1
        time.sleep(1)
    concat_list = pd.concat(concat_list)
    return concat_list,exceptions

def all_leagues_aggregate():
    full_aggregate = []; full_exceptions = []
    code = league_mapping()
    for x in code: 
        #print(x,code[x])
        league,exceptions = aggregate_stats_seasons(x,code[x],2008)
        full_aggregate.append(league)
        full_exceptions.append(exceptions)
    
    full_aggregate = pd.concat(full_aggregate)
    return full_aggregate,full_exceptions

def pivot_data(df):
    pivot = df.pivot_table(values=['pid','class', 'hgt', 'mp', 'usg', 'TS%', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 'BLK%', 'blk_share','STL%',
                                   'stl_share', 'pfr', 'ftr', 'FT%', 'dunkar', 'rimar', 'rim%','midar', 'mid%', '3par', '3P%','ORtg', 'drtg', 'bpm'],
                              index=['player','season','link_1_x'], 
                              aggfunc=lambda rows: np.average(rows, weights=df.loc[rows.index, 'MIN_x']))

    gp = df.pivot_table(values=['GP'], index=['player','season','link_1_x'], aggfunc="sum")
    team = df.pivot_table(values=['team'], index=['player','season','link_1_x'], aggfunc=lambda x: ' '.join(x.unique()))

    team = team.reset_index()
    gp = gp.reset_index()
    pivot = pivot.reset_index()

    df0 = team.merge(gp, left_on=['player','season','link_1_x'], right_on=['player','season','link_1_x'])
    df0 = df0.merge(pivot, left_on=['player','season','link_1_x'], right_on=['player','season','link_1_x'])
    return df0

def aggregate_age_dob(df):
    print("unique entries",len(df['link_1_x'].unique()))
    bio = []; c = 0
    for links in df['link_1_x'].unique():
        hgt,dob = player_dob_height(links)
        bio.append([links,hgt,dob])
        #dob_list.append(dob)
        c+=1 
        if(c%60 == 0): time.sleep(3); print(c)
    
    df_bio = pd.DataFrame(bio, columns = ['link_1_x','hgt','dob'])
    return df_bio

def round_down_with_nan(series):
    return series.apply(lambda x: np.floor(x)-18 if pd.notna(x) else x)

def df_class(df):
    mapping = {6:'Pro', 5:'Pro', 4:'Sr', 3:'Jr', 2:'So', 1:'Fr', 0:'HS', -1:'HS' ,'--': np.nan}
    df['class'] = df['class'].map(mapping)
    return df['class'].values

#%% extract stats from real gm tables
stats,errors = all_leagues_aggregate()
stats[['ast/tov','blk_share','stl_share','pfr','ftr','3par']] = stats[['ast/tov','blk_share','stl_share','pfr','ftr','3par']].fillna(0)
stats[['ast/tov','blk_share','stl_share','pfr','ftr']] = stats[['ast/tov','blk_share','stl_share','pfr','ftr']].replace(np.inf, 10)
stats = stats[stats['MIN_x'] >= 1]

#%%convert stats into the desired format
file0 = pivot_data(stats.copy())
#do some age processing as well
file0 = file0.loc[(file0['mp']>=10) & (file0['GP']>=10)]

#%% get the dob and height for the players
bio = aggregate_age_dob(file0)

#%% merge age info with the stats and do final processing
file0 = file0.merge(bio, left_on=['link_1_x'], right_on=['link_1_x'])
file0['dob'] = pd.to_datetime(file0['dob'], format='mixed', errors='coerce')
file0['age'] = pd.to_datetime(file0['season'].astype(str) + '-10-1', format='%Y-%m-%d') - file0['dob']
file0['age'] = file0['age'] / pd.Timedelta(days=365.25)
file0['hgt'] = file0['hgt'].replace(0, np.nan)
file0['class'] = round_down_with_nan(file0['age'])
file0 = file0[file0['class'] <= 6]
file0['class'] = df_class(file0.copy())

file0['pid'] = file0['link_1_x'].str.split('/').str[4]
file0[['dunkar','rimar','rim%','midar','mid%','bpm']] = np.nan

final_data = file0[['player','pid','team','season','class','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%','blk_share',
                 'STL%','stl_share','pfr','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','bpm']]
final_data = final_data.apply(pd.to_numeric, errors='ignore')
final_data['team'] = final_data['team'].str.replace('-', ' ')
