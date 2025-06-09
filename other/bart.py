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

import scipy.stats
from scipy import stats
#from scipy.stats import norm
#from scipy.stats import skewnorm
from scipy.stats import skew
#from scipy.stats import gamma
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from pandas.errors import SettingWithCopyWarning
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)

path = "C:/Users/GF63/Desktop/cricket/excel/bart"
#path = "C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart"

#%% team ratings
def team_ratings():
    i = 2008; team_ranking = []
    while(i<2026):
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
    
#team_ranking = team_ratings()

#%% player classification
def df_class(df):
    mapping = {'Sr': 4, 'Jr': 3, 'So': 2, 'Fr': 1, '--': np.nan}
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
    df = df[df['Feet'].notna()]
    df = df[df['Inches'].notna()]
    df['hgt'] = 12*df['Feet'].astype(int) + df['Inches'].astype(int)
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

def extract_player_stats():
    headers = pd.read_csv(f'{path}/header.csv')
    i = 2008; p_stats = []; unadj_p_stats = []
    while(i<2026):
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
        
        data = data.loc[(data['mp']>=12) & (data['GP']>=10)]
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
        
        data_adj = data[['player','pid','team','season','class','role','Rec Rank','hgt','GP','mp','usg','TS%','ORB%','DRB%','AST%','TO%','ast/tov','BLK%','blk_share',
                         'STL%','stl_share','pfr','ftr','FT%','dunkar','rimar','rim%','midar','mid%','3par','3P%','ORtg','drtg','bpm']]
        
        unadj_p_stats.append(data_adj.copy())
        
        for x in ['ORB%','DRB%','BLK%','blk_share','STL%','stl_share','pfr','dunkar','AST%','TO%','ast/tov','mp']:
            data_adj = log_adjust(data_adj,x)
        for x in ['usg','ftr','rimar','midar','3par','3P%','rim%','mid%','FT%','ORtg','drtg','bpm','mp']:
            data_adj = iqr_column(data_adj,x)
        p_stats.append(data_adj)
        i+=1
        
    p_stats = pd.concat(p_stats)
    unadj_p_stats = pd.concat(unadj_p_stats)
    p_stats = df_class(p_stats)
    unadj_p_stats = df_class(unadj_p_stats)
    p_stats = df_role(p_stats)
    unadj_p_stats = df_role(unadj_p_stats)
    
    
    p_stats['hgt'] = p_stats['hgt'] - 60
    p_stats = iqr_column(p_stats,'hgt')
    p_stats = log_adjust(p_stats,'class')
    p_stats = log_adjust(p_stats,'role')
    
    return p_stats,unadj_p_stats

data,player_stats = extract_player_stats()
data.reset_index(drop=True,inplace=True)
player_stats.reset_index(drop=True,inplace=True)
#player_stats = player_stats.merge(team_ranking, left_on=['team','season'], right_on=['team','season'])

#%% histogram of all player stats
data.hist(figsize=(10, 8))  # Adjust figsize as needed
plt.tight_layout() # Adjust layout to prevent overlap
plt.show()

#%% covariance and inverse covariance for all the stats under consideration
def data_imputation_08_09(df):
    imputer = IterativeImputer()
    imputed = imputer.fit_transform(df)
    df_imputed = pd.DataFrame(imputed, columns=df.columns)
    return df_imputed

data = data[['class', 'hgt', 'usg', 'ORB%', 'DRB%', 'AST%', 'TO%', 'ast/tov', 'BLK%','blk_share','STL%','stl_share','pfr', 'ftr','FT%', 'dunkar', 'rimar', 
             'rim%', 'midar', 'mid%', '3par', '3P%','ORtg','drtg','bpm','mp']]

data = data_imputation_08_09(data.copy())
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
    #cov[0,0] = cov[0,0] * 2
    #cov[1,1] = cov[1,1] * 2
    #cov[7,7] = cov[7,7] * 2
    #cov[24,24] = cov[24,24] * 2
    
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
    full_matrix = full_matrix[['player','team','season','hgt','bpm','mdist','pid']]
    full_matrix['score'] = 1/(full_matrix['mdist']*full_matrix['mdist']) #np.exp(-1*full_matrix['mdist']*full_matrix['mdist'])
    full_matrix = full_matrix.sort_values(by=['score'], ascending=False)
    full_matrix = full_matrix.loc[full_matrix['score'] >= (full_matrix[1:]['score'].mean()+3.75*full_matrix[1:]['score'].std())]
    return full_matrix

