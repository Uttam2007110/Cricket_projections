# -*- coding: utf-8 -*-
"""
Created on Fri May 16 12:32:18 2025
similarity tests for nba draft prospects based on NCAA stats
@author: Subramanya.Ganti
"""
#%% imports
import numpy as np
import pandas as pd

import itertools
import math
import scipy.stats
from scipy import stats
from scipy.stats import norm
from scipy.stats import skew
from scipy.optimize import fsolve
from scipy.spatial.distance import cdist

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

#path = "C:/Users/GF63/Desktop/cricket/excel/bart"
path = "C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart"

latest_season = 2025

#%% team ratings
def team_ratings():
    i = 2008; team_ranking = []
    while(i<latest_season+1):
        team = pd.read_csv(f'{path}/team/{i}_team_results.csv')
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
team_ranking['adj_rating'] = norm.ppf(team_ranking['rating'], loc=0.494, scale=0.255)

#%% player classification
def data_imputation_08_09(df):
    imputer = IterativeImputer()
    imputed = imputer.fit_transform(df)
    df_imputed = pd.DataFrame(imputed, columns=df.columns)
    return df_imputed

def df_class(df):
    mapping = {'Pro': 5, 'Sr': 4, 'Jr': 3, 'So': 2, 'Fr': 1, 'HS': 0, '--': np.nan}
    df['class'] = df['class'].map(mapping)
    df = df[df['class'].notna()]
    #df['class'] = stats.zscore(df['class'])
    return df

def df_role(df):
    mapping = {'Pure PG': 1, 'Combo G': 1.5, 'Wing F': 2, 'Wing G': 1.75, 'Stretch 4': 2.5, 'Scoring PG': 1.25, 'PF/C': 2.75, 'C': 3}
    df['role'] = df['role'].map(mapping)
    #df = df[df['role'].notna()]
    return df

def height_adj(df):
    df[['Feet', 'Inches']] = df['height'].str.split('-', expand=True)
    #df = df[df['Feet'].notna()]
    #df = df[df['Inches'].notna()]
    df['Feet'] = pd.to_numeric(df['Feet'], errors='coerce', downcast='integer')
    df['Inches'] = pd.to_numeric(df['Inches'], errors='coerce', downcast='integer')
    df['hgt'] = 12*df['Feet'] + df['Inches'] #.astype(int)
    df = df[df['hgt']>=60]
    return df

def log_adjust(df,category):
    df[category] = np.log(df[category])
    df[category] = df[category].replace(-np.inf, np.nan)
    min_value = df[category].min(skipna=True)
    df[category] = df[category].replace(np.nan, min_value)
    return df

def iqr_column(df,category):
    df[category] = (df[category]-df[category].quantile(0.5))/(df[category].quantile(0.75) - df[category].quantile(0.25))
    return df

def international_stats_adjustments():
    df = pd.read_excel(f'{path}/foreign_players.xlsx','final')
    df['TS%'] = df['TS%']*100
    
    df['mp'] = 10.2 + 25.7*(df['mp'].rank(pct=True))
    df['usg'] = df['usg'] + 1.5
    df['AST%'] = df['AST%'] + 0.5
    df['TO%'] = df['TO%'] + 1.8
    df['ast/tov'] = df['ast/tov'] - 0.1
    df['ftr'] = df['ftr'] + 0.04
    #df['drtg'] = 92.85 + 21.247*(df['drtg'].rank(pct=True))
    #df['ORtg'] = 80.391 + 40.954*(df['ORtg'].rank(pct=True))
    df['drtg'] = df['drtg'] - 7
    df['ORtg'] = df['ORtg'] - 2.5
    df['BLK%'] = df['BLK%'] * (1.9/1.4)
    
    factor = 1.1
    df['mp'] = df['mp'] * factor
    df['ORB%'] = df['ORB%'] * factor
    df['DRB%'] = df['DRB%'] * factor
    df['AST%'] = df['AST%'] * factor
    df['TO%'] = df['TO%'] * factor
    df['ast/tov'] = df['ast/tov'] * factor
    df['BLK%'] = df['BLK%'] * factor
    df['STL%'] = df['STL%'] * factor
    df['ftr'] = df['ftr'] * factor
    df['ORtg'] = df['ORtg'] * (factor**0.5)
    df['drtg'] = df['drtg'] / (factor**0.5)    
    return df

