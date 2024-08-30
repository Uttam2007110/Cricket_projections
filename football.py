# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 10:31:41 2024

@author: Subramanya.Ganti
"""

import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from functools import reduce
import requests
from bs4 import BeautifulSoup
import time
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'
input_file = f'{path}/football_clustering.xlsx'

def league_mapping(code):
    league_code = {
        9: 'Premier-League', 11: 'Serie-A', 12: 'La-Liga', 13: 'Ligue-1', 20: 'Bundesliga',
        10: 'Championship', 33: '2-Bundesliga', 17: 'Segunda-Division', 18: 'Seire-B', 60: 'Ligue-2',
        23: 'Eredivisie', 32: 'Primeira-Liga', 37: 'Belgian-Pro-League', 24: 'Serie-A', 31: 'Liga-MX', 21: 'Liga-Profesional-Argentina',
        676: 'UEFA-Euro', 685: 'Copa-America', 1: 'World-Cup'
        }
    try:
        league = league_code[code]
    except KeyError:
        print("unknown league was selected, premier league chosen as default")
        code = 9
        league = 'Premier-League'
    return code,league

def fbref_league_stats_year(season,code):
    code,league = league_mapping(code)
    table = pd.read_html(f'https://fbref.com/en/comps/{code}/{season}-{season+1}/{season}-{season+1}-{league}-Stats')
    return table

def fbref_team_ids(season,code):
    code,league = league_mapping(code)
    url = f'https://fbref.com/en/comps/{code}/{season}-{season+1}/{season}-{season+1}-{league}-Stats'
    data  = requests.get(url).text
    soup = BeautifulSoup(data,"html.parser")
    links = BeautifulSoup(data,"html.parser").select('th a')
    urls = [link['href'] for link in links]
    urls = list(set(urls))
    #print(urls)
    return urls

def prog_pass_carry(init_season,end_season,code):
    season = init_season; final = []
    while(season < end_season+1):
        table = fbref_league_stats_year(season,code)
        prog = table[2]
        prog.columns = prog.columns.droplevel(0)
        column_names = prog.columns.values
        column_names[27] = 'xG/90'; column_names[28] = 'xAG/90'; column_names[30] = 'npxG/90'; 
        prog.columns = column_names
        prog = prog[['Squad','90s','Poss','PKatt','xG','npxG','xAG','PrgC','PrgP']]
        prog['season'] = season
        
        if(season == init_season): final = prog
        else: final = pd.concat([final, prog], axis=0)
        season += 1
    return final

def turnover_calculation(init_season,end_season,code):
    season = init_season; final = []
    while(season < end_season+1):
        table = fbref_league_stats_year(season,code)
        points = table[0]
        touches = table[18]
        opp_touches = table[19]
        shooting = table[8]
        passing = table[12]
        tkl_int = table[17]
        attack = table[2]
        touches.columns = touches.columns.droplevel(0)
        #opp_touches.columns = opp_touches.columns.droplevel(0)
        shooting.columns = shooting.columns.droplevel(0)
        passing.columns = passing.columns.droplevel(0)
        tkl_int.columns = tkl_int.columns.droplevel(0)
        attack.columns = attack.columns.droplevel(0)
    
        #points = points[['Squad','MP','npxG','npxGA']]
        attack = attack[['Squad','MP','npxG']]
        touches2 = touches.copy()
        touches2 = touches2[['Squad','Touches']]
        passing['pass_tov'] = passing['Att'] - passing['Cmp'] - passing['Blocks']
        passing = passing[['Squad','pass_tov']]
        tkl_int = tkl_int[['Squad','Tkl+Int','Sh']]
        tkl_int = tkl_int.rename(columns={'Sh': 'blocked shots'})
        tkl_int['Squad'] = tkl_int['Squad'].str.replace('vs ','')
        shooting = shooting[['Squad','Sh']]
    
        tov = reduce(lambda x,y: pd.merge(x,y, on='Squad', how='outer'), [touches2, passing, tkl_int, shooting])
        tov['tov'] = tov['pass_tov'] + tov['Tkl+Int'] - tov['blocked shots'] + tov['Sh']
        tov['tov%'] = tov['tov']/(tov['tov'] + tov['Touches'])
    
        defend = table[3]
        opp_shooting = table[9]
        opp_passing = table[13]
        opp_tkl_int = table[16]
        opp_touches.columns = opp_touches.columns.droplevel(0)
        opp_shooting.columns = opp_shooting.columns.droplevel(0)
        opp_passing.columns = opp_passing.columns.droplevel(0)
        opp_tkl_int.columns = opp_tkl_int.columns.droplevel(0)
        defend.columns = defend.columns.droplevel(0)
        opp_touches2 = opp_touches.copy()
        defend = defend[['Squad','MP','npxG']]
        opp_touches2 = opp_touches2[['Squad','Touches']]
        opp_touches2 = opp_touches2.rename(columns={'Touches': 'Touches Against'})
        opp_passing['pass_tov'] = opp_passing['Att'] - opp_passing['Cmp'] - opp_passing['Blocks']
        opp_passing = opp_passing[['Squad','pass_tov']]
        opp_tkl_int = opp_tkl_int[['Squad','Tkl+Int','Sh']]
        opp_tkl_int = opp_tkl_int.rename(columns={'Sh': 'blocked shots'})
        opp_passing['Squad'] = opp_passing['Squad'].str.replace('vs ','')
        opp_shooting['Squad'] = opp_shooting['Squad'].str.replace('vs ','')
        opp_touches2['Squad'] = opp_touches2['Squad'].str.replace('vs ','')
        defend['Squad'] = defend['Squad'].str.replace('vs ','')
        opp_shooting = opp_shooting[['Squad','Sh']]
    
        tov_forced = reduce(lambda x,y: pd.merge(x,y, on='Squad', how='outer'), [opp_touches2, opp_passing, opp_tkl_int, opp_shooting])
        tov_forced['tov_forced'] = tov_forced['pass_tov'] + tov_forced['Tkl+Int'] - tov_forced['blocked shots'] + tov_forced['Sh']
        tov_forced['tov_forced%'] = tov_forced['tov_forced']/(tov_forced['tov_forced'] + tov_forced['Touches Against'])
    
    
        points = reduce(lambda x,y: pd.merge(x,y, on=['Squad','MP'], how='outer'), [attack, defend])
        column_names = points.columns.values
        column_names[2] = 'npxG'
        column_names[4] = 'npxGA'
        points = points[['Squad','MP','npxG','npxGA']]
        turnovers = reduce(lambda x,y: pd.merge(x,y, on='Squad', how='outer'), [points, tov, tov_forced])
        turnovers['Season'] = season
        turnovers = turnovers[['Squad','Season','MP','Touches','tov','tov%','npxG','Touches Against','tov_forced', 'tov_forced%','npxGA']]        
        turnovers['poss'] = turnovers['tov_forced%']/(turnovers['tov_forced%'] + turnovers['tov%'])
        turnovers['npxG/touch'] = 600*turnovers['npxG']/turnovers['Touches']
        turnovers['npxGA/touch'] = 600*turnovers['npxGA']/turnovers['Touches Against']
        
        if(season == init_season): final = turnovers
        else: final = pd.concat([final, turnovers], axis=0)
        season += 1
    return final

def player_cluster_data(season,code):
    print("Strated extracting club level data")
    team_list = fbref_team_ids(season,code)
    i=0; final = pd.DataFrame(columns=['Player','Club','Pos','Age','90s','touch%','Def Pen%','Def 3rd%', 'Mid 3rd%', 'Att 3rd%', 'Att Pen%','PrgC%','PrgP%','Sh%'])
    while(i<len(team_list)):
        #table = pd.read_html(f'https://fbref.com/en/squads/361ca564/2023-2024/Tottenham-Hotspur-Stats')
        #not more than 10 requests per min, buffer >6s is ideal
        time.sleep(10)
        table = pd.read_html('https://fbref.com'+team_list[i])
        shooting = table[4]
        passing = table[5]
        touches = table[9]
        tkl_int = table[8]
        
        club_name = 'https://fbref.com'+team_list[i]
        club_name = club_name.split("/")
        club_name = club_name[len(club_name)-1]
        club_name = club_name[:-6]
        club_name = club_name.replace('-',' ')
    
        touches.columns = touches.columns.droplevel(0)
        touches = touches[['Player','Pos','Age','90s','Touches','Def Pen','Def 3rd','Mid 3rd','Att 3rd','Att Pen','Carries','PrgC']]
        touches = touches.dropna(subset = ['Pos'])
        touches['PrgC%'] = touches['PrgC']/touches['Carries']
        touches['Att 3rd'] = touches['Att 3rd'] - touches['Att Pen']
        touches['Def 3rd'] = touches['Def 3rd'] - touches['Def Pen']
        touches['Def Pen%'] = touches['Def Pen']/touches['Touches']
        touches['Def 3rd%'] = touches['Def 3rd']/touches['Touches']
        touches['Mid 3rd%'] = touches['Mid 3rd']/touches['Touches']
        touches['Att 3rd%'] = touches['Att 3rd']/touches['Touches']
        touches['Att Pen%'] = touches['Att Pen']/touches['Touches']
        touches['touch%'] = (touches['Touches']/sum(touches['Touches']))*(38/touches['90s'])
    
        passing.columns = passing.columns.droplevel(0)
        column_names = passing.columns.values
        column_names[5] = 'Completions'
        passing = passing[['Player','Pos','Age','90s','Completions','PrgP']]
        passing = passing.dropna(subset = ['Pos'])
        passing['PrgP%'] = passing['PrgP']/passing['Completions']
        passing = passing[['Player','PrgP%']]
        
        shooting.columns = shooting.columns.droplevel(0)
        shooting = shooting[['Player','Pos','Sh']]
        shooting = shooting.dropna(subset = ['Pos'])
        shooting['Sh%'] = shooting['Sh']
        shooting = shooting[['Player','Sh%']]
    
        cluster = reduce(lambda x,y: pd.merge(x,y, on='Player', how='outer'), [touches, passing, shooting])
        cluster['Sh%'] = cluster['Sh%']/cluster['Touches']
        cluster['Club'] = club_name
        cluster = cluster[['Player','Club','Pos','Age','90s','touch%','Def Pen%','Def 3rd%', 'Mid 3rd%', 'Att 3rd%', 'Att Pen%','PrgC%','PrgP%','Sh%']]
        
        final = pd.concat([final, cluster], axis=0)
        print(club_name)
        i+=1
    print("Ended extracting club level data")
    return final

#team_list = fbref_team_ids(2023,9)
#prog = prog_pass_carry(2023,2023,11)
#turnovers = turnover_calculation(2017,2023,11)
#cluster = player_cluster_data(2023,9)

cluster_data = pd.read_excel(input_file,'Premier-League')
cluster_data = cluster_data.drop('Unnamed: 0', axis=1)
cluster_data = cluster_data.dropna()
cluster_data = cluster_data[cluster_data['90s']>10]

test = cluster_data[['touch%', 'Def Pen%', 'Def 3rd%','Mid 3rd%', 'Att 3rd%', 'Att Pen%', 'PrgC%', 'PrgP%', 'Sh%']]
pca = test.PCA(n_components=2)
model = KMeans(n_clusters=7)
model.fit(test)
predictions = model.predict(test)
test['Cluster'] = predictions
