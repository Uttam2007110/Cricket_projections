# -*- coding: utf-8 -*-
"""
Created on Wed Jul  2 16:22:28 2025
code to extract NCAA basketball stats from RealGM
@author: Subramanya.Ganti
"""

import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import datetime

start_season = 2003
end_season = 2007
final_stats = []

#%% player stats
def extract_table_data(season,data_type,data_filter,player_class):    
    if(data_filter == ''): 
        url = f"https://basketball.realgm.com/ncaa/team-stats/{season}/Totals/Team_Totals/0"
    else: url = f"https://basketball.realgm.com/ncaa/stats/{season}/{data_type}/{data_filter}/{player_class}/Season/All/points/desc/1/"
    
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

def derive_player_stats_league(season):
    class_list = ['Fr','So','Jr','Sr']
    totals = []; advanced = []
    for c in class_list:
        totals_class = extract_table_data(season,'Totals','All',c)
        #totals_class['class'] = c
        totals.append(totals_class)
        advanced_class = extract_table_data(season,'Advanced_Stats','All',c)
        advanced_class['class'] = c
        advanced.append(advanced_class)
    
    totals = pd.concat(totals)
    advanced = pd.concat(advanced)
    team = extract_table_data(season,'Totals','','')
    team = team[['GP','MIN','STL','BLK','link_1']]
    team['team_full'] = team['link_1'].str.split('/').str[5]
    
    p_stats = advanced.merge(totals, left_on=['Player','Team','link_1','link_2'], right_on=['Player','Team','link_1','link_2'])
    p_stats['team_full'] = p_stats['link_2'].str.split('/').str[5]
    
    p_stats = p_stats.merge(team, left_on=['team_full'], right_on=['team_full'])
    p_stats['pid'] = p_stats['link_1_x'].str.split('/').str[4]
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
    
    #p_stats = p_stats[['Player','TS%','ORB%', 'DRB%', 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%','ORtg','DRtg','GP_x','mp','3par',
    #'blk_share','stl_share','ast/tov','ftr','3P%','FT%','link_1_x','MIN_x','season']]
    p_stats[['hgt','dunkar','rimar','rim%','midar','mid%','bpm']] = np.nan
    p_stats = p_stats.rename(columns={'Player': 'player', 'team_full': 'team', 'GP_x':'GP', 'USG%':'usg', 'TOV%':'TO%', 'DRtg':'drtg'})
    
    p_stats = p_stats[['player','pid','team','season','class','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%','blk_share',
                     'STL%','stl_share','pfr','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','bpm']]
    return p_stats

while(start_season < end_season+1):
    stats = derive_player_stats_league(start_season)
    final_stats.append(stats)
    start_season += 1
    
final_stats = pd.concat(final_stats)
final_stats = final_stats.loc[(final_stats['mp']>=10) & (final_stats['GP']>=10)]
final_stats['team'] = final_stats['team'].str.replace('-', ' ')
final_stats['pid'] = final_stats['pid'] * -1

#%% player height info
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

def aggregate_age_dob(df):
    print("unique entries",len(df['link'].unique()))
    bio = []; c = 0
    for links in df['link'].unique():
        hgt,dob = player_dob_height(links)
        bio.append([links,hgt,dob])
        #dob_list.append(dob)
        c+=1 
        if(c%60 == 0): time.sleep(3); print(c)
    
    df_bio = pd.DataFrame(bio, columns = ['link','hgt','dob'])
    return df_bio

old_names = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/foreign_players.xlsx','ncaa')
old_names = old_names[['player','pid']]
old_names = old_names.drop_duplicates()
old_names['pid'] = old_names['pid'] * -1
old_names['link'] = old_names['player']
old_names['link'] = old_names['link'].str.replace('.','')
old_names['link'] = old_names['link'].str.replace(' ','-')
#player/Kevin-Durant/Summary/34
old_names['link'] = 'player/' + old_names['link'] + '/Summary/' + old_names['pid'].astype(str)

info = aggregate_age_dob(old_names)