def pre_08_ncaa():
    df = pd.read_excel(f'{path}/foreign_players.xlsx','ncaa')
    #darren yates 2004 season has a ast/tov of infinity
    df['ast/tov'] = df['ast/tov'].replace(np.inf, 11)
    df['TS%'] = df['TS%']*100
    return df

def bpm_estimate(df):
    df['bpm'] = -0.144113373288963 + \
                +0.099780626377398  * df['mp'] + \
                -0.033812208445742  * df['usg'] + \
                -0.0794753081021516 * df['TS%'] + \
                +0.0938757627410997 * df['ORB%'] + \
                -0.0198264884876267 * df['DRB%'] + \
                +0.0498729810633044 * df['AST%'] + \
                +0.05202239249302   * df['TO%'] + \
                +0.20818594724229   * df['ast/tov'] + \
                +0.384495013690059  * df['BLK%'] + \
                +0.613544025847017  * df['STL%'] + \
                -0.161067815268391  * df['ftr'] + \
                -1.17542648511186   * df['FT%'] + \
                +2.30629767192219   * df['3par'] + \
                +0.599363695211862  * df['3P%'] + \
                +0.236841287583253  * df['ORtg'] + \
                -0.246965207036096  * df['drtg']
    return df

def height_estimate(df):
    df['hgt'] = +74.0115813626499 + \
                +0.0242139494814847 * df['TS%'] + \
                +0.154491122634659  * df['ORB%'] + \
                +0.17303148969203   * df['DRB%'] + \
                -0.151160612178076  * df['AST%'] + \
                +0.343528125104708  * df['BLK%'] + \
                -0.952915225005203  * df['3par']
    return df

def extract_player_stats():
    headers = pd.read_csv(f'{path}/header.csv')   
    internationals = international_stats_adjustments()
    pre_2008 = pre_08_ncaa()
    
    #estimate the height and bpm for player stats pulled from RealGM
    internationals = bpm_estimate(internationals)
    pre_2008 = bpm_estimate(pre_2008)
    #pre_2008 = height_estimate(pre_2008)
    
    i = 2003; p_stats = []; unadj_p_stats = []
    while(i<latest_season+1):
        if(i < 2008):
            data_adj = pre_2008[pre_2008['season']==i]
        else:
            data = pd.read_csv(f'{path}/{i}.csv', names=headers.columns)
            
            data['blocks']  = data['blk'] * data['GP']
            data['steals']  = data['stl'] * data['GP']
            data['minutes']  = data['mp'] * data['GP']
            team_bs = pd.pivot_table(data,values=['blocks','steals','minutes'],index=['team'],aggfunc=np.sum)
            team_bs['minutes'] = team_bs['minutes']/200
            team_bs['blocks'] = team_bs['blocks']/team_bs['minutes']
            team_bs['steals'] = team_bs['steals']/team_bs['minutes']
            team_bs = team_bs.reset_index()
            data = data.merge(team_bs, left_on='team', right_on='team')
            
            data = data.loc[(data['mp']>=10) & (data['GP']>=10)]
            data['blk_share'] = (data['blk']*40/data['mp'])/data['blocks_y']
            data['stl_share'] = (data['stl']*40/data['mp'])/data['steals_y']
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
            
            #data['rim%'] = data['rim%'].fillna(0)
            #data['mid%'] = data['mid%'].fillna(0)
            #data = data.loc[data['rimar'].isna() == False]
            #data = data.loc[data['midar'].isna() == False]
            #data = data.loc[data['ftr'].isna() == False]
            
            data_adj = data[['player','pid','team','season','class','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%','blk_share',
                             'STL%','stl_share','pfr','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','bpm']]
        
        #add internationals data
        data_adj = pd.concat([data_adj, internationals[internationals['season']==i]])
        unadj_p_stats.append(data_adj.copy())
        
        for x in ['ORB%','DRB%','BLK%','blk_share','STL%','stl_share','dunkar','AST%','TO%','ast/tov','mp']:
            data_adj = log_adjust(data_adj,x)
        for x in ['usg','ftr','rimar','midar','3par','3P%','rim%','mid%','FT%','ORtg','drtg','bpm','pfr']:
            data_adj = iqr_column(data_adj,x)
        p_stats.append(data_adj)
        i+=1
        
    p_stats = pd.concat(p_stats)
    unadj_p_stats = pd.concat(unadj_p_stats)
    p_stats = df_class(p_stats.copy())
    unadj_p_stats = df_class(unadj_p_stats.copy())
    #p_stats = df_role(p_stats)
    #unadj_p_stats = df_role(unadj_p_stats)
    
    
    p_stats['hgt'] = p_stats['hgt'] - 60
    p_stats = iqr_column(p_stats,'hgt')
    p_stats = log_adjust(p_stats,'class')
    #p_stats = log_adjust(p_stats,'role')
    
    return p_stats,unadj_p_stats