#%% mapping nba stats
def extract_nba_stats(year):
    nba_stats_y = pd.read_excel(f'{path}/nba_stats.xlsx','DARKO')
    """
    nba_stats_y = pd.pivot_table(nba_stats_y,values=['dpm'],index=['player_name'],columns=['season'],aggfunc=np.sum)
    nba_stats_y.columns = nba_stats_y.columns.droplevel(0)
    nba_stats_y['VORP/S'] =  nba_stats_y.max(axis=1, numeric_only=True)
    nba_stats_y['S'] =  nba_stats_y.count(axis=1, numeric_only=True)
    nba_stats_y['S'] -= 1
    #nba_stats_y['VORP/S'] = 82 * nba_stats_y['VORP'] / nba_stats_y['G']
    nba_stats_y.reset_index(inplace=True)
    """
    mapping = pd.read_excel(f'{path}/nba_stats.xlsx','mapping DARKO')                   
    nba_stats_y = pd.merge(nba_stats_y, mapping, left_on='player_name', right_on='player_name', how='left')
    
    nba_stats_y['age_adj'] = nba_stats_y['age'].round()
    nba_stats_y = nba_stats_y[['player_name','season_x','age_adj','dpm','pid']]
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
            
    #nba_stats = combinations.copy()
    #nba_stats = nba_stats.groupby('player_name')['dpm'].apply(lambda x: x.nlargest(5))
    #nba_stats = nba_stats[nba_stats['dpm'] >= -4]
    return combinations

nba_stats = extract_nba_stats(2023)
#nba_stats = age_curve_adj(nba_stats.copy())

#%% individual player comps analysis
def fleishman_coeffs(skew, kurt):
    def equations(vars):
        a, b, c, d = vars
        eq1 = b**2 + 6*b*d + 2*c**2 + 15*d**2 - 1
        eq2 = 2*c*(b**2 + 24*b*d + 105*d**2 + 2) - skew
        eq3 = b**4 + 24*b**3*d + 144*b**2*d**2 + 12*b**2*c**2 + 720*b*d**3 + 120*b*c**2*d + 36*c**4 + 1680*d**4 + 12*c**2 + 3 - kurt
        eq4 = a
        return [eq1, eq2, eq3, eq4]

    initial_guess = [0.001, .99, 0.005, 0.004]
    a, b, c, d = fsolve(equations, initial_guess)
    return a, b, c, d

def generate_fleishman_distribution(n_samples, mean, std, skew, kurt):
    a, b, c, d = fleishman_coeffs(skew, kurt)
    z = np.random.normal(0, 1, 10000)
    x = a + b*z + c*z**2 + d*z**3
    x = mean + x*std
    return x

