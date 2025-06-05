# -*- coding: utf-8 -*-
"""
Created on Fri May 16 12:32:18 2025
similarity tests for nba draft prospects based on NCAA stats
@author: Subramanya.Ganti
"""
#%% imports
import numpy as np
import pandas as pd
import math
from scipy.stats import norm
from scipy.stats import skewnorm
from scipy.stats import skew
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

#%% team ratings
def team_ratings():
    i = 2008; team_ranking = []
    while(i<2026):
        team = pd.read_csv(f'C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/team/{i}_team_results.csv')
        team['season'] = i
        team = team[['rank','season','de Rank']]
        team_ranking.append(team)
        i+=1
    
    team_ranking = pd.concat(team_ranking)
    team_ranking.rename(columns = {'rank':'team','de Rank':'rating'}, inplace = True)
    #team_ranking = pd.pivot_table(team_ranking,values=['rating'],index=['team'],columns=['season'],aggfunc=np.sum)
    #team_ranking.columns = team_ranking.columns.droplevel(level=0)
    return team_ranking
    
team_ranking = team_ratings()

#%% player classification
def df_class(df):
    mapping = {'Sr': 4, 'Jr': 3, 'So': 2, 'Fr': 1, '--': np.nan}
    df['class'] = df['class'].map(mapping)
    df = df[df['class'].notna()]
    #df['class'] = stats.zscore(df['class'])
    return df

def height_adj(df):
    df[['Feet', 'Inches']] = df['height'].str.split('-', expand=True)
    df = df[df['Feet'].notna()]
    df = df[df['Inches'].notna()]
    df['hgt'] = 12*df['Feet'].astype(int) + df['Inches'].astype(int)
    df = df[df['hgt']>=60]
    return df

def iqr_column(df,category):
    df[category] = (df[category]-df[category].quantile(0.5))/(df[category].quantile(0.75) - df[category].quantile(0.25))
    return df

def extract_player_stats():
    headers = pd.read_csv('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/header.csv')
    i = 2010; p_stats = []; unadj_p_stats = []
    while(i<2026):
        data = pd.read_csv(f'C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/{i}.csv', names=headers.columns)
        data = data.loc[(data['mp']>=12) & (data['GP']>=10)]
        #data = df_class(data)
        data = height_adj(data)
        data['season'] = i
        
        data['FG/mp'] = (data['2PA'] + data['3PA']) / (data['mp'] * data['GP'])
        data['dunkar'] = data['dunkFGA']/(data['2PA']+data['3PA'])
        data['rimFGA'] = data['rimFGA'] - data['dunkFGA']
        data['rimFG'] = data['rimFG'] - data['dunkFG']
        data['rim%'] = data['rimFG']/(data['rimFGA']+0.00000000000001)       
        data['rimar'] = data['rimFGA']/(data['2PA']+data['3PA'])
        data['midar'] = data['midFGA']/(data['2PA']+data['3PA'])
        data['3par'] = data['3PA']/(data['2PA']+data['3PA'])
        data['ftr'] = data['FTA']/(data['2PA']+data['3PA'])
        
        data['rim%'] = data['rim%'].fillna(0)
        data['mid%'] = data['mid%'].fillna(0)
        data = data.loc[data['rimar'].isna() == False]
        data = data.loc[data['midar'].isna() == False]
        data = data.loc[data['ftr'].isna() == False]
        data = data.merge(team_ranking, left_on=['team','season'], right_on=['team','season'])
        
        data_adj = data[['player','pid','team','rating','season','class','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%',
                         'STL%','pfr','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','bpm']]
        
        unadj_p_stats.append(data_adj.copy())
        
        for x in ['usg','ORB%','DRB%','AST%','TO%','BLK%','STL%','pfr','ftr','dunkar','rimar','midar','3par',
                  'ast/tov','3P%','rim%','mid%','FT%','ORtg','drtg','bpm','mp']:
            data_adj = iqr_column(data_adj,x)
        p_stats.append(data_adj)
        i+=1
        
    p_stats = pd.concat(p_stats)
    unadj_p_stats = pd.concat(unadj_p_stats)
    p_stats = df_class(p_stats)
    unadj_p_stats = df_class(unadj_p_stats)
    
    p_stats = iqr_column(p_stats,'hgt')
    p_stats = iqr_column(p_stats,'class')
    #p_stats = iqr_column(p_stats,'3P%')
    #p_stats = iqr_column(p_stats,'FT%')
    #p_stats = iqr_column(p_stats,'rim%')
    #p_stats = iqr_column(p_stats,'mid%')
    #p_stats = iqr_column(p_stats,'TS%')
    #p_stats = iqr_column(p_stats,'class')
    #p_stats = iqr_column(p_stats,'rating')
    
    return p_stats,unadj_p_stats