data,player_stats = extract_player_stats()
data.reset_index(drop=True,inplace=True)
player_stats.reset_index(drop=True,inplace=True)

data = data.merge(team_ranking, left_on=['team','season'], right_on=['team','season'], how='left')
data.drop('rating', axis=1, inplace=True)

#%% fix pids of players in both real GM and bart torvik
mapping = pd.read_excel(f'{path}/nba_stats.xlsx','mapping DARKO')
mapping = mapping[['pid','pid2']]
mapping = mapping.rename(columns={'pid': 'pid2', 'pid2': 'pid'})
mapping = mapping.dropna()
player_stats = player_stats.merge(mapping, left_on='pid', right_on='pid', how='left')

player_stats['pid'] = player_stats['pid2'].fillna(player_stats['pid'])
del player_stats['pid2']; del mapping

#other corrections
player_stats.loc[((player_stats['pid']==50678)&(player_stats['season']==2018)),'player'] = 'Ja Morant'
player_stats.loc[((player_stats['player']=='Lachlan Olbrich')&(player_stats['pid']==-186799)),'pid'] = 76638

#%% aggregate weighted career level data instead of single season (not implemented yet)
def pivot_data(df,df2):
    mapping = {0:5, 1:5, 2:3, 3:1.5, 4:0.5}
    df['weight'] = df['class'].map(mapping)
    df['weight'] *= df['mp'] * df['GP']
    pivot = df.pivot_table(values=['class', 'hgt', 'mp', 'usg', 'TS%', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 'BLK%', 'blk_share','STL%',
                                   'stl_share', 'pfr', 'ftr', 'FT%', 'dunkar', 'rimar', 'rim%','midar', 'mid%', '3par', '3P%','ORtg', 'drtg', 'bpm'],
                              index=['player','pid'], 
                              aggfunc=lambda rows: np.average(rows, weights=df.loc[rows.index, 'weight']))

    gp = df.pivot_table(values=['GP'], index=['player','pid'], aggfunc="sum")
    team = df.pivot_table(values=['team'], index=['player','pid'], aggfunc=lambda x: ' '.join(x.unique()))

    team = team.reset_index()
    gp = gp.reset_index()
    pivot = pivot.reset_index()

    df0 = team.merge(gp, left_on=['player','pid'], right_on=['player','pid'])
    df0 = df0.merge(pivot, left_on=['player','pid'], right_on=['player','pid'])
    return df0

#career_stats = pivot_data(player_stats.copy(),data.copy())

#%% histogram of all player stats
data.hist(figsize=(10, 8))  # Adjust figsize as needed
plt.tight_layout() # Adjust layout to prevent overlap
plt.show()

#%% correlation matrix for all the stats under consideration
data = data[['class', 'hgt', 'usg', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 'BLK%','blk_share','STL%','stl_share', 'ftr','FT%', 
             #'dunkar', 'rimar', 'rim%', 'midar', 'mid%', 
             '3par', '3P%','ORtg','drtg','bpm','mp','adj_rating']]