def player_comp_analysis(x,year,p_stats,league_stats,print_val):
    try:
        dist = distance(x, year, p_stats.copy(), data, print_val)
        dist = dist.drop_duplicates(subset=['player'], keep='first')
        
        team = dist['team'].values[0]
        bpm = dist['bpm'].values[0]
        hgt = dist['hgt'].values[0]
        dist['hgt_pct'] = 1-np.abs(dist['hgt'] - hgt).rank(pct=True)
        dist['bpm_pct'] = np.abs(dist['score']).rank(pct=True)
        
        #if(print_val==0): dist = dist.loc[(dist['season']<year)] #| ((dist['player']==x) & (dist['season']==year))]
        dist = dist.loc[(dist['season']<2025)] #| ((dist['player']==x) & (dist['season']==year))]
        
        dist.reset_index(inplace=True)
        comps = league_stats[league_stats['pid'].isin(dist['pid'])]
        nba_comps = len(comps['pid'].unique())
        comps = comps.groupby('player_name')['dpm'].apply(lambda x: x.nlargest(5))
        comps = comps.groupby(level=0).mean()
        
        comps_list = comps.to_list() + [-3.5] * (len(dist)-nba_comps) #[-3.8,-3.6,-3.4,-3.3,-3.2]
        comps_list.sort()
        comps_list = [x + 4 for x in comps_list]
        skewness = skew(comps_list)
        kurtosis = scipy.stats.kurtosis(comps_list)
        mean = np.mean(comps_list)
        variance = np.var(comps_list)
        
        #theta1 = 6/kurtosis 
        #theta2 = (2/skewness)**2
        #theta = theta2 #(theta1 + theta2)/2
        #alpha1 = (mean+4)/theta
        #alpha2 = variance/(theta*theta)
        #alpha = (alpha1 + alpha2)/2
        
        # Remove the top 5% values
        #del comps_list[:round(len(comps_list)*0.05)]
        # Remove the bottom 5% values
        #del comps_list[-round(len(comps_list)*0.05):]
        
        distribution = generate_fleishman_distribution(10000,mean, variance**0.5, skewness, kurtosis)
        
        comps_num = len(dist)
        bpm_gap = stats.percentileofscore(dist['bpm'].to_list(), bpm)
        
        if(np.mean(comps_list) != -4):
            #made_nba = 1-skewnorm.cdf(-2.2, a=skewness, loc=np.mean(comps_list), scale=np.var(comps_list))
            #vorp_0 = 1-skewnorm.cdf(-0.6, a=skewness, loc=np.mean(comps_list), scale=np.var(comps_list))
            #vorp_2 = 1-skewnorm.cdf(0.4, a=skewness, loc=np.mean(comps_list), scale=np.var(comps_list))
            #vorp_4 = 1-skewnorm.cdf(1.8, a=skewness, loc=np.mean(comps_list), scale=np.var(comps_list))
            made_nba = np.sum(np.array(distribution) >= 1)/10000
            vorp_0 = np.sum(np.array(distribution) >= 3)/10000
            vorp_2 = np.sum(np.array(distribution) >= 4)/10000
            vorp_4 = np.sum(np.array(distribution) >= 5.8)/10000
        else:
            made_nba = 0
            vorp_0 = 0
            vorp_2 = 0
            vorp_4 = 0
        
        dist2 = league_stats[league_stats['pid'].isin(dist['pid'])]
        dist2 = pd.pivot_table(dist2,values=['dpm'],index=['player_name'],columns=['season_x'],aggfunc=np.sum)
        dist2.columns = dist2.columns.droplevel(0)
        dist2['VORP/S'] =  dist2.max(axis=1, numeric_only=True)
        dist2['S'] =  dist2.count(axis=1, numeric_only=True)
        dist2['S'] -= 1
        dist2.reset_index(inplace=True)
        dist2 = dist2[['player_name','VORP/S','S']]
        
        dist2 = dist2.merge(dist[['player','hgt_pct','bpm_pct']], left_on=['player_name'], right_on=['player'])
        dist2['VORP/S_pct'] = np.abs(dist2['VORP/S']).rank(pct=True)
        dist2['composite'] = dist2['hgt_pct']*dist2['VORP/S_pct']
        dist2 = dist2.loc[dist2['S'] > 1]
        
        if(len(dist2) < 5):
            c1 = ""
            c2 = ""
            c3 = ""
            c4 = ""
            c5 = ""
        elif(len(dist2) < 11):
            c1 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(1)[-1:].values[0],'player_name'].values[0]
            c2 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(2)[-1:].values[0],'player_name'].values[0]
            c3 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(3)[-1:].values[0],'player_name'].values[0]
            c4 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(4)[-1:].values[0],'player_name'].values[0]
            c5 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(5)[-1:].values[0],'player_name'].values[0]
        else:
            c1 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(1)[-1:].values[0],'player_name'].values[0]
            c2 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(3)[-1:].values[0],'player_name'].values[0]
            c3 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(5)[-1:].values[0],'player_name'].values[0]
            c4 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(7)[-1:].values[0],'player_name'].values[0]
            c5 = dist2.loc[dist2['composite'] == dist2['composite'].nlargest(9)[-1:].values[0],'player_name'].values[0]
        
        if(print_val == 1):
            print()
            print("Made Roster",made_nba)
            print("Rotation Rate",vorp_0)
            print("Starter Rate",vorp_2)
            print("Star Rate",vorp_4)
            print("bpm percentile among comps",bpm_gap)
            print()
            print("Comp 1 - ",c1)
            print("Comp 2 - ",c2)
            print("Comp 3 - ",c3)
            print("Comp 4 - ",c4)
            print("Comp 5 - ",c5)
            print()
            print("mean - ",mean)
            print("variance - ",variance)
            print("skew - ",skewness)
            print("kurt - ",kurtosis)
            return dist,comps
        else:
            print(x)
            return [x, team, year, comps_num, bpm, bpm_gap, made_nba, vorp_0, vorp_2, vorp_4, c1, c2, c3, c4, c5]
        
    except IndexError:
        print(f"*******error with {x}*******")
        if(print_val == 0): return [x, "NA", year, 0, 0, 0, 0, 0, 0, 0, "", "", "", "", ""]        
    
def mdist_list(year, p_stats, print_val):
    nba_stats = extract_nba_stats(year)
    list_p = pd.read_excel(f'{path}/nba_stats.xlsx',f'{year}')
    #seniors_p = p_stats.loc[(p_stats['season']==year)&(p_stats['class']==4)&(p_stats['bpm']>=5)]
    names_list = list_p['Player'].to_list() #+ seniors_p['player'].to_list()
    names_list = list(set(names_list))
    names_list.sort()
    #names_list = p_stats[p_stats['player'].isin(names_list)]
    #names_list = names_list.loc[names_list['season']==year]
    #names_list = names_list.loc[(names_list['season']<=year)&(names_list['season']>year-5)]   
    
    result = [['player','team','season','comps','bpm','bpm percentile','made NBA','rotation','starter','all star','comp 1','comp 2','comp 3','comp 4','comp 5']]    
    for x in names_list:
        result.append(player_comp_analysis(x,year,p_stats,nba_stats.copy(),print_val))        
    
    result = pd.DataFrame(result)
    result.columns = result.iloc[0];result = result.drop(0)
    result = result.apply(pd.to_numeric, errors='ignore')
    result = result.sort_values(by=['starter', 'player'], ascending=[False, True])
    result = result.drop_duplicates(subset=['player'], keep='first')
    print()
    print("NBA claiber players",result['made NBA'].sum())
    print("rotation caliber players",result['rotation'].sum())
    print("starter caliber players",result['starter'].sum())
    print("all star caliber players",result['all star'].sum())
    return result

#%% call the player comparision function    
#pdist,nba_comps = player_comp_analysis("Brandon Miller", 2023, player_stats.copy(), nba_stats.copy(), 1)
draft_list = mdist_list(2023, player_stats.copy(),0)
