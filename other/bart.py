# -*- coding: utf-8 -*-
"""
Created on Fri May 16 12:32:18 2025
similarity tests for nba draft prospects based on NCAA stats
@author: Subramanya.Ganti
"""
#%% imports
import numpy as np
import pandas as pd
from scipy import stats

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
headers = pd.read_csv('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/header.csv')

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
    return df

def iqr_column(df,category):
    df[category] = (df[category]-df[category].quantile(0.5))/(df[category].quantile(0.75) - df[category].quantile(0.25))
    return df

def extract_player_stats():
    i = 2010; p_stats = []; unadj_p_stats = []
    while(i<2026):
        data = pd.read_csv(f'C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/{i}.csv', names=headers.columns)
        data = data.loc[(data['mp']>=12) & (data['GP']>=10)]
        #data = df_class(data)
        data = height_adj(data)
        data['season'] = i
        
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
        
        data_adj = data[['player','pid','team','rating','season','class','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%','STL%','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','porpag']]
        
        unadj_p_stats.append(data_adj.copy())
        
        for x in ['usg','ORB%','DRB%','AST%','TO%','BLK%','STL%','ftr','dunkar','rimar','midar','3par','ast/tov','3P%','rim%','mid%','FT%','ORtg','drtg']:
            data_adj = iqr_column(data_adj,x)
        p_stats.append(data_adj)
        i+=1
        
    p_stats = pd.concat(p_stats)
    unadj_p_stats = pd.concat(unadj_p_stats)
    p_stats = df_class(p_stats)
    unadj_p_stats = df_class(unadj_p_stats)
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

#%% covariance and inverse covariance for all the stats under consideration
data = data[['class', 'hgt', 'usg', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 'BLK%', 'STL%', 'ftr','FT%', 'dunkar', 'rimar', 'rim%', 'midar', 'mid%', '3par', '3P%','ORtg','drtg']]

correlation_matrix = data.corr()

year_pivot = pd.pivot_table(player_stats,values=['class','hgt', 'GP', 'mp', 'usg','TS%', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 
                                                 'BLK%', 'STL%', 'ftr','FT%', 'dunkar', 'rimar', 'rim%', 'midar', 'mid%', '3par', 
                                                 '3P%','ORtg', 'drtg'],index=['season'],aggfunc='mean')

#%% mahlanobis distance based player comps
def distance(name, yr, full_matrix, data):
    # Computes the Mahalanobis distance for a given player to all other player.
    cov = np.ma.cov(np.ma.masked_invalid(data), rowvar=False)
    invcov = np.linalg.inv(cov)\
    
    # Get player data
    player_data = full_matrix.loc[(full_matrix['player']==name)&(full_matrix['season']==yr)]
    player_index = player_data.index[0]
    player = data.iloc[player_index]
    print(player_data.squeeze())
    
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
    full_matrix = full_matrix[['player','team','season','porpag','mdist']]
    full_matrix['score'] = 1/(full_matrix['mdist']*full_matrix['mdist'])
    full_matrix = full_matrix.sort_values(by=['score'], ascending=False)
    full_matrix = full_matrix.loc[full_matrix['score'] >= (full_matrix[1:]['score'].mean()+5*full_matrix[1:]['score'].std())]
    return full_matrix

#%% mapping nba stats
nba_stats = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/nba_stats.xlsx','Sheet1')
nba_stats = pd.pivot_table(nba_stats,values=['VORP'],index=['Player'],columns=['season'],aggfunc=np.sum)
nba_stats.columns = nba_stats.columns.droplevel(0)
nba_stats['VORP'] =  nba_stats.sum(axis=1, numeric_only=True)
nba_stats['seasons'] =  nba_stats.count(axis=1, numeric_only=True)
nba_stats['seasons'] -= 1
nba_stats['VORP/season'] = nba_stats['VORP'] / nba_stats['seasons']
nba_stats.reset_index(inplace=True)
                                 
#names = player_stats[['player','pid']].drop_duplicates(subset=['player'])
#names = names.merge(nba_stats, left_on='player', right_on='Player')

#%% call the distance function
pdist = distance("Egor Demin", 2025, player_stats.copy(), data)

pdist = pd.merge(pdist, nba_stats[['Player','seasons','VORP/season']], left_on='player', right_on='Player', how='left')
pdist = pdist.drop(columns=['Player'])

print("Success Rate",pdist['seasons'].count()/len(pdist))