data = data_imputation_08_09(data.copy())
correlation_matrix = data.corr()
"""
year_pivot = pd.pivot_table(player_stats,values=['class','hgt', 'GP', 'mp', 'usg','TS%', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 
                                                 'BLK%', 'STL%', 'ftr','FT%', 'dunkar', 'rimar', 'rim%', 'midar', 'mid%', '3par', 
                                                 '3P%','ORtg', 'drtg','bpm'],index=['season'],aggfunc='mean')
"""

#%% mahlanobis distance based player comps
def distance(name, yr, full_matrix, data, print_df):
    # Computes the Mahalanobis distance for a given player to all other player.
    cov = np.ma.cov(np.ma.masked_invalid(data), rowvar=False)
    
    #custom weightage to specific factors, ast/tov, STL%
    #cov[18,18] = cov[18,18] * 2
    
    #inverse covaiance matrix
    invcov = np.linalg.inv(cov)\
    
    # Get player data
    if(name == "Jalen Johnson"): #multiple jalen johnsons exist
        player_data = full_matrix.loc[(full_matrix['pid']==73238)&(full_matrix['season']==yr)]
    else:
        player_data = full_matrix.loc[(full_matrix['player']==name)&(full_matrix['season']==yr)]
    player_index = player_data.index[0]
    player = data.iloc[player_index]
    #if(print_df == 1): print(player_data.squeeze())
    
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
    full_matrix = full_matrix[['player','team','season','hgt','bpm','mdist','pid']]
    full_matrix['score'] = 1/(full_matrix['mdist']*full_matrix['mdist']) #np.exp(-1*full_matrix['mdist']*full_matrix['mdist'])
    full_matrix = full_matrix.sort_values(by=['score'], ascending=False)
    full_matrix = full_matrix.loc[full_matrix['score'] >= (full_matrix[1:]['score'].mean()+4*full_matrix[1:]['score'].std())]  #3.75 or 4
    return full_matrix

#%% function to map nba stats
def extract_nba_stats(year):
    nba_stats_y = pd.read_excel(f'{path}/nba_stats.xlsx','DARKO')
    mapping = pd.read_excel(f'{path}/nba_stats.xlsx','mapping DARKO')
    nba_stats_y = pd.merge(nba_stats_y, mapping, left_on='player_name', right_on='player_name', how='left')
    
    #padding DARKO with mins
    mins = pd.read_excel(f'{path}/nba_stats.xlsx','mins')
    mins['season'] = mins['season'] + 1
    nba_stats_y = pd.merge(nba_stats_y, mins[['RowId','season','Minutes']], left_on=['nba_id','season_x'], right_on=['RowId','season'], how='left')
    nba_stats_y['Minutes'] = nba_stats_y['Minutes'].fillna(25)
    nba_stats_y['o_dpm'] = (nba_stats_y['o_dpm'] * nba_stats_y['Minutes'] + -2.5 * 250)/(nba_stats_y['Minutes'] + 250)
    nba_stats_y['d_dpm'] = (nba_stats_y['d_dpm'] * nba_stats_y['Minutes'] + -1.5 * 250)/(nba_stats_y['Minutes'] + 250)
    
    nba_stats_y['age_adj'] = nba_stats_y['age'].round()
    #nba_stats_y = nba_stats_y[['player_name','season_x','age_adj','dpm','pid']]
    nba_stats_y = nba_stats_y[['player_name','season_x','age_adj','o_dpm','d_dpm','pid']]
    nba_stats_y = nba_stats_y[nba_stats_y['pid'].notna()]
    nba_stats_y = nba_stats_y[nba_stats_y['season_x']<=year]
    
    nba_stats_y = age_curve_adj(nba_stats_y.copy())
    return nba_stats_y