data,player_stats = extract_player_stats()
data.reset_index(drop=True,inplace=True)
player_stats.reset_index(drop=True,inplace=True)
#player_stats = player_stats.merge(team_ranking, left_on=['team','season'], right_on=['team','season'])

#%% histogram of all player stats
player_stats.hist(figsize=(10, 8))  # Adjust figsize as needed
plt.tight_layout() # Adjust layout to prevent overlap
plt.show()

#%% covariance and inverse covariance for all the stats under consideration
data = data[['class', 'hgt', 'usg', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 'BLK%', 'STL%','pfr', 'ftr','FT%', 'dunkar', 'rimar', 
             'rim%', 'midar', 'mid%', '3par', '3P%','ORtg','drtg','bpm','mp']]

correlation_matrix = data.corr()
"""
year_pivot = pd.pivot_table(player_stats,values=['class','hgt', 'GP', 'mp', 'usg','TS%', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 
                                                 'BLK%', 'STL%','pfr', 'ftr','FT%', 'dunkar', 'rimar', 'rim%', 'midar', 'mid%', '3par', 
                                                 '3P%','ORtg', 'drtg','bpm'],index=['season'],aggfunc='mean')
"""

#%% mahlanobis distance based player comps
def distance(name, yr, full_matrix, data, print_df):
    # Computes the Mahalanobis distance for a given player to all other player.
    cov = np.ma.cov(np.ma.masked_invalid(data), rowvar=False)
    
    #custom weightage to specific factors, ast/tov, STL%
    #cov[:,7] = cov[:,7] * 2
    #cov[7,:] = cov[7,:] * 2
    cov[0,0] = cov[0,0] * 2
    cov[1,1] = cov[1,1] * 2
    cov[7,7] = cov[7,7] * 2
    cov[22,22] = cov[22,22] * 2
    
    #inverse covaiance matrix
    invcov = np.linalg.inv(cov)\
    
    # Get player data
    player_data = full_matrix.loc[(full_matrix['player']==name)&(full_matrix['season']==yr)]
    player_index = player_data.index[0]
    player = data.iloc[player_index]
    if(print_df == 1): print(player_data.squeeze())
    
    # Mask invalid values in the player vector
    pvec = np.ma.masked_invalid(np.array(player))

    min_player = None
    min_val = None
    min_id = None
    
    dist_array = []

    for i in range(len(data)):
        # Get the ith player season
        cdata = data.iloc[i]

        # Ignore the current player season
        if i == player_index:
            dist_array.append(0)
            continue

        # Mask invalid values
        cvec = np.ma.masked_invalid(np.array(cdata))

        # Find difference between x and y
        delta = pvec - cvec

        # Find Mahalanobis distance
        dist = np.sqrt(np.einsum('i,ij,j', delta, invcov, delta))
        dist_array.append(dist)
        #dist = np.sqrt(np.einsum('nj,jk,nk->n', delta, invcov, delta))[0]

        # Check to see if current distance is smallest, if so, keep it.
        if min_id == None or min_val > dist:
            min_player = full_matrix.iloc[i]
            min_val = dist
            min_id = 0

    # Print out the most similar season
    #print('Most similar: dist: {}\n{}'.format(min_val, min_player))
    full_matrix['mdist'] = dist_array
    full_matrix = full_matrix[['player','team','season','bpm','mdist','pid']]
    full_matrix['score'] = 1/(full_matrix['mdist']*full_matrix['mdist'])
    full_matrix = full_matrix.sort_values(by=['score'], ascending=False)
    full_matrix = full_matrix.loc[full_matrix['score'] >= (full_matrix[1:]['score'].mean()+4*full_matrix[1:]['score'].std())]
    return full_matrix

#%% mapping nba stats
nba_stats = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/nba_stats.xlsx','DARKO')
"""
nba_stats = pd.pivot_table(nba_stats,values=['dpm'],index=['player_name'],columns=['season'],aggfunc=np.sum)
nba_stats.columns = nba_stats.columns.droplevel(0)
nba_stats['VORP/S'] =  nba_stats.max(axis=1, numeric_only=True)
nba_stats['S'] =  nba_stats.count(axis=1, numeric_only=True)
nba_stats['S'] -= 1
#nba_stats['VORP/S'] = 82 * nba_stats['VORP'] / nba_stats['G']
nba_stats.reset_index(inplace=True)
"""
mapping = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/nba_stats.xlsx','mapping DARKO')                   
nba_stats = pd.merge(nba_stats, mapping, left_on='player_name', right_on='player_name', how='left')
del mapping

