# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:33:12 2024
football player projections from fbref data
@author: Subramanya.Ganti
"""
#%% initialize
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import requests
from bs4 import BeautifulSoup
import time
from itertools import combinations
from sklearn import linear_model
import statsmodels.api as sm
import statsmodels.formula.api as smf

from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

path = "C:/Users/Subramanya.Ganti/Downloads/"

#%% functions
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

def fbref_league_fixtures(season,code):
    code,league = league_mapping(code)
    table = pd.read_html(f'https://fbref.com/en/comps/{code}/{season}-{season+1}/{season}-{season+1}-{league}-Stats')
    return table

def fbref_team_ids(season,code):
    code,league = league_mapping(code)
    url = f'https://fbref.com/en/comps/{code}/{season}-{season+1}/{season}-{season+1}-{league}-Stats'
    #take care to verify why this bypass is needed
    data  = requests.get(url,verify=False).text
    #data  = requests.get(url).text
    soup = BeautifulSoup(data,"html.parser")
    links = BeautifulSoup(data,"html.parser").select('th a')
    urls = [link['href'] for link in links]
    urls = list(set(urls))
    #print(urls)
    urls = pd.DataFrame(urls, columns=['links'])
    urls['team'] = urls['links'].str.split("/").str[-1]
    urls['team'] = urls['team'].str.replace('-Stats','')
    urls['code'] = urls['links'].str.split("/").str[3]
    urls['season'] = season
    urls = urls[['team','code','season']]
    return urls

def player_stats(club,code,season):
    ref = pd.read_html(f'https://fbref.com/en/squads/{code}/{season}-{season+1}/{club}-Stats')
    basic = ref[0]
    basic.columns = basic.columns.droplevel(0)
    basic = basic[['Player', 'Nation', 'Pos', 'Age', 'MP', 'Min', '90s']]
    keeper_basic = ref[2]
    keeper_basic.columns = keeper_basic.columns.droplevel(0)
    keeper_basic = keeper_basic[['Player', 'Nation', 'Pos', 'Age','SoTA','Saves','Save%','PKatt', 'PKA', 'PKsv', 'PKm']]
    keeper_basic.columns = ['Player', 'Nation', 'Pos', 'Age','SoTA','Saves','Save%','PKSave%','PKatt', 'PKA', 'PKsv', 'PKm']
    keeper_adv = ref[3]
    keeper_adv.columns = keeper_adv.columns.droplevel(0)
    keeper_adv = keeper_adv[['Player', 'Nation', 'Pos', 'Age', 'OG', 'PSxG', 'PSxG/SoT', 'PSxG+/-']]
    shots = ref[4]
    shots.columns = shots.columns.droplevel(0)
    shots = shots[['Player', 'Nation', 'Pos', 'Age','Sh', 'SoT']]
    passing = ref[5]
    passing.columns = passing.columns.droplevel(0)
    passing.columns = ['Player', 'Nation', 'Pos', 'Age', '90s', 'TotCmp', 'TotAtt', 'TotCmp%', 'TotDist', 'PrgDist',
           'Cmp', 'Att', 'Cmp%', 'Cmp', 'Att', 'Cmp%', 'Cmp', 'Att', 'Cmp%', 'Ast',
           'xAG', 'xA', 'A-xAG', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP','Matches']
    passing = passing[['Player', 'Nation', 'Pos', 'Age','TotCmp', 'TotAtt', 'TotCmp%', 'TotDist', 'PrgDist','Ast','xAG', 'xA','KP','PrgP']]
    #check from here
    pass_types = ref[6]
    pass_types.columns = pass_types.columns.droplevel(0)
    pass_types = pass_types[['Player', 'Nation', 'Pos', 'Age','Live', 'Dead', 'FK','TB', 'Sw', 'Crs', 'TI', 'CK']]
    offball = ref[8]
    offball.columns = offball.columns.droplevel(0)
    offball.columns = ['Player', 'Nation', 'Pos', 'Age', '90s', 'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd',
           'cTkl', 'cAtt', 'cTkl%', 'Lost', 'Blocks', 'blkSh', 'blkPass', 'Int', 'Tkl+Int',
           'Clr', 'Err','Matches']
    offball = offball[['Player', 'Nation', 'Pos', 'Age','Tkl', 'TklW','Blocks', 'blkSh', 'blkPass', 'Int','Clr', 'Err']]
    home_touches = ref[9]
    home_touches.columns = home_touches.columns.droplevel(0)
    home_touches = home_touches[['Player', 'Nation', 'Pos', 'Age','Touches','Carries','PrgC','TotDist','PrgDist','Rec','PrgR']]
    discipline = ref[11]
    discipline.columns = discipline.columns.droplevel(0)
    discipline = discipline[['Player', 'Nation', 'Pos', 'Age','CrdY', 'CrdR', '2CrdY', 'Fls', 'Fld','Recov', 'Won', 'Lost']]
    discipline.columns = ['Player', 'Nation', 'Pos', 'Age','CrdY', 'CrdR', '2CrdY', 'Fls', 'Fld','Recov', 'headWon', 'headLost']
    minutes = ref[10]
    minutes.columns = minutes.columns.droplevel(0)
    minutes = minutes[['Player', 'Nation', 'Pos', 'Age','Starts', 'Mn/Start', 'Subs', 'Mn/Sub', 'unSub']]
    dfs = [basic, keeper_basic, keeper_adv, shots, passing, pass_types, offball, home_touches, discipline, minutes]
    merged_df = dfs[0]
    for i in range(1, len(dfs)):
        merged_df = pd.merge(merged_df, dfs[i], on=['Player', 'Nation', 'Pos', 'Age'], how='left')
    merged_df['o_Touches'] = merged_df.loc[merged_df['Player']=='Opponent Total','TotAtt'].sum()/11
    games =  merged_df.loc[merged_df['Player']=='Opponent Total','90s'].sum()
    merged_df['o_Touches'] = merged_df['o_Touches'] * merged_df['90s'] / games
    merged_df = merged_df.dropna(subset=['Nation','Min'])
    merged_df['season'] = season
    merged_df['club'] = club
    #p_stats_agg = aggregate_stats(merged_df,1)
    return merged_df
    
def team_stats(init_season,end_season,code):
    season = init_season; final = []
    while(season < end_season+1):
        time.sleep(3.01); print(season)
        ref = fbref_league_fixtures(season,code)
        basic = ref[0]
        basic = basic[['Squad', 'MP', 'GF', 'GA','xG', 'xGA' ,'Pts']]
        keeper_basic = ref[4]
        keeper_basic.columns = keeper_basic.columns.droplevel(0)
        keeper_basic = keeper_basic[['Squad','Save%','PKatt', 'PKA', 'PKsv', 'PKm']]
        keeper_basic.columns = ['Squad','Save%','PKSave%','PKatt', 'PKA', 'PKsv', 'PKm']
        keeper_adv = ref[6]
        keeper_adv.columns = keeper_adv.columns.droplevel(0)
        keeper_adv = keeper_adv[['Squad', 'OG', 'PSxG', 'PSxG/SoT', 'PSxG+/-']]
        shots = ref[8]
        shots.columns = shots.columns.droplevel(0)
        shots = shots[['Squad','Sh', 'SoT']]
        passing = ref[10]
        passing.columns = passing.columns.droplevel(0)
        passing.columns = ['Squad', '# Pl', '90s', 'TotCmp', 'TotAtt', 'TotCmp%', 'TotDist', 'PrgDist',
               'Cmp', 'Att', 'Cmp%', 'Cmp', 'Att', 'Cmp%', 'Cmp', 'Att', 'Cmp%', 'Ast',
               'xAG', 'xA', 'A-xAG', 'KP', '1/3', 'PPA', 'CrsPA', 'PrgP']
        passing = passing[['Squad','TotCmp', 'TotAtt', 'TotCmp%', 'TotDist', 'PrgDist','Ast','xAG', 'xA','PrgP','KP']]
        pass_types = ref[12]
        pass_types.columns = pass_types.columns.droplevel(0)
        offball = ref[16]
        offball.columns = offball.columns.droplevel(0)
        offball.columns = ['Squad', '# Pl', '90s', 'Tkl', 'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd',
               'cTkl', 'cAtt', 'cTkl%', 'Lost', 'Blocks', 'blkSh', 'blkPass', 'Int', 'Tkl+Int',
               'Clr', 'Err']
        offball = offball[['Squad','Tkl', 'TklW','Blocks', 'blkSh', 'blkPass', 'Int','Clr', 'Err']]
        home_touches = ref[18]
        home_touches.columns = home_touches.columns.droplevel(0)
        home_touches = home_touches[['Squad','Touches','Carries','PrgC','TotDist','PrgDist','Rec','PrgR']]
        opp_touches = ref[19]
        opp_touches.columns = opp_touches.columns.droplevel(0)
        opp_touches = opp_touches[['Squad','Touches','Carries','PrgC','TotDist','PrgDist','Rec','PrgR']]
        opp_touches.columns = ['Squad', 'o_Touches', 'o_Carries','o_PrgC', 'o_TotDist', 'o_PrgDist', 'o_Rec', 'o_PrgR']
        opp_touches['Squad'] = opp_touches['Squad'].str.replace('vs ','')
        discipline = ref[22]
        discipline.columns = discipline.columns.droplevel(0)
        discipline = discipline[['Squad','CrdY', 'CrdR', '2CrdY', 'Fls', 'Fld','Recov', 'Won', 'Lost']]
        discipline.columns = ['Squad','CrdY', 'CrdR', '2CrdY', 'Fls', 'Fld','Recov', 'headWon', 'headLost']
        
        dfs = [basic, keeper_basic, keeper_adv, shots, passing, pass_types, offball, home_touches, opp_touches, discipline]
        merged_df = dfs[0]
        for i in range(1, len(dfs)):
            merged_df = pd.merge(merged_df, dfs[i], on='Squad', how='inner')
        
        merged_df['season'] = season
        final.append(merged_df)
        season += 1
    
    final = pd.concat(final)
    return final

def aggregate_stats(df,player_yes):
    if(player_yes == 1):
        df['90s'] = df['Min']/90
        analysis = df[['Player','Nation','Pos','club','Age','season','90s','Touches','o_Touches','Save%','Sh','TotAtt','TotCmp%','PrgP',
                       'Carries','PrgC','Tkl', 'TklW','blkSh', 'blkPass', 'Int', 'Clr','Err','Fls', 'Fld','Age_copy']]
    else: 
        analysis = df[['Squad','season','MP','Pts','GF', 'GA','xG','xGA','Touches','o_Touches','Save%','Sh','TotAtt','TotCmp%','PrgP',
                       'Carries','PrgC','Tkl', 'TklW','blkSh', 'blkPass', 'Int', 'Clr','Err','Fls', 'Fld']]
    
    analysis['PrgP'] = analysis['PrgP']/analysis['TotAtt']
    analysis['PrgC'] = analysis['PrgC']/analysis['Carries']
    analysis['Sh'] = analysis['Sh']/analysis['Touches']
    analysis['TotAtt'] = analysis['TotAtt']/analysis['Touches']
    #analysis['KP'] = analysis['KP']/analysis['Touches']
    analysis['Carries'] = analysis['Carries']/analysis['Touches']   
    analysis['blkSh'] = analysis['blkSh']/analysis['o_Touches']
    analysis['blkPass'] = analysis['blkPass']/analysis['o_Touches']
    analysis['Int'] = analysis['Int']/analysis['o_Touches']
    analysis['Clr'] = analysis['Clr']/analysis['o_Touches']
    analysis['Err'] = analysis['Err']/analysis['o_Touches']
    analysis['Fls'] = analysis['Fls']/analysis['o_Touches']
    analysis['Fld'] = analysis['Fld']/analysis['Touches']
    if(player_yes == 1):
        analysis['Touches'] = analysis['Touches']/analysis['90s']
        analysis['o_Touches'] = analysis['o_Touches']/analysis['90s']
        analysis['Tkl'] = analysis['Tkl']/analysis['o_Touches']
    else:
        analysis['TklW'] = 100*analysis['TklW']/analysis['Tkl']
        analysis['Tkl'] = analysis['Tkl']/analysis['o_Touches']
        analysis['Touches'] = analysis['Touches']/analysis['MP']
        analysis['o_Touches'] = analysis['o_Touches']/analysis['MP']
        analysis['Pts'] = analysis['Pts']/analysis['MP']
        analysis['GF'] = analysis['GF']/analysis['MP']
        analysis['GA'] = analysis['GA']/analysis['MP']
        analysis['xG'] = analysis['xG']/analysis['MP']
        analysis['xGA'] = analysis['xGA']/analysis['MP']
        analysis['GD'] = analysis['GF'] - analysis['GA']
        analysis['xGD'] = analysis['xG'] - analysis['xGA']
        analysis['pace'] = analysis['Touches'] + analysis['o_Touches']
        analysis['dominance'] = analysis['Touches']/analysis['o_Touches']
        analysis.drop(['Touches','o_Touches'], axis=1, inplace=True)
    return analysis

def regression(df, a):
    df.reset_index(drop=True, inplace=True)
    analysis = aggregate_stats(df,0)    
    # Generate some synthetic data
    y = analysis['Pts']
    X = analysis[['Save%','Sh','TotAtt','TotCmp%','PrgP','Carries','PrgC','Tkl','TklW','blkSh','blkPass','Int','Clr','Err','Fls','Fld']] #'dominance','pace'
    #normalization
    y_mean = y.mean(); y_std = y.std()
    X_mean = X.mean(); X_std = X.std()
    #print("y_mean",y_mean,"y_stdev",y_std)
    #print("X_mean",X_mean,"X_stdev",X_std)
    y=(y-y.mean())/y.std()
    X=(X-X.mean())/X.std()
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    # Initialize and fit the Lasso model
    # 'alpha' is the regularization parameter (strength of the penalty)
    lasso_model = Lasso(alpha=a) 
    lasso_model.fit(X_train, y_train)
    # Print the coefficients
    print("Lasso Coefficients:", lasso_model.coef_)
    # Make predictions
    y_pred = lasso_model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print("Mean Squared Error (MSE):", mse)
    print("R-squared (R2):", r2)
    
    analysis['pred'] = lasso_model.predict(X)
    analysis['pred'] = (analysis['pred']*y_std) + y_mean
    s = analysis[['Squad','season','Pts','GD','xGD','pred']]
    
    data = pd.DataFrame(columns=['variable','weight','mean','stdev'])
    X_mean = pd.DataFrame(X_mean)
    X_mean.reset_index(inplace=True)
    data['variable'] = X_mean['index']
    data['mean'] = X_mean[0]
    X_std = pd.DataFrame(X_std)
    X_std.reset_index(inplace=True)
    data['stdev'] = X_std[0]
    data.loc[len(data)] = ['pred',np.nan,y_mean,y_std]
    data['weight'] = np.append(lasso_model.coef_,[np.nan])
    
    return s,analysis,lasso_model,data

def multi_leagues(read):
    if(read == 0):
        t_stats_1 = team_stats(2017,2024,9)
        t_stats_2 = team_stats(2017,2024,11)
        t_stats_3 = team_stats(2017,2024,12)
        t_stats_4 = team_stats(2017,2024,13)
        t_stats_5 = team_stats(2017,2024,20)
        df = pd.concat([t_stats_1,t_stats_2,t_stats_3,t_stats_4,t_stats_5])
    else:
        df = pd.read_excel(f'{path}/fbref.xlsx','big 5 leagues raw')
        df = df.drop('index', axis=1)
    return df

def multi_team_links(start,end,code):
    raw = []
    season = start
    while(season<=end):
        links = fbref_team_ids(season,code)
        for l in links['team'].index:
            time.sleep(3.01)
            t = links.iloc[l]['team']
            c = links.iloc[l]['code']
            s = links.iloc[l]['season']
            print(s,t)
            raw_stats = player_stats(t,c,s)
            raw.append(raw_stats)
        season += 1
    raw = pd.concat(raw)
    return raw

def extract_player_data(convert,target):
    leagues = ['serie a','bundesliga','premier league','la liga','ligue un'];
    df_all = []
    for l in leagues:
        df = pd.read_excel(f'{path}/fbref.xlsx',l)
        df = df.drop('Unnamed: 0', axis=1)
        df = df[['Player','club','Nation','Pos','Age','season','Min','Touches','o_Touches','Save%','Sh','TotAtt','TotCmp%','PrgP','Carries','PrgC',
                 'Tkl', 'TklW','blkSh', 'blkPass', 'Int', 'Clr','Err','Fls', 'Fld','Starts', 'Mn/Start', 'Subs', 'Mn/Sub', 'unSub']]
        df['yob'] = df['season'] - df['Age']
        df = df.drop_duplicates(subset=['Player', 'club', 'Nation', 'Pos', 'Age', 'season'], keep='first')
        
        if(convert == 1):
            factors = league_conversion_factors(1)
            f = np.exp(factors.loc[l] - factors.loc[target])
            df[f.index] = df[f.index] * f.values
            
        df_all.append(df)    
    return df_all,leagues
    
def league_conversion_factors(read_file):
    if(read_file == 1):
        all_eqn = pd.read_excel(f'{path}/fbref.xlsx','conversions',index_col=0)
    else:
        df,leagues = extract_player_data(0,'')
        combos = list(combinations(range(0,len(df)), 2))
        categories = ['Touches', 'o_Touches', 'Save%', 'Sh', 'TotAtt', 'TotCmp%', 'PrgP', 'Carries',
                      'PrgC', 'Tkl', 'TklW', 'blkSh', 'blkPass', 'Int', 'Clr', 'Err', 'Fls', 'Fld']
        all_eqn = [['category'] + leagues]
        
        for ch in categories:
            eqn = pd.DataFrame(columns=range(0,len(df)), index=range(0,2*len(combos)))
            eqn[f'{ch} log factor'] = 0.0
            r = 0
            for c in combos:
                from_df = df[c[0]]
                from_df['season+1'] = from_df['season'] + 1
                to_df = df[c[1]]
                to_df['season+1'] = to_df['season'] + 1
                
                df_from_to = to_df.merge(from_df, left_on=['Player','Nation','yob','season'], right_on=['Player','Nation','yob','season+1'])
                #print("from",c[0],"to",c[1],(df_from_to[f'{ch}_x'].sum()/df_from_to['Min_x'].sum())/(df_from_to[f'{ch}_y'].sum()/df_from_to['Min_y'].sum()))
                eqn.loc[r,c[0]] = 1
                eqn.loc[r,c[1]] = -1
                eqn.loc[r,f'{ch} log factor'] = np.log((df_from_to[f'{ch}_x'].sum()/df_from_to['Min_x'].sum())/(df_from_to[f'{ch}_y'].sum()/df_from_to['Min_y'].sum()))
                r+=1
                
                df_to_from = from_df.merge(to_df, left_on=['Player','Nation','yob','season'], right_on=['Player','Nation','yob','season+1'])
                #print("from",c[1],"to",c[0],(df_to_from[f'{ch}_x'].sum()/df_to_from['Min_x'].sum())/(df_to_from[f'{ch}_y'].sum()/df_to_from['Min_y'].sum()))
                eqn.loc[r,c[0]] = -1
                eqn.loc[r,c[1]] = 1
                eqn.loc[r,f'{ch} log factor'] = np.log((df_to_from[f'{ch}_x'].sum()/df_to_from['Min_x'].sum())/(df_to_from[f'{ch}_y'].sum()/df_to_from['Min_y'].sum()))
                
                r+=1
            
            eqn[[0,1,2,3,4]] = eqn[[0,1,2,3,4]].fillna(0)
            eqn = eqn[eqn[f'{ch} log factor'].notna()]
            
            regr = linear_model.LinearRegression()
            regr.fit(eqn[[0,1,2,3,4]], eqn[f'{ch} log factor'])
            #all_eqn.append(eqn)
            #all_eqn.loc[r0] = list(regr.coef_) + [ch]
            print(ch,regr.coef_)
            all_eqn.append([ch] + list(regr.coef_))
        
        all_eqn = pd.DataFrame(all_eqn)
        all_eqn.columns = all_eqn.iloc[0];all_eqn = all_eqn.drop(0)
        all_eqn = all_eqn.T
        all_eqn.columns = all_eqn.iloc[0]
        all_eqn = all_eqn.drop('category')
        all_eqn = all_eqn.apply(pd.to_numeric, errors='ignore')
        all_eqn[['Save%','TotCmp%']] = all_eqn[['Save%','TotCmp%']]/10
    return all_eqn

def aging_analysis(read_file):
    if(read_file == 1):
        df_all = pd.read_excel(f'{path}/fbref.xlsx','aging')
    else:
        df,leagues = extract_player_data(1,'premier league')
        df = pd.concat(df)
        df = df.reset_index(drop=True)
        df = df[df['Pos']!='GK']
        df = df[df['Min']>450]
        categories = ['Touches', 'o_Touches', 'Sh', 'TotAtt', 'PrgP', 'Carries',
                      'PrgC', 'Tkl', 'TklW', 'blkSh', 'blkPass', 'Int', 'Clr', 'Err', 'Fls', 'Fld']
        df_all = []
        for key in categories:
            df2 = df[['Age', 'season', 'Min',key]]
            df2[f'{key}_Min'] = df[key]/df2['Min']
            df2['Age2'] = df['Age']*df2['Age']
            df2 = df2[[f'{key}_Min','Age','Age2','Min']]
            df2 = df2.reset_index(drop=True)
            df2 = df2.dropna()
            
            model = smf.mixedlm(f"{key}_Min ~ Age + Age2", data=df2, groups="Min")
            result = model.fit()
            params = result.params
            #print(result)
            #print(result.params)
            aging = pd.DataFrame(columns=['Age','Age2',key])
            aging['Age'] = range(1,50)
            aging['Age2'] = aging['Age']*aging['Age']
            aging[key] = params['Intercept'] + params['Age']*aging['Age'] + params['Age2']*aging['Age2']
            df_all.append(aging)
        
        df_all = pd.concat(df_all, axis=1)
        df_all = df_all.drop(columns=['Age','Age2'])
        df_all['Age'] = range(1,50)
        df_all['Save%'] = df_all['o_Touches']
        df_all['TotCmp%'] = df_all['TotAtt']
        df_all = df_all[['Age','Touches', 'o_Touches', 'Save%', 'Sh', 'TotAtt', 'TotCmp%', 'PrgP', 'Carries',
                      'PrgC', 'Tkl', 'TklW', 'blkSh', 'blkPass', 'Int', 'Clr', 'Err', 'Fls', 'Fld']]
    return df_all

def keep_unique_substrings(row):
    substrings = row.split(',')  # Split the string into substrings
    unique_substrings = list(dict.fromkeys(substrings))  # Remove duplicates while preserving order
    return ','.join(unique_substrings)

def mean_reversion(proj_year,standard):
    #proj_year = 2025
    df,leagues = extract_player_data(1,standard)
    df = pd.concat(df)
    df = df.reset_index(drop=True)
    coeffs = pd.read_excel(f'{path}/fbref.xlsx','model coefficients')
    coeffs = coeffs.drop('Unnamed: 0', axis=1)
    
    df['weight'] = pow(2/3,proj_year-df['season'])
    df_agg = df.pivot_table(values=['Min','Touches','o_Touches','Save%','Sh','TotAtt','TotCmp%','PrgP','Carries','PrgC',
                                'Tkl', 'TklW','blkSh', 'blkPass', 'Int', 'Clr','Err','Fls', 'Fld'],
                              index=['Player','Nation','yob'], 
                              aggfunc=lambda rows: np.average(rows, weights=df.loc[rows.index, 'weight']))
    pos = df.pivot_table(values=['Pos'], index=['Player','Nation','yob'], aggfunc=lambda x: ','.join(x.unique()))
    team = df.pivot_table(values=['club'], index=['Player','Nation','yob'], columns=['season'], aggfunc=lambda x: ','.join(x.unique()))
    team.columns = team.columns.droplevel(0)
    age = df.pivot_table(values=['Age','season'], index=['Player','Nation','yob'], aggfunc='max')
    avg = df[['Touches','o_Touches','Save%','Sh','TotAtt','TotCmp%','PrgP','Carries','PrgC',
             'Tkl', 'TklW','blkSh', 'blkPass', 'Int', 'Clr','Err','Fls', 'Fld']].sum()
    avg = 600 * avg/df['Min'].sum()
    #percentage stats need to be fixed
    avg['Save%'] = coeffs.loc[coeffs['variable']=='Save%','mean'].sum()
    avg['TotCmp%'] = coeffs.loc[coeffs['variable']=='TotCmp%','mean'].sum()
    avg['TklW'] = coeffs.loc[coeffs['variable']=='TklW','mean'].sum()
    
    pos = pos.reset_index()
    team = team.reset_index()
    team = team[['Player','Nation','yob',proj_year-1]]
    team = team.rename(columns={proj_year-1: 'club'})
    age = age.reset_index()
    age['Age_copy'] = age['Age']
    age['Age'] = age['Age'] + proj_year - age['season']
    age['season'] = proj_year
    df_agg = df_agg.reset_index()
    df_agg = pos.merge(df_agg, left_on=['Player','Nation','yob'], right_on=['Player','Nation','yob'])
    df_agg = team.merge(df_agg, left_on=['Player','Nation','yob'], right_on=['Player','Nation','yob'])
    df_agg = age.merge(df_agg, left_on=['Player','Nation','yob'], right_on=['Player','Nation','yob'])
    df_agg['TklW'] = 100*df_agg['TklW']/df_agg['Tkl']
    for x in avg.index:
        if(x not in ['Save%','TotCmp%','TklW']):  df_agg[x] = df_agg[x] + avg[x]
        else: df_agg[x] = (df_agg[x]*df_agg['Min'] + avg[x]*600)/(df_agg['Min']+600)
    df_agg['Min'] = df_agg['Min'] + 600
    df_agg = aggregate_stats(df_agg,1)
    df_agg['90s'] = df_agg['90s'] - (600/90)
    df_agg['Pos'] = df_agg['Pos'].str.replace(' ','')
    df_agg['Pos'] = df_agg['Pos'].apply(keep_unique_substrings)
    df_agg['club'] = df_agg['club'].str.replace('-',' ')
    
    aging = aging_analysis(1)
    projections_copy = df_agg.merge(aging, left_on='Age_copy', right_on='Age')
    projections_copy = projections_copy.merge(aging, left_on='Age_x', right_on='Age')
    
    for v in ['Touches','o_Touches','Save%','Sh','TotAtt','TotCmp%','PrgP','Carries','PrgC',
             'Tkl', 'TklW','blkSh', 'blkPass', 'Int', 'Clr','Err','Fls', 'Fld']:
        projections_copy[f'{v}_x'] *= projections_copy[v] / projections_copy[f'{v}_y']
        
    projections_copy = projections_copy[['Player', 'Nation', 'Pos', 'club', 'Age_x', 'season', '90s',
           'Touches_x', 'o_Touches_x', 'Save%_x', 'Sh_x', 'TotAtt_x', 'TotCmp%_x',
           'PrgP_x', 'Carries_x', 'PrgC_x', 'Tkl_x', 'TklW_x', 'blkSh_x',
           'blkPass_x', 'Int_x', 'Clr_x', 'Err_x', 'Fls_x', 'Fld_x']]
    projections_copy.columns = ['Player', 'Nation', 'Pos', 'club', 'Age', 'season', '90s',
           'Touches', 'o_Touches', 'Save%', 'Sh', 'TotAtt', 'TotCmp%',
           'PrgP', 'Carries', 'PrgC', 'Tkl', 'TklW', 'blkSh',
           'blkPass', 'Int', 'Clr', 'Err', 'Fls', 'Fld']
    return projections_copy

#%% extract data
#t_stats = multi_leagues(0)
player_stats_raw = multi_team_links(2017,2024,13)

#%% analyze
#summary,t_stats_reg,lasso,coeffs = regression(t_stats,0.001)
#factors = league_conversion_factors(0)
projections = mean_reversion(2025,'premier league')