def age_curve_adj(stats):
    age_curve = pd.read_excel(f'{path}/nba_stats.xlsx','age curve')
    
    combinations = list(itertools.product(stats['player_name'].unique(), range(19,40)))
    combinations = pd.DataFrame(combinations, columns=['player_name', 'age_adj'])
    combinations = combinations.merge(stats, left_on=['player_name','age_adj'], right_on=['player_name','age_adj'], how='outer')
    combinations = combinations.merge(age_curve, left_on=['age_adj'], right_on=['age'])
    combinations = combinations.sort_values(by=['player_name', 'age'], ascending=[True, True])
    
    prev = np.nan; prev_name = ""; prev_pid = np.nan; prev_off = np.nan; prev_def = np.nan
    for x in combinations.values:
        #print(x)
        """
        if(pd.isna(x[4]) and pd.notna(prev) and (prev_name == x[0])):  
            combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'dpm'] = prev + x[6]
            combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'pid'] = prev_pid
            prev_name = x[0]
            prev = prev + x[6]
        else:
            prev_name = x[0]
            prev = x[3]
            prev_pid = x[4]
        """
        if(pd.isna(x[5]) and pd.notna(prev_off) and pd.notna(prev_def) and (prev_name == x[0])):  
            combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'o_dpm'] = prev_off + x[8]
            combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'d_dpm'] = prev_def + x[9]
            combinations.loc[(combinations['player_name']==x[0])&(combinations['age']==x[1]),'pid'] = prev_pid
            prev_name = x[0]
            prev_off = prev_off + x[8]
            prev_def = prev_def + x[9]
        else:
            prev_name = x[0]
            prev_off = x[3]
            prev_def = x[4]
            prev_pid = x[5]
            
    #nba_stats = combinations.copy()
    #nba_stats = nba_stats.groupby('player_name')['dpm'].apply(lambda x: x.nlargest(5))
    #nba_stats = nba_stats[nba_stats['dpm'] >= -4]
    return combinations

#%% get latest nba stats
nba_stats = extract_nba_stats(latest_season)

#%% individual player comps analysis
def fleishman_coeffs(skew, kurt):
    def equations(vars):
        a, b, c, d = vars
        eq1 = b**2 + 6*b*d + 2*c**2 + 15*d**2 - 1
        eq2 = 2*c*(b**2 + 24*b*d + 105*d**2 + 2) - skew
        eq3 = b**4 + 24*b**3*d + 144*b**2*d**2 + 12*b**2*c**2 + 720*b*d**3 + 120*b*c**2*d + 36*c**4 + 1680*d**4 + 12*c**2 + 3 - kurt
        eq4 = a
        return [eq1, eq2, eq3, eq4]

    initial_guess = [0.25, 0.25, 0.25, 0.25]
    #initial_guess = [0, 0, 1, 0]
    a, b, c, d = fsolve(equations, initial_guess)
    #print(a, b, c, d)
    return a, b, c, d

def generate_fleishman_distribution(n_samples, mean, std, skew, kurt):
    a, b, c, d = fleishman_coeffs(skew, kurt)
    z = np.random.normal(0, 1, n_samples)
    x = a + b*z + c*z**2 + d*z**3
    x = mean + x*std
    return x

def clustering(start_season,end_season):
    
    i = start_season; df_all = []
    while(i<end_season+1):
        df = pd.read_excel(f'{path}/results.xlsx',f'{i}')
        first_column_name = df.columns[0]
        df.drop(columns=[first_column_name], inplace=True)
        df_all.append(df)
        i += 1
        
    df_all = pd.concat(df_all)
    df_all.reset_index(drop=True, inplace=True)
    
    centroids = pd.read_excel(f'{path}/results.xlsx','centroids')
    centroids.drop(columns=['cluster'], inplace=True)
    
    distances = cdist(df_all[['bust','rotation','starter','all star','all nba','mvp','floor', 'ceil']], centroids, metric='euclidean')
    cluster_assignments = np.argmin(distances, axis=1)
    df_all['cluster'] = cluster_assignments + 1
    
    i = start_season; df_final = []
    while(i<end_season+1):
        df = df_all[df_all['season'] == i]
        df = df.drop_duplicates(subset=['player'], keep='first')
        df = df.set_index('cluster')
        df_final.append(df)
        i += 1
    
    return df_final