nba_stats['age_adj'] = nba_stats['age'].round()
nba_stats = nba_stats[['player_name','season_x','age_adj','dpm','pid']]
nba_stats = nba_stats[nba_stats['pid'].notna()]

age_curve = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/nba_stats.xlsx','age curve')

import itertools
combinations = list(itertools.product(nba_stats['player_name'].unique(), range(19,40)))
combinations = pd.DataFrame(combinations, columns=['player_name', 'age_adj'])
combinations = combinations.merge(nba_stats, left_on=['player_name','age_adj'], right_on=['player_name','age_adj'], how='outer')
combinations = combinations.merge(age_curve, left_on=['age_adj'], right_on=['age'])

prev = np.nan; prev_name = ""; prev_pid = np.nan
for x in combinations.values:
    #print(x)
    if(pd.isna(x[4]) and pd.notna(prev) and (prev_name == x[0])):  
        combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'dpm'] = prev + x[6]
        combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'pid'] = prev_pid
        prev_name = x[0]
        prev = prev + x[6]
    else:
        prev_name = x[0]
        prev = x[3]
        prev_pid = x[4]
        
nba_stats = combinations.copy()
#nba_stats = nba_stats.groupby('player_name')['dpm'].apply(lambda x: x.nlargest(5))
nba_stats = nba_stats[nba_stats['dpm'] >= -4]
del combinations; del x; del prev; del prev_name; del prev_pid

#%% call the distance function
name = "Cooper Flagg"; p_season = 2025
pdist = distance(name, p_season, player_stats.copy(), data, 1)
pdist = pdist.drop_duplicates(subset=['player'], keep='first')
pdist = pdist.loc[(pdist['season']<2025) | ((pdist['player']==name) & (pdist['season']==p_season))]
pdist.reset_index(inplace=True)

#pdist = pd.merge(pdist, nba_stats[['pid','VORP/S','S']], left_on='pid', right_on='pid', how='left')
#pdist = pdist.drop(columns=['pid'])
comps = nba_stats[nba_stats['pid'].isin(pdist['pid'])]
nba_comps = len(comps['pid'].unique())
comps = comps.groupby('player_name')['dpm'].apply(lambda x: x.nlargest(5))
comps = comps.to_list() + [-4] * (len(pdist)-nba_comps) * 5

print("NBA Rate",1-skewnorm.cdf(-3, a=skew(comps) ,loc=np.mean(comps), scale=np.std(comps)))
print("Starter NBA Rate",1-skewnorm.cdf(-1, a=skew(comps), loc=np.mean(comps), scale=np.std(comps)))
print("Star NBA Rate",1-skewnorm.cdf(1, a=skew(comps), loc=np.mean(comps), scale=np.std(comps)))
print("bpm gap over comps",pdist['bpm'].values[0]-pdist['bpm'].quantile(0.75)) #pdist['bpm'].mean())

qdist = nba_stats[nba_stats['pid'].isin(pdist['pid'])]
qdist = pd.pivot_table(qdist,values=['dpm'],index=['player_name'],columns=['season_x'],aggfunc=np.sum)
qdist.columns = qdist.columns.droplevel(0)
qdist['VORP/S'] =  qdist.max(axis=1, numeric_only=True)
qdist['S'] =  qdist.count(axis=1, numeric_only=True)
qdist['S'] -= 1
qdist.reset_index(inplace=True)
qdist = qdist[['player_name','VORP/S','S']]
qdist = qdist.loc[qdist['S'] > 1]

print("Comp 1 - ",qdist.loc[qdist['VORP/S'] == qdist['VORP/S'].nlargest(2)[-1:].values[0],'player_name'].values[0])
print("Comp 2 - ",qdist.loc[qdist['VORP/S'] == qdist['VORP/S'].nlargest(math.ceil(0.15*len(qdist)))[-1:].values[0],'player_name'].values[0])
print("Comp 3 - ",qdist.loc[qdist['VORP/S'] == qdist['VORP/S'].nlargest(math.ceil(0.25*len(qdist)))[-1:].values[0],'player_name'].values[0])
print("Comp 4 - ",qdist.loc[qdist['VORP/S'] == qdist['VORP/S'].nlargest(math.ceil(0.50*len(qdist)))[-1:].values[0],'player_name'].values[0])
print("Comp 5 - ",qdist.loc[qdist['VORP/S'] == qdist['VORP/S'].nlargest(math.ceil(0.75*len(qdist)))[-1:].values[0],'player_name'].values[0])
del qdist; del name; del p_season; del comps