def sum_of_unique_combinations(arr1, arr2):
    sums = []
    # Generate all unique combinations (Cartesian product) of elements
    # from arr1 and arr2
    for combo in itertools.product(arr1, arr2):
        sums.append(sum(combo))
    return sums

def player_comp_analysis(x,year,p_stats,league_stats,print_val):
    try:
        dist = distance(x, year, p_stats.copy(), data, print_val)
        dist = dist.drop_duplicates(subset=['player'], keep='first')
        
        pid = dist['pid'].values[0]
        team = dist['team'].values[0]
        bpm = dist['bpm'].values[0]
        hgt = dist['hgt'].values[0]
        dist['hgt_pct'] = norm.pdf(dist['hgt'], loc=hgt, scale=3.4) #1-np.abs(dist['hgt'] - hgt).rank(pct=True)
        dist['bpm_pct'] = np.abs(dist['score']).rank(pct=True)
        
        if(print_val==0): dist = dist.loc[(dist['season']<year)] #| ((dist['player']==x) & (dist['season']==year))]
        else: dist = dist.loc[(dist['season']<latest_season) | ((dist['player']==x) & (dist['season']==year))]
        
        dist.reset_index(inplace=True)
        p_class = player_stats.iloc[dist['index'].values[0]]['class']
        
        comps = league_stats[league_stats['pid'].isin(dist['pid'])]
        nba_comps = len(comps['pid'].unique())
        #comps = comps.groupby('player_name')['dpm'].apply(lambda x: x.nlargest(5))
        samples = 1000#00
        
        off_comps = comps.groupby('player_name')['o_dpm'].apply(lambda x: x.nlargest(5))
        off_comps = off_comps.groupby(level=0).mean()
        
        def_comps = comps.groupby('player_name')['d_dpm'].apply(lambda x: x.nlargest(5))
        def_comps = def_comps.groupby(level=0).mean()
        
        #comps_list = comps.to_list() + [-4] * (len(dist)-nba_comps) #[-3.8,-3.6,-3.4,-3.3,-3.2]
        comps_list = off_comps.to_list() + [-3.5] * (len(dist)-nba_comps) #-3.5
        comps_list.sort()
        #comps_list = [x + 2.5 for x in comps_list] #3.5
        skewness_off = skew(comps_list)
        kurtosis_off = scipy.stats.kurtosis(comps_list)
        mean_off = np.mean(comps_list)
        variance_off = np.var(comps_list)
        #distribution = generate_fleishman_distribution(samples,mean, variance**0.5, skewness, kurtosis)
        distribution_off = generate_fleishman_distribution(samples,mean_off, variance_off**0.5, skewness_off, kurtosis_off)
        
        comps_list = def_comps.to_list() + [-2] * (len(dist)-nba_comps) #-2
        comps_list.sort()
        #comps_list = [x + 1.5 for x in comps_list] #2
        skewness = skew(comps_list)
        kurtosis = scipy.stats.kurtosis(comps_list)
        mean = np.mean(comps_list)
        variance = np.var(comps_list)
        
        distribution_def = generate_fleishman_distribution(samples,mean, variance**0.5, skewness, kurtosis)
        
        distribution = sum_of_unique_combinations(distribution_off,distribution_def)
        distribution = [x + 2 for x in distribution]
        if(print_val==1):
            #plot of histogram
            plt.hist(distribution_off, bins = 100 ,edgecolor='red') # 'bins' controls the number of bins, 'edgecolor' adds a border
            plt.hist(distribution_def, bins = 100 ,edgecolor='blue') # 'bins' controls the number of bins, 'edgecolor' adds a border
            plt.hist(distribution, bins = 100 ,edgecolor='green') # 'bins' controls the number of bins, 'edgecolor' adds a border
            plt.gca().yaxis.set_major_formatter(PercentFormatter((samples*samples)))
            plt.xlim(-4, 6)
            plt.title(f'{x} {year}')
            plt.xlabel('DARKO peak')
            plt.ylabel('Frequency')
            plt.grid(axis='y')
            plt.show()
        
        comps_num = len(dist)
        #bpm_gap = stats.percentileofscore(dist['bpm'].to_list(), bpm)
        
        bench = np.sum(np.array(distribution) >= -1.75)/(samples*samples) #2.5
        starter = np.sum(np.array(distribution) >= -0.25)/(samples*samples) #4
        allstar = np.sum(np.array(distribution) >= 0.75)/(samples*samples) #5.2
        allnba = np.sum(np.array(distribution) >= 1.5)/(samples*samples) #6
        mvp = np.sum(np.array(distribution) >= 3.75)/(samples*samples) #8.5
        
        dist2 = league_stats[league_stats['pid'].isin(dist['pid'])]
        #new line
        dist2['dpm'] = dist2['o_dpm'] + dist2['d_dpm']
        dist2 = pd.pivot_table(dist2,values=['dpm'],index=['player_name'],columns=['season_x'],aggfunc=np.sum)
        dist2.columns = dist2.columns.droplevel(0)
        dist2['VORP/S'] =  dist2.max(axis=1, numeric_only=True)
        dist2['S'] =  dist2.count(axis=1, numeric_only=True)
        dist2['S'] -= 1
        dist2.reset_index(inplace=True)
        dist2 = dist2[['player_name','VORP/S','S']]
        
        dist2 = dist2.merge(dist[['player','hgt_pct','bpm_pct']], left_on=['player_name'], right_on=['player'])
        dist2['VORP/S_pct'] = np.abs(dist2['VORP/S']).rank(pct=True)
        dist2['composite'] = (dist2['bpm_pct'])*(dist2['VORP/S'])
        dist2 = dist2.loc[dist2['S'] > 1]
        
        v1 = min(math.ceil(0.05*len(dist2)),len(dist2)-1)
        v2 = max(math.ceil(0.15*len(dist2)),v1+1)
        v3 = max(math.ceil(0.4*len(dist2)),v2+1)
        
        try : c1 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(v1)[-1:].values[0],'player_name'].values[0] 
        except: c1 = ""
        try: c2 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(v2)[-1:].values[0],'player_name'].values[0]
        except : c2 = ""
        try: c3 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(v3)[-1:].values[0],'player_name'].values[0]
        except : c3 = ""
        
        p_25 = round(np.percentile(distribution, 25),1) #4
        p_50 = round(np.percentile(distribution, 50),1) #4
        p_90 = round(np.percentile(distribution, 90),1) #4
        
        if(print_val == 1):
            print()
            print(x)
            print(team,year)
            print()
            print("Bust rate",round(1-bench,4))
            print("Rotation Rate",round(bench-starter,4))
            print("Starter Rate",round(starter-allstar,4))
            print("All Star Rate",round(allstar-allnba,4))
            print("All NBA Rate",round(allnba-mvp,4))
            print("MVP Rate",round(mvp,4))
            #print("bpm percentile among comps",bpm_gap)
            print()
            print("Comp 1 - ",c1)
            print("Comp 2 - ",c2)
            print("Comp 3 - ",c3)
            print()
            #print("offense")
            #print("mean - ",mean_off)
            #print("variance - ",variance_off)
            #print("skew - ",skewness_off)
            #print("kurt - ",kurtosis_off)
            #print("defense")
            #print("mean - ",mean)
            #print("variance - ",variance)
            #print("skew - ",skewness)
            #print("kurt - ",kurtosis)
            #print()
            print("25th percentile DARKO",p_25)
            print("median DARKO",p_50)
            print("90th percentile DARKO",p_90)
            return dist,(off_comps + def_comps)
        else:
            print(x,year)
            return [x, pid, team, p_class, year, comps_num, bpm, bench, starter, allstar, allnba, mvp, c1, c2, c3, p_25, p_90]
        
    except:
        print(f"*******error with {x} {year}*******")
        if(print_val == 0): return [x, 0,"NA", 0, year, 0, 0, 0, 0, 0,0,0, "", "", "",0,0]        
    
def mdist_list(year, p_stats, print_val, get_seniors_stats):
    nba_stats = extract_nba_stats(year)
    #list_p = pd.read_excel(f'{path}/nba_stats.xlsx',f'{year}')
    list_p = pd.read_excel(f'{path}/nba_stats.xlsx','draft list')[f'{year}']
    #names_list = list_p['Player'].dropna().to_list()
    names_list = list(set(list_p))
    #names_list.sort()
    try: withdrawn_list = list_p['Withdrawn'].dropna().to_list()
    except KeyError: withdrawn_list = []
    
    if(get_seniors_stats == 1):
        seniors = p_stats[(p_stats['season']==year)&(p_stats['class']==4)&(p_stats['bpm']>=7)]
        seniors = [x for x in seniors['player'].to_list() if x not in withdrawn_list]
        names_list = names_list + seniors
    
    exceptions = list(set(names_list)-set(p_stats.player))
    print("names not in player data")
    print(exceptions)
    print()
    
    names_list = p_stats[p_stats['player'].isin(names_list)]
    names_list = names_list.loc[(names_list['season']<=year)&(names_list['season']>year-5)&(names_list['class']>0)]   
    
    result = [['player','pid','team','class','season','comps','bpm','rotation','starter','all star','all nba','mvp','comp 1','comp 2','comp 3','floor','ceil']]    
    for x,y in names_list[['player','season']].values:
        result.append(player_comp_analysis(x,y,p_stats,nba_stats.copy(),print_val))        
    
    result = pd.DataFrame(result)
    result.columns = result.iloc[0];result = result.drop(0)
    result = result.apply(pd.to_numeric, errors='ignore')
    result = result.sort_values(by=['all nba', 'player'], ascending=[False, True])
    result = result[result['class']>0]
    
    pivot = result.pivot_table(values=['season','rotation','starter','all star','all nba','mvp','floor','ceil'], index=['player','pid'], 
                               aggfunc = lambda rows: np.average(rows, weights = result.loc[rows.index, 'class'])) #aggfunc="mean")    
    team = result.pivot_table(values=['team'], index=['player','pid'], aggfunc=lambda x: ', '.join(x.unique()))
    team = team.reset_index()
    pivot = pivot.reset_index()
    exceptions += list(set(result['player'].to_list()) - set(pivot['player'].to_list()))

    pivot = team.merge(pivot, left_on=['player','pid'], right_on=['player','pid'])
    pivot['season'] = year
    
    print()
    print("rotation caliber players",round(pivot['rotation'].sum(),2))
    print("starter caliber players",round(pivot['starter'].sum(),2))
    print("all star caliber players",round(pivot['all star'].sum(),2))
    print("all nba caliber players",round(pivot['all nba'].sum(),2))
    print("mvp claiber players",round(pivot['mvp'].sum(),2))
    
    pivot['bust'] = 1 - pivot['rotation']
    pivot['rotation'] = pivot['rotation'] - pivot['starter']
    pivot['starter'] = pivot['starter'] - pivot['all star']
    pivot['all star'] = pivot['all star'] - pivot['all nba']
    pivot['all nba'] = pivot['all nba'] - pivot['mvp']
    pivot = pivot[['player','team','season','bust','rotation','starter','all star','all nba','mvp','floor','ceil']]
    pivot['ceil'] = round(pivot['ceil'],1)
    pivot['floor'] = round(pivot['floor'],1)
    pivot['bust'] = round(pivot['bust'],5)
    pivot['rotation'] = round(pivot['rotation'],5)
    pivot['starter'] = round(pivot['starter'],5)
    pivot['all star'] = round(pivot['all star'],5)
    pivot['all nba'] = round(pivot['all nba'],5)
    pivot['mvp'] = round(pivot['mvp'],5)
    return pivot,exceptions    

#%% call the player comparision function

pdist,nba_comps = player_comp_analysis("Cooper Flagg", 2025, player_stats.copy(), nba_stats.copy(), 1)

#draft_list,exception_list = mdist_list(2019, player_stats.copy(),0,0)

#clustered_list = clustering(2018,2019)