#%% distance func for a list
def mdist_list(year, nba_stats, p_stats):
    list_p = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/nba_stats.xlsx',f'{year}')
    seniors_p = p_stats.loc[(p_stats['season']==year)&(p_stats['class']==4)&(p_stats['bpm']>=5)]
    names_list = list_p['Player'].to_list() + seniors_p['player'].to_list()
    names_list = list(set(names_list))
    #names_list.sort()
    names_list = p_stats[p_stats['player'].isin(names_list)]
    names_list = names_list.loc[names_list['season']==year]
    #names_list = names_list.loc[(names_list['season']<=year)&(names_list['season']>year-5)]   
    #names_list = names_list[0:10]
    
    result = [['player','team','season','comps','bpm','bpm gap','made NBA','role player','star','comp 1','comp 2','comp 3','comp 4','comp 5']]
    
    for x,y in names_list[['player','season']].values:
        try:
            dist = distance(x, y, p_stats.copy(), data, 0)
            dist = dist.loc[(dist['season']<2025) | ((dist['player']==x) & (dist['season']==y))]
            dist.reset_index(inplace=True)
            #dist = pd.merge(dist, nba_stats[['pid','VORP/S','S']], left_on='pid', right_on='pid', how='left')
            #dist = dist.drop(columns=['pid'])
            comps = nba_stats[nba_stats['pid'].isin(dist['pid'])]
            comps = comps['dpm'].to_list() + [-3.64,-2.89,-2.25,-1.71,-1.29,-0.97,-0.77,-0.67,-0.68,-0.8,-1.03,-1.36,-1.81,-2.36,-3.03,-3.8,-4.68] * (len(dist)-len(comps['pid'].unique()))
            
            team = dist['team'][0]
            bpm = dist['bpm'][0]
            comps_num = len(dist)
            bpm_gap = bpm - dist['bpm'].quantile(0.75)
            made_nba = 1-skewnorm.cdf(-3, a=skew(comps), loc=np.mean(comps), scale=np.std(comps))
            vorp_1 = 1-skewnorm.cdf(-1, a=skew(comps), loc=np.mean(comps), scale=np.std(comps))
            vorp_2 = 1-skewnorm.cdf(1, a=skew(comps), loc=np.mean(comps), scale=np.std(comps))
            #median_vorp = (dist['VORP/S']*dist['S']).sum()/dist['S'].sum()
            
            dist2 = nba_stats[nba_stats['pid'].isin(dist['pid'])]
            dist2 = pd.pivot_table(dist2,values=['dpm'],index=['player_name'],columns=['season_x'],aggfunc=np.sum)
            dist2.columns = dist2.columns.droplevel(0)
            dist2['VORP/S'] =  dist2.max(axis=1, numeric_only=True)
            dist2['S'] =  dist2.count(axis=1, numeric_only=True)
            dist2['S'] -= 1
            dist2.reset_index(inplace=True)
            dist2 = dist2[['player_name','VORP/S','S']]
            dist2 = dist2.loc[dist2['S'] > 0]
            
            if(len(dist2) < 5):
                c1 = ""
                c2 = ""
                c3 = ""
                c4 = ""
                c5 = ""
            elif(len(dist2) < 10):
                c1 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(1)[-1:].values[0],'player_name'].values[0]
                c2 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(2)[-1:].values[0],'player_name'].values[0]
                c3 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(3)[-1:].values[0],'player_name'].values[0]
                c4 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(4)[-1:].values[0],'player_name'].values[0]
                c5 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(5)[-1:].values[0],'player_name'].values[0]
            else:
                c1 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(2)[-1:].values[0],'player_name'].values[0]
                c2 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(int(0.15*len(dist2)))[-1:].values[0],'player_name'].values[0]
                c3 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(int(0.25*len(dist2)))[-1:].values[0],'player_name'].values[0]
                c4 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(int(0.50*len(dist2)))[-1:].values[0],'player_name'].values[0]
                c5 = dist2.loc[dist2['VORP/S'] == dist2['VORP/S'].nlargest(int(0.75*len(dist2)))[-1:].values[0],'player_name'].values[0]
            
            result.append([x, team, y, comps_num, bpm, bpm_gap, made_nba, vorp_1, vorp_2, c1, c2, c3, c4, c5])
            print(x,y)
            
        except IndexError:
            print(f"*******error with {x},{y}*******")
            result.append([x, "NA", y, 0, 0, 0, 0, 0, 0, 0, "", "", "", "", ""])
        
    
    result = pd.DataFrame(result)
    result.columns = result.iloc[0];result = result.drop(0)
    result = result.apply(pd.to_numeric, errors='ignore')
    result = result.sort_values(by=['role player', 'player'], ascending=[False, True])
    result = result.drop_duplicates(subset=['player'], keep='first')
    return result

draft_list = mdist_list(2025, nba_stats.copy(), player_stats.copy())
