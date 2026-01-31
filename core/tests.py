# -*- coding: utf-8 -*-
"""
Created on Wed Dec 24 16:55:30 2025
Cricket projections v2
@author: Uttam Ganti
"""
#%% imports and read files
import numpy as np
import pandas as pd
from datetime import datetime
from pykalman import KalmanFilter
from sklearn import linear_model
from itertools import combinations
import statsmodels.formula.api as smf
import glob

np.seterr(divide='ignore')

league = 't20i'
#full_leagues_list = ['odi','odiq','t20i','t20iq','ipl','psl','cpl','mlc','sa20','blast','bbl','hundred','lpl','ilt','smash','bpl','smat']
#full_leagues_list = ['tests','cc','shield']

path = 'C:/Users/Subramanya.Ganti/Downloads/Sports/cricket'

#%% read files and basic pre processing
def test_leagues(): l = ['tests','cc','shield']; return l
def odi_leagues(): l = ['odi','odiq']; return l
def t20_leagues(): l = ['t20i','t20iq','ipl','psl','cpl','mlc','sa20','blast','bbl','lpl','ilt','smash','bpl','smat']; return l
def short_leagues(): l = ['hundred']; return l

def leagues_considered(l):
    if(l in test_leagues()): return test_leagues()
    else: return (odi_leagues() + short_leagues() + t20_leagues()) 

def active_lineups(comp):
    path_files = f"{path}/raw/{comp}"        
    col_names = ["col1", "col2", "team", "player","id"]
    full_squad_list = []
    file_list = glob.glob(path_files + "/*.csv")
    
    for file in file_list:
        if(file[-8:] == 'info.csv'):
            df = pd.read_csv(file, names=col_names)
            date = datetime.strptime(df.loc[df['col2']=='date','team'].values[0], '%Y/%m/%d')
            teams_list = df[df['col2']=='player']
            teams_list = teams_list.copy()
            teams_list['date'] = date
            full_squad_list.append(teams_list)

    full_squad_list = pd.concat(full_squad_list)
    max_dates = full_squad_list.groupby('team')['date'].transform('max')
    full_squad_list = full_squad_list[full_squad_list['date'] == max_dates]
    full_squad_list = full_squad_list.copy()
    full_squad_list['comp'] = comp
    
    if(comp in ['t20i','odi']): full_squad_list = full_squad_list[full_squad_list['team'].isin(["Australia","England","New Zealand","India","South Africa",
                                                                                               "Sri Lanka","West Indies","Pakistan","Bangladesh","Ireland",
                                                                                               "Afghanistan","Zimbabwe","Scotland","Netherlands","Namibia",
                                                                                               "United Arab Emirates","Nepal","Oman","Papua New Guinea",
                                                                                               "Canada","United States of America",'Italy'])]
    return full_squad_list
    
def concat_game_files(comp):
    if(comp == 'odiq'):
        path_files = f"{path}/raw/odi"
    elif(comp == 't20iq'):
        path_files = f"{path}/raw/t20i"
    elif(comp == 't20iwq'):
        path_files = f"{path}/raw/t20iw"
    else:
        path_files = f"{path}/raw/{comp}"
        
    output = f'{path}/raw/{comp}.csv'
    output2 = f'{path}/raw/{comp}_GP.csv'

    db_start = 1
    db_end = 2100
    league = 0; check = 0
    col_names = ["col1", "col2", "team", "player","id"]
    excl_list = []; names_list=[]; i=0

    file_list = glob.glob(path_files + "/*.csv")
    if(comp == 'odiq'):
        countries = ["Zimbabwe","Netherlands","West Indies","Nepal","United States of America","Ireland","Scotland","Oman","United Arab Emirates"]
    elif(comp == 't20iw'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Ireland","Scotland","West Indies","Pakistan","Bangladesh","Thailand","Zimbabwe"]
    elif(comp == 't20iwq'):
        countries = ["Ireland","Scotland","Thailand","Zimbabwe","Papua New Guinea","Netherlands","Namibia","United Arab Emirates","Uganda","Tanzania","Indonesia","Nepal"]
    elif(comp == 'odiw'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Thailand","Ireland"]
    elif(comp == 'odi'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Pakistan","Bangladesh","Afghanistan","West Indies","Netherlands","Nepal","Ireland","Zimbabwe"]
    elif(comp == 't20i'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Ireland","Afghanistan","Zimbabwe","Scotland","Netherlands","Namibia","United Arab Emirates","Nepal","Oman","Papua New Guinea","Canada","United States of America","Uganda"]
    elif(comp == 't20iq'):
        countries = ["Ireland","Scotland","Jersey","Italy","Germany","Denmark","Austria","Netherlands","Zimbabwe","Namibia","Nigeria","Rwanda","Tanzania","Uganda","Kenya","Bahrain","Hong Kong","Kuwait","Malaysia","Nepal","Oman","Singapore","United Arab Emirates","Japan","Papua New Guinea","Philippines","Canada","United States of America"]
    elif(comp == 'tests'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Pakistan","West Indies","Bangladesh"]
    elif(comp == 'cwc'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Pakistan","Bangladesh","Afghanistan","West Indies","Netherlands","Nepal","Ireland","Zimbabwe","Kenya","Namibia"]
    elif(comp == 'smat'):
        countries = ['Meghalaya','Mizoram','Sikkim','Arunachal Pradesh','Manipur','Nagaland','Pondicherry']
    else:
        league = 1

    for file in file_list:
        if(file[-8:] != "info.csv"):
            df = pd.read_csv(file)
            date = datetime.strptime(df['start_date'][0], '%Y-%m-%d')
            if(league == 0):check = df['batting_team'][0] in countries and df['bowling_team'][0] in countries
            if(comp == 'smat'):check = df['batting_team'][0] not in countries and df['bowling_team'][0] not in countries
            if(date.year>=db_start and (check or league) and date.year<=db_end):
                if((comp == 'bbl' or comp == 'wbbl' or comp == 'ss' or comp == 'wss' or comp == 'shield') and date.month < 4):   #big bash is a december-january league
                    df['season'] = date.year-1
                elif(comp == 'smat' and date.year>=db_start and date.year<=db_end):
                    df['season'] = int((df['season'][0]).split('/')[0])
                else:                
                    df['season'] = date.year
                print(df['start_date'][0],df['batting_team'][0],df['bowling_team'][0])
                excl_list.append(df)
                
        if(file[-8:] == 'info.csv'):
            df = pd.read_csv(file, names=col_names)
            date = datetime.strptime(df.loc[df['col2']=='date','team'].values[0], '%Y/%m/%d')
            t1 = df.loc[(df['col2']=='team') | (df['col2']=='teams'),'team'].values[0]
            t2 = df.loc[(df['col2']=='team') | (df['col2']=='teams'),'team'].values[1]
            if(league == 0):check = t1 in countries and t2 in countries
            if(comp == 'smat'):check = t1 not in countries and t2 not in countries
            if(date.year>=db_start and (check or league) and date.year<=db_end):
                names = df.loc[(df['col2']=='player') | (df['col2']=='players'),'player']
                names = pd.concat([names,pd.Series([t1,t2])])
                names = pd.DataFrame(names)
                if((comp == 'bbl' or comp == 'wbbl' or comp == 'ss' or comp == 'wss' or comp == 'shield') and date.month < 4):   #big bash is a december-january league
                    names['season'] = date.year-1
                elif(comp == 'smat' and date.year>=db_start and date.year<=db_end):
                    names['season'] = int((df.loc[df['col2']=='season','team'].values[0]).split('/')[0])
                else:                
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
    print(f"concat for {comp} done, file dumped, run generate.py")
    
def squad_info():
    #all_leagues = ['tests','odi','odiq','t20i','t20iq','ipl','psl','cpl','mlc','sa20','blast','bbl','hundred','cc','shield','lpl','ilt','smash','bpl','smat']
    all_leagues = test_leagues() + odi_leagues() + t20_leagues() + short_leagues()
    agg = []
    for l in all_leagues:
        file = f'{path}/raw/{l}.csv'
        sample = pd.read_csv(file,sep=',',low_memory=False)
        #sample['start_date'] = pd.to_datetime(sample['start_date'], format='%Y-%m-%d')
        bat = sample[['striker','batting_team','start_date']]
        bat.columns = ['player',l,'start_date']
        bowl = sample[['bowler','bowling_team','start_date']]
        bowl.columns = ['player',l,'start_date']
        team = pd.concat([bat,bowl])
        team = team.sort_values(by=['start_date'], ascending=[False])
        team = team[['player',l]].drop_duplicates(subset='player')
        #team['league'] = l
        #agg.append(team)
        if(len(agg) == 0): agg = team
        else: agg = agg.merge(team,how='outer')
       
    existing = pd.read_excel(f'{path}/excel/projections.xlsx','squads')
    agg = agg.merge(existing[['player','team']], on='player', how='left')
    agg = agg[['player','team','tests','odi','t20i','odiq','t20iq','ipl','psl','cpl','mlc','sa20','blast','bbl','lpl','ilt','smash','bpl','smat','hundred','cc','shield']]
    return agg
    
def league_data(l):
    file = f'{path}/raw/{l}.csv'
    sample = pd.read_csv(file,sep=',',low_memory=False)
    
    sample['wicket_bowler'] = sample['wicket_type'].isin(['caught', 'bowled', 'lbw', 'caught and bowled','stumped', 'hit wicket'])
    #sample['wicket_other'] = sample['wicket_type'].isin(['run out','retired hurt', 'retired not out','obstructing the field', 'handled the ball'])
    sample['wicket_striker'] = sample['striker']==sample['player_dismissed']
    sample['wicket_non_striker'] = sample['non_striker']==sample['player_dismissed']
    sample['batter_bf'] = sample['wides'].isna()
    sample['bowler_bb'] = sample['wides'].isna() & sample['noballs'].isna()
    
    sample['wicket_bowler'] = sample['wicket_bowler'].astype(int)
    sample['wicket_striker'] = sample['wicket_striker'].astype(int)
    sample['wicket_non_striker'] = sample['wicket_non_striker'].astype(int)
    sample['batter_bf'] = sample['batter_bf'].astype(int)
    sample['bowler_bb'] = sample['bowler_bb'].astype(int)
    
    sample['0s'] = (sample['runs_off_bat']==0).astype(int)
    sample['1s'] = (sample['runs_off_bat']==1).astype(int)
    sample['2s'] = (sample['runs_off_bat']==2).astype(int)
    sample['3s'] = (sample['runs_off_bat']==3).astype(int)
    sample['2s'] +=  sample['3s']
    sample['1s'] +=  sample['3s']
    sample['4s'] = (sample['runs_off_bat']==4).astype(int)
    sample['5s'] = (sample['runs_off_bat']==5).astype(int)
    sample['6s'] = (sample['runs_off_bat']==6).astype(int)
    sample['4s'] +=  sample['5s']
    sample['1s'] +=  sample['5s']
    sample['0s'] *= sample['batter_bf']
    
    pivot = sample.pivot_table(index=['match_id'],values=['bowler_bb','batter_bf','runs_off_bat','0s','1s','2s','4s','6s','extras','wicket_bowler','wicket_striker','wicket_non_striker'],aggfunc='sum')
    pivot = pivot.reset_index()
    #pivot2 = sample.pivot_table(index=['match_id'],values=['wicket_non_striker'],aggfunc='sum')
    #pivot2 = pivot2.reset_index()
    #pivot = pivot.merge(pivot2, on=['match_id'], how='left')
    
    pivot['bat_runs_ball'] = pivot['runs_off_bat'] / pivot['batter_bf']
    pivot['bat_wkt_ball'] = (pivot['wicket_striker']+pivot['wicket_non_striker']) / pivot['batter_bf']
    pivot['bowl_runs_ball'] = (pivot['runs_off_bat']+pivot['extras']) / pivot['bowler_bb']
    pivot['bowl_wkt_ball'] = pivot['wicket_bowler'] / pivot['bowler_bb']
    pivot['0s_ball'] = pivot['0s'] / pivot['batter_bf']
    pivot['1s_ball'] = pivot['1s'] / pivot['batter_bf']
    pivot['2s_ball'] = pivot['2s'] / pivot['batter_bf']
    pivot['4s_ball'] = pivot['4s'] / pivot['batter_bf']
    pivot['6s_ball'] = pivot['6s'] / pivot['batter_bf']
    pivot['extras_ball'] = pivot['extras'] / pivot['bowler_bb']
    
    sample = sample.merge(pivot[['match_id','bat_runs_ball','bat_wkt_ball','bowl_runs_ball','bowl_wkt_ball','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras_ball']], on=['match_id'])
    sample['bat_runs_ball'] *= sample['batter_bf']
    sample['0s_ball'] *= sample['batter_bf']
    sample['1s_ball'] *= sample['batter_bf']
    sample['2s_ball'] *= sample['batter_bf']
    sample['4s_ball'] *= sample['batter_bf']
    sample['6s_ball'] *= sample['batter_bf']
    sample['bat_wkt_ball'] *= sample['batter_bf'] 
    #sample['bowl_runs_ball'] *= sample['bowler_bb']
    sample['bowl_wkt_ball'] *= sample['bowler_bb']
    
    sample['over'] = np.ceil(sample['ball'])
    per_ball = sample.pivot_table(index=['over'],values=['batter_bf','runs_off_bat','extras','wicket_bowler','wicket_striker','wicket_non_striker',
                                                         'bat_runs_ball','bat_wkt_ball','bowl_runs_ball','bowl_wkt_ball','0s','0s_ball','1s','1s_ball',
                                                         '2s','2s_ball','4s','4s_ball','6s','6s_ball','extras_ball'],aggfunc='sum')
    per_ball = per_ball.reset_index()    
    per_ball['bat_runs_adj'] = per_ball['runs_off_bat']/per_ball['bat_runs_ball']
    per_ball['0s_adj'] = per_ball['0s']/per_ball['0s_ball']
    per_ball['1s_adj'] = per_ball['1s']/per_ball['1s_ball']
    per_ball['2s_adj'] = per_ball['2s']/per_ball['2s_ball']
    per_ball['4s_adj'] = per_ball['4s']/per_ball['4s_ball']
    per_ball['6s_adj'] = per_ball['6s']/per_ball['6s_ball']
    per_ball['extras_adj'] = per_ball['extras']/per_ball['extras_ball']
    per_ball['bowl_runs_adj'] = (per_ball['runs_off_bat']+per_ball['extras'])/per_ball['bowl_runs_ball']
    per_ball['bowl_wkt_adj'] = per_ball['wicket_bowler']/per_ball['bat_wkt_ball']
    per_ball['bat_wkt_adj'] = (per_ball['wicket_striker']+per_ball['wicket_non_striker'])/per_ball['bowl_wkt_ball']
    
    #using best fit for overs beyond 150
    fit = np.polyfit(per_ball['over'], per_ball['bat_runs_adj'], 1)
    per_ball.loc[per_ball['over']>150,'bat_runs_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['0s_adj'], 1)
    per_ball.loc[per_ball['over']>150,'0s_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['1s_adj'], 1)
    per_ball.loc[per_ball['over']>150,'1s_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['2s_adj'], 1)
    per_ball.loc[per_ball['over']>150,'2s_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['4s_adj'], 1)
    per_ball.loc[per_ball['over']>150,'4s_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['6s_adj'], 1)
    per_ball.loc[per_ball['over']>150,'6s_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['extras_adj'], 1)
    per_ball.loc[per_ball['over']>150,'extras_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['bat_wkt_adj'], 1)
    per_ball.loc[per_ball['over']>150,'bowl_runs_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['bowl_runs_adj'], 1)
    per_ball.loc[per_ball['over']>150,'bowl_runs_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    fit = np.polyfit(per_ball['over'], per_ball['bowl_wkt_adj'], 1)
    per_ball.loc[per_ball['over']>150,'bowl_wkt_adj'] = fit[1] + fit[0]*per_ball.loc[per_ball['over']>150,'over']
    
    sample = sample.merge(per_ball[['over','bat_runs_adj','bat_wkt_adj','bowl_runs_adj','bowl_wkt_adj','0s_adj','1s_adj','2s_adj','4s_adj','6s_adj','extras_adj']], on=['over'])
    sample['bat_runs_ball'] *= sample['bat_runs_adj']
    sample['0s_ball'] *= sample['0s_adj']
    sample['1s_ball'] *= sample['1s_adj']
    sample['2s_ball'] *= sample['2s_adj']
    sample['4s_ball'] *= sample['4s_adj']
    sample['6s_ball'] *= sample['6s_adj']
    sample['extras_ball'] *= sample['extras_adj']
    sample['bowl_runs_ball'] *= sample['bowl_runs_adj']
    sample['bat_wkt_ball'] *= sample['bat_wkt_adj']
    sample['bowl_wkt_ball'] *= sample['bowl_wkt_adj']
    
    #bat_pos = league_data(league)
    bat_pos = sample.pivot_table(index=['match_id','innings','batting_team','striker'],values=['ball'],aggfunc='min')
    bat_pos = bat_pos.reset_index()
    bat_pos = bat_pos.sort_values(by=['match_id', 'innings','ball'], ascending=[True, True, True])
    bat_pos['Pos'] = bat_pos.groupby(['match_id','innings']).cumcount() + 1
    
    bowl_pos = sample.pivot_table(index=['match_id','innings','bowling_team','bowler'],values=['ball'],aggfunc='min')
    bowl_pos = bowl_pos.reset_index()
    bowl_pos = bowl_pos.sort_values(by=['match_id', 'innings','ball'], ascending=[True, True, True])
    bowl_pos['Pos_bowler'] = bowl_pos.groupby(['match_id','innings']).cumcount() + 1
    
    sample = sample.merge(bat_pos[['match_id','innings','batting_team','striker','Pos']], on=['match_id','innings','batting_team','striker'], how='left')
    sample = sample.merge(bowl_pos[['match_id','innings','bowling_team','bowler','Pos_bowler']], on=['match_id','innings','bowling_team','bowler'], how='left')
    return sample

def league_conversion_factors(df, leagues, bat_bowl):
    combos = list(combinations(range(0,len(df)), 2))
    if(bat_bowl == 0): categories = ['rRuns','rWkts','r0s','r1s','r2s','r4s','r6s', 'rextras']; key = 'bowler'; bx = 'bowler_bb_x'; by = 'bowler_bb_y'
    else: categories = ['rRuns','rWkts','r0s','r1s','r2s','r4s','r6s']; key = 'striker'; bx = 'batter_bf_x'; by = 'batter_bf_y'
    all_eqn = [['category'] + leagues]

    for ch in categories:
        eqn = pd.DataFrame(columns=range(0,len(df)), index=range(0,len(combos)))
        eqn[f'{ch} log factor'] = 0.0
        eqn[f'{ch} balls'] = 0.0
        r = 0
        for c in combos:
            from_df = df[c[0]]
            to_df = df[c[1]]
            
            df_from_to = to_df.merge(from_df, on=[key,'season'])
            df_from_to['weighted'] = df_from_to[[bx,by]].min(axis=1)
            
            eqn.loc[r,c[0]] = 1
            eqn.loc[r,c[1]] = -1 #check this

            factor = np.log(((df_from_to[f'{ch}_x']*df_from_to['weighted']).sum()/df_from_to['weighted'].sum())/((df_from_to[f'{ch}_y']*df_from_to['weighted']).sum()/df_from_to['weighted'].sum()))
            
            tot_mins_sample = df_from_to[bx].sum() + df_from_to[by].sum()
            eqn.loc[r,f'{ch} log factor'] = factor
            eqn.loc[r,f'{ch} balls'] = tot_mins_sample
            r+=1
        
        eqn[list(range(0,len(df)))] = eqn[list(range(0,len(df)))].fillna(0) #.infer_objects(copy=False)
        eqn.replace([np.inf, -np.inf], np.nan, inplace=True)
        eqn = eqn[eqn[f'{ch} log factor'].notna()]
        
        regr = linear_model.LinearRegression(fit_intercept=False)
        regr.fit(eqn[list(range(0,len(df)))], eqn[f'{ch} log factor'], sample_weight=eqn[f'{ch} balls'])
        #all_eqn.append(eqn)
        #all_eqn.loc[r0] = list(regr.coef_) + [ch]
        coef_list = list(regr.coef_)
        minimum_element = min(coef_list)
        coef_list = [element - minimum_element for element in coef_list]
        #print(ch,coef_list)
        all_eqn.append([ch] + coef_list)

    all_eqn = pd.DataFrame(all_eqn)
    all_eqn.columns = all_eqn.iloc[0];all_eqn = all_eqn.drop(0)
    all_eqn = all_eqn.T
    all_eqn.columns = all_eqn.iloc[0]
    all_eqn = all_eqn.drop('category')
    all_eqn = all_eqn.apply(pd.to_numeric, errors='ignore')
    return all_eqn

def aging_analysis(df, bat_bowl):
    if(bat_bowl == 0): key = 'bowler'; bx = 'bowler_bb_x'; by = 'bowler_bb_y'
    else: key = 'striker'; bx = 'batter_bf_x'; by = 'batter_bf_y'
    
    df = pd.concat(df)
    df['age'] = (pd.to_datetime(df['season'], format='%Y')-df['dob']) / (pd.Timedelta(days=1)*365.25)
    df['age'] = df['age'].apply(np.floor)
    df = df[df['age']<=45]
    df['age'] = df['age'].astype(int)
    
    if(bat_bowl == 0): df_agg = df.pivot_table(index=[key,'age'],values=['bowler_bb','0s','1s','2s','4s','6s','extras','dismissals','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras_ball','bowl_wkt_ball'],aggfunc='sum')
    else: df_agg = df.pivot_table(index=[key,'age'],values=['batter_bf','0s','1s','2s','4s','6s','dismissals','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','bat_wkt_ball'],aggfunc='sum')
    df_agg = df_agg.reset_index()
    df_agg['r0s'] = df_agg['0s'] / df_agg['0s_ball']
    df_agg['r1s'] = df_agg['1s'] / df_agg['1s_ball']
    df_agg['r2s'] = df_agg['2s'] / df_agg['2s_ball']
    df_agg['r4s'] = df_agg['4s'] / df_agg['4s_ball']
    df_agg['r6s'] = df_agg['6s'] / df_agg['6s_ball']
    if(bat_bowl == 0): 
        df_agg['rextras'] = df_agg['extras'] / df_agg['extras_ball']
        df_agg['rWkts'] = df_agg['dismissals'] / df_agg['bowl_wkt_ball']
    else:
        df_agg['rWkts'] = df_agg['dismissals'] / df_agg['bat_wkt_ball']
    
    combos = list(combinations(range(13,46), 2))
    if(bat_bowl == 0): categories = ['rWkts','r0s','r1s','r2s','r4s','r6s','rextras']
    else: categories = ['rWkts','r0s','r1s','r2s','r4s','r6s']
    
    all_eqn = [['category']+list(range(13,46))]
    
    for ch in categories:
        eqn = pd.DataFrame(index=range(0,len(combos)),columns=range(13,46))
        #eqn['from_age'] = 0
        #eqn['to_age'] = 0
        eqn[f'{ch} log factor'] = 0.0
        eqn[f'{ch} balls'] = 0.0
        r=0
        for c in combos: #range(13,46):
            from_df = df_agg[df_agg['age']==c[0]] #df[c[0]]
            to_df = df_agg[df_agg['age']==c[1]] #df[c[1]]
            
            df_from_to = to_df.merge(from_df, on=[key])
            df_from_to['weighted'] = df_from_to[[bx,by]].min(axis=1)
            
            eqn.loc[r,c[0]] = 1
            eqn.loc[r,c[1]] = -1 #check this
            try:
                factor = np.log(((df_from_to[f'{ch}_x']*df_from_to['weighted']).sum()/df_from_to['weighted'].sum())/((df_from_to[f'{ch}_y']*df_from_to['weighted']).sum()/df_from_to['weighted'].sum()))
                
                tot_mins_sample = df_from_to[bx].sum() + df_from_to[by].sum()
                #print(c,len(df_from_to),factor)
                eqn.loc[r,f'{ch} log factor'] = factor
                eqn.loc[r,f'{ch} balls'] = tot_mins_sample
            except KeyError:
                eqn
            r+=1
        
        eqn[list(range(13,46))] = eqn[list(range(13,46))].fillna(0) #.infer_objects(copy=False)
        eqn.replace([np.inf, -np.inf], np.nan, inplace=True)
        eqn = eqn[eqn[f'{ch} log factor'].notna()]
        #eqn = eqn.reset_index()
        #eqn['age^2'] = eqn['index']*eqn['index']
        
        regr = linear_model.LinearRegression(fit_intercept=False)
        regr.fit(eqn[range(13,46)], eqn[f'{ch} log factor'], sample_weight=eqn[f'{ch} balls'])
        coef_list = list(regr.coef_)
        all_eqn.append([ch] + coef_list)

    all_eqn = pd.DataFrame(all_eqn)
    all_eqn.columns = all_eqn.iloc[0];all_eqn = all_eqn.drop(0)
    all_eqn = all_eqn.T
    all_eqn.columns = all_eqn.iloc[0]
    all_eqn = all_eqn.drop('category')
    all_eqn = all_eqn.apply(pd.to_numeric, errors='ignore')
    all_eqn = all_eqn.reset_index()
    if(bat_bowl == 0): all_eqn.columns = ['age', 'rWkts', 'r0s', 'r1s', 'r2s', 'r4s', 'r6s', 'rextras']
    else: all_eqn.columns = ['age', 'rWkts', 'r0s', 'r1s', 'r2s', 'r4s', 'r6s']
    all_eqn['age2'] = all_eqn['age']*all_eqn['age']
    
    final_eqn = [['category','intercept','age','age^2','var']]
    for c in categories:
        model = smf.mixedlm(f"{c} ~ age + age2", data=all_eqn, groups=all_eqn['age'])
        result = model.fit()
        params = result.params
        final_eqn.append([c]+list(params))
        
    final_eqn = pd.DataFrame(final_eqn)
    final_eqn.columns = final_eqn.iloc[0];final_eqn = final_eqn.drop(0)
    final_eqn = final_eqn.apply(pd.to_numeric, errors='ignore')
    return final_eqn

def extract_all_league_stats(leagues):
    df_game_stats = []; df_conversion = []
    df_game_stats_bowl = []; df_conversion_bowl = []
    player_age = pd.read_excel(f'{path}/excel/people.xlsx','people')
    player_age = player_age[['unique_name', 'dob', 'batType', 'bowlType']]
    
    for l in leagues:
        sample = league_data(l)
        
        batter = sample.pivot_table(index=['striker','batting_team','start_date'],values=['batter_bf','runs_off_bat','wicket_bowler','wicket_striker',
                                                                                          'wicket_non_striker','bat_runs_ball','bat_wkt_ball',
                                                                                          '0s','1s','2s','4s','6s','0s_ball','1s_ball','2s_ball',
                                                                                          '4s_ball','6s_ball'],aggfunc='sum')
        batter = batter.reset_index()
        #batter['Pos'] /= batter['batter_bf']
        batterp = sample.pivot_table(index=['striker','batting_team','start_date'],values=['Pos'],aggfunc='mean')
        batter = batter.merge(batterp, on=['striker','batting_team','start_date'], how='left')
        
        batter2 = sample.pivot_table(index=['non_striker','batting_team','start_date'],values=['wicket_non_striker'],aggfunc='sum')
        batter2 = batter2.reset_index()
        batter2.columns = ['striker','batting_team','start_date','wicket_non_striker']
        batter = batter.merge(batter2, on=['striker','batting_team','start_date'], how='left')
        batter = batter.merge(player_age, left_on=['striker'], right_on=['unique_name'], how='left')
        batter['wicket_non_striker_y'] = batter['wicket_non_striker_y'].fillna(0)
        batter['dismissals'] = batter['wicket_striker']+batter['wicket_non_striker_y']
        batter['start_date'] = pd.to_datetime(batter['start_date'], format='%Y-%m-%d')
        #batter['delta'] = datetime.now() - batter['start_date']
        #batter['delta'] = batter['delta'].dt.total_seconds()/(60*60*24)
        #batter['delta'] = pow(.999,batter['delta'])
        batter['season'] = batter['start_date'].dt.year
        batter['dob'] = pd.to_datetime(batter['dob'],errors='coerce')
        batter['age'] = (batter['start_date'] - batter['dob']) / (pd.Timedelta(days=1)*365.25)
        df_game_stats.append(batter)
        
        batter_season = batter.pivot_table(index=['striker','season'],values=['bat_runs_ball','bat_wkt_ball','batter_bf','runs_off_bat','dismissals','0s',
                                                                              '1s','2s','4s','6s','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball'],aggfunc='sum')
        batter_season = batter_season.reset_index()
        batter_season2 = batter.pivot_table(index=['striker','season'],values=['age'],aggfunc='mean')
        batter_season2 = batter_season2.reset_index()
        batter_season['rRuns'] = batter_season['runs_off_bat'] / batter_season['bat_runs_ball']
        batter_season['r0s'] = batter_season['0s'] / batter_season['0s_ball']
        batter_season['r1s'] = batter_season['1s'] / batter_season['1s_ball']
        batter_season['r2s'] = batter_season['2s'] / batter_season['2s_ball']
        batter_season['r4s'] = batter_season['4s'] / batter_season['4s_ball']
        batter_season['r6s'] = batter_season['6s'] / batter_season['6s_ball']
        batter_season['rWkts'] = batter_season['dismissals'] / batter_season['bat_wkt_ball']
        batter_season = batter_season.merge(batter_season2, on=['striker','season'], how='left')
        df_conversion.append(batter_season)
        
        bowler = sample.pivot_table(index=['bowler','bowling_team','start_date'],values=['bowler_bb','runs_off_bat','wicket_bowler','bowl_runs_ball',
                                                                                         'bowl_wkt_ball','0s','1s','2s','4s','6s','0s_ball','1s_ball',
                                                                                         '2s_ball','4s_ball','6s_ball','extras','extras_ball'],aggfunc='sum')
        bowler = bowler.reset_index()
        #bowler['Pos_bowler'] /= bowler['bowler_bb']
        bowlerp = sample.pivot_table(index=['bowler','bowling_team','start_date'],values=['Pos_bowler'],aggfunc='mean')
        bowler = bowler.merge(bowlerp, on=['bowler','bowling_team','start_date'], how='left')
        
        bowler = bowler.merge(player_age, left_on=['bowler'], right_on=['unique_name'], how='left')
        bowler['dismissals'] = bowler['wicket_bowler']
        bowler['start_date'] = pd.to_datetime(bowler['start_date'], format='%Y-%m-%d')
        bowler['season'] = bowler['start_date'].dt.year
        bowler['dob'] = pd.to_datetime(bowler['dob'],errors='coerce')
        bowler['age'] = (bowler['start_date'] - bowler['dob']) / (pd.Timedelta(days=1)*365.25)
        df_game_stats_bowl.append(bowler)
        
        bowler_season = bowler.pivot_table(index=['bowler','season'],values=['bowl_runs_ball','bowl_wkt_ball','bowler_bb','runs_off_bat','dismissals','0s',
                                                                             '1s','2s','4s','6s','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras','extras_ball'],aggfunc='sum')
        bowler_season = bowler_season.reset_index()
        bowler_season2 = bowler.pivot_table(index=['bowler','season'],values=['age'],aggfunc='mean')
        bowler_season2 = bowler_season2.reset_index()
        bowler_season['rRuns'] = (bowler_season['runs_off_bat']+bowler_season['extras']) / bowler_season['bowl_runs_ball']
        bowler_season['r0s'] = bowler_season['0s'] / bowler_season['0s_ball']
        bowler_season['r1s'] = bowler_season['1s'] / bowler_season['1s_ball']
        bowler_season['r2s'] = bowler_season['2s'] / bowler_season['2s_ball']
        bowler_season['r4s'] = bowler_season['4s'] / bowler_season['4s_ball']
        bowler_season['r6s'] = bowler_season['6s'] / bowler_season['6s_ball']
        bowler_season['rextras'] = bowler_season['extras'] / bowler_season['extras_ball']
        bowler_season['rWkts'] = bowler_season['dismissals'] / bowler_season['bowl_wkt_ball']
        bowler_season = bowler_season.merge(bowler_season2, on=['bowler','season'], how='left')
        df_conversion_bowl.append(bowler_season)
        
    conversions = league_conversion_factors(df_conversion, leagues, 1)
    conversions_bowl = league_conversion_factors(df_conversion_bowl, leagues, 0)
    #aging = aging_analysis(df_conversion)    
    return df_game_stats, conversions, df_game_stats_bowl, conversions_bowl

def apply_factors(df_list, df_factors, target, league_list, bat_bowl):
    c=0; df_list_modified = [];
    if(bat_bowl == 0): df_scale = [['league','scaled_balls','scaled_runs','scaled_dismissals', 'scaled_0s','scaled_1s','scaled_2s','scaled_4s','scaled_6s','scaled_extras','matches']]
    else: df_scale = [['league','scaled_balls','scaled_runs','scaled_dismissals', 'scaled_0s','scaled_1s','scaled_2s','scaled_4s','scaled_6s','matches']]

    for l in league_list:
        df = df_list[c]
        df['runs_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[0]
        df['wickets_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[1]
        df['0s_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[2]
        df['1s_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[3]
        df['2s_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[4]
        df['4s_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[5]
        df['6s_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[6]
        if(bat_bowl == 0): df['extras_factor'] = np.exp(df_factors.loc[l] - df_factors.loc[target]).values[7]
        df['league'] = l
        m = pd.read_csv(f'{path}/raw/{l}.csv',sep=',',low_memory=False)
        m = len(m['match_id'].unique())
        df_list_modified.append(df)
        
        if(bat_bowl == 0):
            df_scale.append([l,df['bowler_bb'].sum(),(df['runs_off_bat'].sum()+df['extras'].sum()),df['dismissals'].sum(),
                             df['0s'].sum(),df['1s'].sum(),df['2s'].sum(),df['4s'].sum(),df['6s'].sum(),df['extras'].sum(),m])
        else:
            df_scale.append([l,df['batter_bf'].sum(),df['runs_off_bat'].sum(),df['dismissals'].sum(),
                             df['0s'].sum(),df['1s'].sum(),df['2s'].sum(),df['4s'].sum(),df['6s'].sum(),m])
                
        c+=1
    
    df_scale = pd.DataFrame(df_scale[1:], columns=df_scale[0])
    return df_list_modified,df_scale

def league_scaling(df_scaling,target,bat_bowl):
    if(bat_bowl == 0): scaled_list = ['scaled_balls','scaled_runs','scaled_dismissals','scaled_0s','scaled_1s','scaled_2s','scaled_4s','scaled_6s', 'scaled_extras']
    else: scaled_list = ['scaled_balls','scaled_runs','scaled_dismissals','scaled_0s','scaled_1s','scaled_2s','scaled_4s','scaled_6s']
    
    for k in scaled_list:
        df_scaling[k] /= df_scaling['matches']
        
    for c in df_scaling.columns:
        if(c!='league'):
            t_value = df_scaling.loc[df_scaling['league']==target,c].values[0]
            df_scaling[c] = t_value/df_scaling[c]
            
    df_scaling = df_scaling.drop('matches',axis=1)
    return df_scaling

def stats_concat(df,df_scale, bat_bowl):
    df = pd.concat(df)
    #league scaling for no of balls
    df = df.merge(df_scale, on=['league'], how='left')
    if(bat_bowl == 0):
        df['runs_off_bat'] *= df['scaled_runs']
        df['bowl_runs_ball'] *= df['scaled_runs']
        df['dismissals'] *= df['scaled_dismissals']
        df['bowl_wkt_ball'] *= df['scaled_dismissals']
        df['bowler_bb'] *= df['scaled_balls']
        df['extras'] *= df['scaled_extras']
        df['extras_ball'] *= df['scaled_extras']
    else:
        df['runs_off_bat'] *= df['scaled_runs']
        df['bat_runs_ball'] *= df['scaled_runs']
        df['dismissals'] *= df['scaled_dismissals']
        df['bat_wkt_ball'] *= df['scaled_dismissals']
        df['batter_bf'] *= df['scaled_balls']
        
    df['0s'] *= df['scaled_0s']
    df['1s'] *= df['scaled_1s']
    df['2s'] *= df['scaled_2s']
    df['4s'] *= df['scaled_4s']
    df['6s'] *= df['scaled_6s']
    df['0s_ball'] *= df['scaled_0s']
    df['1s_ball'] *= df['scaled_1s']
    df['2s_ball'] *= df['scaled_2s']
    df['4s_ball'] *= df['scaled_4s']
    df['6s_ball'] *= df['scaled_6s']
    
    #league conversions for level of competition
    df['runs_off_bat'] *= df['runs_factor']
    df['dismissals'] *= df['wickets_factor']
    df['0s'] *= df['0s_factor']
    df['1s'] *= df['1s_factor']
    df['2s'] *= df['2s_factor']
    df['4s'] *= df['4s_factor']
    df['6s'] *= df['6s_factor']
    if(bat_bowl == 0): df['extras'] *= df['extras_factor']
    
    if(bat_bowl == 0): df = df.sort_values(by=['bowler', 'start_date'], ascending=[True, True])
    else: df = df.sort_values(by=['striker', 'start_date'], ascending=[True, True])
    return df

def bowling_usage(lg,df_bat,df_bowl):
    if(lg in test_leagues()): limit = 225*6/5
    elif(lg in short_leagues()): limit = 100/5
    elif(lg in odi_leagues()): limit = 300/5
    else: limit = 120/5
    
    bowler_usage = df_bowl[['bowler','bowling_team','start_date','bowler_bb']].merge(df_bat[['striker','batting_team','start_date']], 
                                                                                    left_on=['bowler','bowling_team','start_date'], 
                                                                                    right_on=['striker','batting_team','start_date'], how='outer')
    
    bowler_usage['bowler'] = bowler_usage['bowler'].fillna(bowler_usage['striker'])
    bowler_usage['bowler_bb'] = bowler_usage['bowler_bb'].fillna(0)
    bowler_usage = bowler_usage[['bowler','start_date','bowler_bb']]
    bowler_usage = bowler_usage.sort_values(by=['bowler','start_date'], ascending=[True,True])
    
    adj_usage = [['bowler','bowler_bb']]
    for n in bowler_usage['bowler'].unique():
        print(n)
        try:
            mean_bb, std_bb = kalman_filtering(bowler_usage,n,'bowler_bb',0)
            adj_usage.append([n,mean_bb[-1]])
        except IndexError:
            adj_usage.append([n,0])
            
    adj_usage = pd.DataFrame(adj_usage[1:], columns=adj_usage[0])    
    adj_usage['bowler_bb'] /= limit
    return adj_usage

def kalman_filtering(df,player,s1,bat_bowl):    
    if(bat_bowl==1): key = 'striker'#; df = batter
    elif(bat_bowl==-1): key = 'short'#; df = batter
    else: key = 'bowler'#; df = bowler
    
    if(s1 in ['runs_off_bat','1s','2s','4s','6s'] and bat_bowl == 1): mf = 2
    elif(s1 in ['runs_off_bat','1s','2s','4s','6s','extras'] and bat_bowl == 0): mf = 1/2
    elif(s1 in ['dismissals','0s'] and bat_bowl == 1): mf = 1/2
    elif(s1 in ['dismissals','0s'] and bat_bowl == 0): mf = 2
    elif(s1 in ['Pos_bowler'] and bat_bowl == 0): mf = np.mean(df[s1])/11
    else: mf = 1
    
    kf = KalmanFilter(transition_matrices = [1],
                      observation_matrices = [1],
                      initial_state_mean = np.mean(df[s1])/mf,
                      initial_state_covariance = (1*np.std(df[s1]))**2,
                      observation_covariance = (1*np.std(df[s1]))**2,
                      transition_covariance = (.05*np.std(df[s1]))**2)
    
    stat = df.loc[df[key]==player,s1]
    mean, cov = kf.filter(stat.values)
    mean, std = mean.squeeze(), np.std(cov.squeeze())
    return mean,std

def kalman_stats_batting(df,player,print_val):
    t_start = datetime.now()
    mean_age, std_age = kalman_filtering(df,player,'age',1)
    mean_pos, std_pos = kalman_filtering(df,player,'Pos',1)
    mean_bf, std_bf = kalman_filtering(df,player,'batter_bf',1)
    #mean_runs, std_runs = kalman_filtering(df,player,'runs_off_bat',1)
    #mean_xruns, std_xruns = kalman_filtering(df,player,'bat_runs_ball',1)
    mean_dismissals, std_runs = kalman_filtering(df,player,'dismissals',1)
    mean_xdismissals, std_xruns = kalman_filtering(df,player,'bat_wkt_ball',1)
    
    mean_0s, std_0s = kalman_filtering(df,player,'0s',1)
    mean_x0s, std_x0s = kalman_filtering(df,player,'0s_ball',1)
    mean_1s, std_1s = kalman_filtering(df,player,'1s',1)
    mean_x1s, std_x1s = kalman_filtering(df,player,'1s_ball',1)
    mean_2s, std_2s = kalman_filtering(df,player,'2s',1)
    mean_x2s, std_x2s = kalman_filtering(df,player,'2s_ball',1)
    mean_4s, std_4s = kalman_filtering(df,player,'4s',1)
    mean_x4s, std_x4s = kalman_filtering(df,player,'4s_ball',1)
    mean_6s, std_6s = kalman_filtering(df,player,'6s',1)
    mean_x6s, std_x6s = kalman_filtering(df,player,'6s_ball',1)
    
    try:
        age = mean_age[-1]
        pos = mean_pos[-1]
        
        mean_runs = mean_1s[-1] + 2*mean_2s[-1] + 4*mean_4s[-1] + 6*mean_6s[-1]
        mean_xruns = mean_x1s[-1] + 2*mean_x2s[-1] + 4*mean_x4s[-1] + 6*mean_x6s[-1]
        #mean_0s = mean_bf[-1]*(1 - (mean_1s[-1] + mean_2s[-1] + mean_4s[-1] + mean_6s[-1]))
        #mean_x0s = mean_bf[-1]*(1 - (mean_x1s[-1] + mean_x2s[-1] + mean_x4s[-1] + mean_x6s[-1]))
        
        avg = mean_runs/mean_dismissals[-1]
        xavg = mean_xruns/mean_xdismissals[-1]
        sr = 100*mean_runs/mean_bf[-1]
        xsr = 100*mean_xruns/mean_bf[-1]
        bpd = mean_bf[-1]/mean_dismissals[-1]
        xbpd = mean_bf[-1]/mean_xdismissals[-1]
        
        r0s = mean_0s[-1]/mean_x0s[-1]
        r1s = mean_1s[-1]/mean_x1s[-1]
        r2s = mean_2s[-1]/mean_x2s[-1]
        r4s = mean_4s[-1]/mean_x4s[-1]
        r6s = mean_6s[-1]/mean_x6s[-1]
        
    except IndexError:
        age = mean_age.item()
        pos = mean_pos.item()
        
        mean_runs = mean_1s.item() + 2*mean_2s.item() + 4*mean_4s.item() + 6*mean_6s.item()
        mean_xruns = mean_x1s.item() + 2*mean_x2s.item() + 4*mean_x4s.item() + 6*mean_x6s.item()
        #mean_0s = mean_bf[-1]*(1 - (mean_1s[-1] + mean_2s[-1] + mean_4s[-1] + mean_6s[-1]))
        #mean_x0s = mean_bf[-1]*(1 - (mean_x1s[-1] + mean_x2s[-1] + mean_x4s[-1] + mean_x6s[-1]))
        
        avg = mean_runs/mean_dismissals.item()
        xavg = mean_xruns/mean_xdismissals.item()
        sr = 100*mean_runs/mean_bf.item()
        xsr = 100*mean_xruns/mean_bf.item()
        bpd = mean_bf.item()/mean_dismissals.item()
        xbpd = mean_bf.item()/mean_xdismissals.item()
        
        r0s = mean_0s.item()/mean_x0s.item()
        r1s = mean_1s.item()/mean_x1s.item()
        r2s = mean_2s.item()/mean_x2s.item()
        r4s = mean_4s.item()/mean_x4s.item()
        r6s = mean_6s.item()/mean_x6s.item()
    
    t_end = datetime.now()
    if(print_val==1):
        print(player,age)
        print("rAVG",avg/xavg)
        print("rSR",sr/xsr)
        print("rBPD",bpd/xbpd)
        print()
        print("AVG",avg)
        print("xAVG",xavg)
        print("SR",sr)
        print("xSR",xsr)
        print("BPD",bpd)
        print("xBPD",xbpd)
        print()
        print('time',(t_end-t_start).total_seconds())
    else:
        print(player, (t_end-t_start).total_seconds())
        return [player,age,pos,avg/xavg,sr/xsr,bpd/xbpd,avg,xavg,sr,xsr,bpd,xbpd,r0s,r1s,r2s,r4s,r6s]
    
def kalman_stats_bowling(df,player,print_val):
    t_start = datetime.now()
    mean_age, std_age = kalman_filtering(df,player,'age',0)
    mean_pos, std_pos = kalman_filtering(df,player,'Pos_bowler',0)
    
    mean_bf, std_bf = kalman_filtering(df,player,'bowler_bb',0)
    mean_runs, std_runs = kalman_filtering(df,player,'runs_off_bat',0)
    mean_xruns, std_xruns = kalman_filtering(df,player,'bowl_runs_ball',0)
    mean_dismissals, std_runs = kalman_filtering(df,player,'dismissals',0)
    mean_xdismissals, std_xruns = kalman_filtering(df,player,'bowl_wkt_ball',0)
    
    mean_0s, std_0s = kalman_filtering(df,player,'0s',0)
    mean_x0s, std_x0s = kalman_filtering(df,player,'0s_ball',0)
    mean_1s, std_1s = kalman_filtering(df,player,'1s',0)
    mean_x1s, std_x1s = kalman_filtering(df,player,'1s_ball',0)
    mean_2s, std_2s = kalman_filtering(df,player,'2s',0)
    mean_x2s, std_x2s = kalman_filtering(df,player,'2s_ball',0)
    mean_4s, std_4s = kalman_filtering(df,player,'4s',0)
    mean_x4s, std_x4s = kalman_filtering(df,player,'4s_ball',0)
    mean_6s, std_6s = kalman_filtering(df,player,'6s',0)
    mean_x6s, std_x6s = kalman_filtering(df,player,'6s_ball',0)
    mean_extras, std_extras = kalman_filtering(df,player,'extras',0)
    mean_xextras, std_xextras = kalman_filtering(df,player,'extras_ball',0)
    
    try:
        age = mean_age[-1]
        pos = mean_pos[-1]
        avg = (mean_runs[-1]+mean_extras[-1])/mean_dismissals[-1]
        xavg = mean_xruns[-1]/mean_xdismissals[-1]
        sr = mean_bf[-1]/mean_dismissals[-1]
        xsr = mean_bf[-1]/mean_xdismissals[-1]
        econ = 6*(mean_runs[-1]+mean_extras[-1])/mean_bf[-1]
        xecon = 6*mean_xruns[-1]/mean_bf[-1]
        
        r0s = mean_0s[-1]/mean_x0s[-1]
        r1s = mean_1s[-1]/mean_x1s[-1]
        r2s = mean_2s[-1]/mean_x2s[-1]
        r4s = mean_4s[-1]/mean_x4s[-1]
        r6s = mean_6s[-1]/mean_x6s[-1]
        rextras = mean_extras[-1]/mean_xextras[-1]
        
    except IndexError:
        age = mean_age.item()
        pos = mean_pos.item()
        avg = (mean_runs.item()+mean_extras.item())/mean_dismissals.item()
        xavg = mean_xruns.item()/mean_xdismissals.item()
        sr = mean_bf.item()/mean_dismissals.item()
        xsr = mean_bf.item()/mean_xdismissals.item()
        econ = 6*(mean_runs.item()+mean_extras.item())/mean_bf.item()
        xecon = 6*mean_xruns.item()/mean_bf.item()
        
        r0s = mean_0s.item()/mean_x0s.item()
        r1s = mean_1s.item()/mean_x1s.item()
        r2s = mean_2s.item()/mean_x2s.item()
        r4s = mean_4s.item()/mean_x4s.item()
        r6s = mean_6s.item()/mean_x6s.item()
        rextras = mean_extras.item()/mean_xextras.item()
    
    t_end = datetime.now()
    if(print_val==1):
        print(player)
        print("rAVG",avg/xavg)
        print("rSR",sr/xsr)
        print("rECON",econ/xecon)
        print()
        print("AVG",avg)
        print("xAVG",xavg)
        print("SR",sr)
        print("xSR",xsr)
        print("ECON",econ)
        print("xECON",xecon)
        print('time',(t_end-t_start).total_seconds())
    else:
        print(player, (t_end-t_start).total_seconds())
        return [player,age,pos,avg/xavg,sr/xsr,econ/xecon,avg,xavg,sr,xsr,econ,xecon,r0s,r1s,r2s,r4s,r6s,rextras]

def kalman_summary(df, bat_bowl):
    if(bat_bowl == 0): 
        summary = [['player','w_age','Pos_bowler','rAVG','rSR','rECON','AVG','xAVG','SR','xSR','ECON','xECON','r0s','r1s','r2s','r4s','r6s','rextras']]
        key = 'bowler'
        typebowl = df[['bowler','bowlType']].drop_duplicates()
        typebowl['type'] = typebowl['bowlType'].isin(['Right-arm offbreak','Legbreak googly','Legbreak','Slow left-arm orthodox',
                                                      'Left-arm wrist-spin','Right-arm offbreak (underarm)'])
        typebowl['type'] = typebowl['type'].replace({True: 'spin', False: 'pace'})
    else: 
        summary = [['player','w_age','Pos','rAVG','rSR','rBPD','AVG','xAVG','SR','xSR','BPD','xBPD','r0s','r1s','r2s','r4s','r6s']]
        key = 'striker'
    
    for n in df[key].unique():
        try: 
            if(bat_bowl == 1): summary.append(kalman_stats_batting(df,n,0))
            else: summary.append(kalman_stats_bowling(df,n,0))
        except: summary
        
    summary = pd.DataFrame(summary[1:], columns=summary[0])
    if(bat_bowl == 0): summary = summary.merge(typebowl, left_on='player', right_on='bowler', how='left')
    return summary

def apply_aging_factors(df,af,df_full,bat_bowl):
    if(bat_bowl == 0): key = 'bowler'
    else: key = 'striker'
        
    dob = df_full[[key,'dob']].drop_duplicates()
    dob['age'] = (datetime.now()-dob['dob']) / (pd.Timedelta(days=1)*365.25)
    
    df = df.merge(dob[[key,'age']],left_on=['player'],right_on=[key],how='left')
    for c in af['category'].to_list():
        a = af.loc[af['category']==c,'age'].values[0]
        a2 = af.loc[af['category']==c,'age^2'].values[0]
        df[f'{c}_aging'] = np.exp(a*(df['age']-df['w_age']) + a2*np.pow(df['age']-df['w_age'],2))
        df[f'{c}_aging'] = df[f'{c}_aging'].fillna(1)
    
    df['r0s'] *= df['r0s_aging']
    df['r1s'] *= df['r1s_aging']
    df['r2s'] *= df['r2s_aging']
    df['r4s'] *= df['r4s_aging']
    df['r6s'] *= df['r6s_aging']
    if(bat_bowl == 0):
        df['rextras'] *= df['rextras_aging']
        df['rSR'] /= df['rWkts_aging']
        df = df[['player','type','age','Pos_bowler','rSR','r0s', 'r1s', 'r2s', 'r4s', 'r6s', 'rextras']]
    else:
        df['rBPD'] /= df['rWkts_aging']
        df = df[['player','age','Pos','rBPD','r0s', 'r1s', 'r2s', 'r4s', 'r6s']]
    return df

def game_matrix(l):
    venues = pd.read_excel(f'{path}/excel/venues.xlsx','Sheet1')
    people = pd.read_excel(f'{path}/excel/people.xlsx','people')
    #people = people[['unique_name','bowlType']]
    
    if(l in ['tests']): target_list = test_leagues()
    elif(l in ['odi']): target_list = odi_leagues()
    elif(l in ['hundred']): target_list = short_leagues()
    else: target_list = t20_leagues()
    
    league_stats_concat = []
    for l2 in target_list:
        sample = league_data(l2)
        league_stats_concat.append(sample)
        
    league_stats_concat = pd.concat(league_stats_concat)
    league_stats_concat['start_date'] = pd.to_datetime(league_stats_concat['start_date'], format='%Y-%m-%d')
    #league_stats_concat = league_stats_concat.sort_values(by=['start_date'], ascending=[True])
    league_stats_concat['weight'] = (datetime.now() - league_stats_concat['start_date']) / (pd.Timedelta(days=1))
    league_stats_concat['weight'] = pow(.9995,league_stats_concat['weight'])
    innings = league_stats_concat.drop_duplicates(subset = 'match_id')['weight'].sum() #'innings'
    
    if(l == 'tests'): filtered_concat = league_stats_concat
    else: filtered_concat = league_stats_concat[league_stats_concat['innings']==1]
    
    avg_stats_bat = filtered_concat.pivot_table(index=['Pos'],
                                                values=['batter_bf', 'bat_wkt_ball', '0s_ball', '1s_ball', '2s_ball', '4s_ball', '6s_ball'],
                                                aggfunc=lambda rows: np.sum(rows * league_stats_concat.loc[rows.index, 'weight']))
    
    avg_stats_bat['BPG'] = avg_stats_bat['batter_bf']/(innings*len(target_list))
    avg_stats_bat['BPD'] = avg_stats_bat['batter_bf']/avg_stats_bat['bat_wkt_ball']
    avg_stats_bat['BPD_ratio'] = avg_stats_bat['BPG']/avg_stats_bat['BPD']
    avg_stats_bat['0s_ball'] = avg_stats_bat['0s_ball']/avg_stats_bat['batter_bf']
    avg_stats_bat['1s_ball'] = avg_stats_bat['1s_ball']/avg_stats_bat['batter_bf']
    avg_stats_bat['2s_ball'] = avg_stats_bat['2s_ball']/avg_stats_bat['batter_bf']
    avg_stats_bat['4s_ball'] = avg_stats_bat['4s_ball']/avg_stats_bat['batter_bf']
    avg_stats_bat['6s_ball'] = avg_stats_bat['6s_ball']/avg_stats_bat['batter_bf']
    avg_stats_bat['bat_wkt_ball'] = avg_stats_bat['bat_wkt_ball']/avg_stats_bat['batter_bf']
    avg_stats_bat = avg_stats_bat[['BPD','BPD_ratio','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','bat_wkt_ball']]
    avg_stats_bat = avg_stats_bat.reset_index()
    print("batting matrix done")

    avg_stats_bowl = filtered_concat.pivot_table(index=['Pos_bowler'],
                                                 values=['bowler_bb', 'bowl_wkt_ball', '0s_ball', '1s_ball', '2s_ball', '4s_ball', '6s_ball', 'extras_ball'], 
                                                 aggfunc=lambda rows: np.sum(rows * league_stats_concat.loc[rows.index, 'weight']))
    avg_stats_bowl['BPG'] = avg_stats_bowl['bowler_bb']/(innings*len(target_list))
    avg_stats_bowl['0s_ball'] = avg_stats_bowl['0s_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl['1s_ball'] = avg_stats_bowl['1s_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl['2s_ball'] = avg_stats_bowl['2s_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl['4s_ball'] = avg_stats_bowl['4s_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl['6s_ball'] = avg_stats_bowl['6s_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl['extras_ball'] = avg_stats_bowl['extras_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl['bowl_wkt_ball'] = avg_stats_bowl['bowl_wkt_ball']/avg_stats_bowl['bowler_bb']
    avg_stats_bowl = avg_stats_bowl[['BPG','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras_ball','bowl_wkt_ball']]
    avg_stats_bowl = avg_stats_bowl.reset_index()
    print("bowling matrix done")
    
    league_stats_concat = league_stats_concat.merge(venues, on=['venue'], how='left')
    league_stats_concat = league_stats_concat.merge(people[['unique_name','bowlType']], left_on=['bowler'], right_on=['unique_name'], how='left')
    league_stats_concat['type'] = league_stats_concat['bowlType'].isin(['Right-arm offbreak','Legbreak googly','Legbreak','Slow left-arm orthodox',
                                                                        'Left-arm wrist-spin','Right-arm offbreak (underarm)'])
    league_stats_concat['type'] = league_stats_concat['type'].replace({True: 'spin', False: 'pace'})
    
    venue_stats = league_stats_concat.pivot_table(index=['start_date','match_id','short','type'], values=['batter_bf','bowler_bb','wicket_bowler',
                                                                                                   '0s','1s','2s','4s','6s','extras','bowl_wkt_ball',
                                                                                                   '0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras_ball'], aggfunc='sum')
    venue_stats = venue_stats.reset_index()
    
    venue_stats['r0s'] = (venue_stats['0s_ball']/venue_stats['batter_bf']) / (venue_stats['0s_ball'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r1s'] = (venue_stats['1s_ball']/venue_stats['batter_bf']) / (venue_stats['1s_ball'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r2s'] = (venue_stats['2s_ball']/venue_stats['batter_bf']) / (venue_stats['2s_ball'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r4s'] = (venue_stats['4s_ball']/venue_stats['batter_bf']) / (venue_stats['4s_ball'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r6s'] = (venue_stats['6s_ball']/venue_stats['batter_bf']) / (venue_stats['6s_ball'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['rextras'] = (venue_stats['extras_ball']/venue_stats['bowler_bb']) / (venue_stats['extras_ball'].sum()/venue_stats['bowler_bb'].sum())
    venue_stats['rwkts'] = (venue_stats['bowl_wkt_ball']/venue_stats['bowler_bb']) / (venue_stats['bowl_wkt_ball'].sum()/venue_stats['bowler_bb'].sum())
    #venue_stats['r0s'] = venue_stats['0s']/venue_stats['0s_ball']
    #venue_stats['r1s'] = venue_stats['1s']/venue_stats['1s_ball']
    #venue_stats['r2s'] = venue_stats['2s']/venue_stats['2s_ball']
    #venue_stats['r4s'] = venue_stats['4s']/venue_stats['4s_ball']
    #venue_stats['r6s'] = venue_stats['6s']/venue_stats['6s_ball']
    #venue_stats['rextras'] = venue_stats['extras']/venue_stats['extras_ball']
    #venue_stats['rwkts'] = venue_stats['wicket_bowler']/venue_stats['bowl_wkt_ball']
    venue_stats['start_date'] = pd.to_datetime(venue_stats['start_date'], format='%Y-%m-%d')
    venue_stats = venue_stats.sort_values(by=['start_date'], ascending=[True])
    venue_stats['weight'] = (datetime.now() - venue_stats['start_date']) / (pd.Timedelta(days=1))
    venue_stats['weight'] = pow(.9995,venue_stats['weight'])
    
    bias = venue_stats.pivot_table(index=['start_date','match_id','short'],columns=['type'],values=['bowler_bb','weight'],aggfunc='sum')
    bias = bias.reset_index()
    bias.columns = bias.columns.droplevel(1)
    bias.columns = ['start_date', 'match_id', 'short', 'pace', 'spin', 'weight', 'weight_copy']
    bias = bias.fillna(0)
    bias['spin_bias'] = bias['spin']/(bias['pace']+bias['spin'])
    bias['pace_bias'] = bias['pace']/(bias['pace']+bias['spin'])
    bias = bias.pivot_table(index=['short'], values=['pace_bias','spin_bias'], aggfunc=lambda rows: np.average(rows, weights = bias.loc[rows.index, 'weight']))
    bias = bias.reset_index()
    
    agg_venue_stats = venue_stats.pivot_table(index=['short','type'], values=['bowler_bb','r0s','r1s','r2s','r4s','r6s','rextras','rwkts'], 
                            aggfunc=lambda rows: np.average(rows, weights = venue_stats.loc[rows.index, 'weight']))
    
    regression_weight = venue_stats['bowler_bb'].mean()/2
    
    agg_venue_stats['r0s'] = (agg_venue_stats['r0s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r1s'] = (agg_venue_stats['r1s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r2s'] = (agg_venue_stats['r2s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r4s'] = (agg_venue_stats['r4s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r6s'] = (agg_venue_stats['r6s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['rextras'] = (agg_venue_stats['rextras']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['rwkts'] = (agg_venue_stats['rwkts']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats = agg_venue_stats.reset_index()
    agg_venue_stats = agg_venue_stats.merge(bias, on='short', how='left')
    agg_venue_stats['bias'] = np.where(agg_venue_stats['type'] == 'pace', agg_venue_stats['pace_bias'], agg_venue_stats['spin_bias'])
    agg_venue_stats = agg_venue_stats[['short','type','bias','r0s','r1s','r2s','r4s','r6s','rextras','rwkts']]
    agg_venue_stats = agg_venue_stats.rename(columns={'short': 'venue'})
    
    """
    agg_venue_stats = [['venue','type','bias','r0s','r1s','r2s','r4s','r6s','rextras','rwkts']]
    for g,t in venue_stats[['short','type']].drop_duplicates().values:
        try:
            print(g,t)
            ground = venue_stats[venue_stats['type']==t]
            mean_r0s, std_r0s = kalman_filtering(ground,g,'r0s',-1)
            mean_r1s, std_r1s = kalman_filtering(ground,g,'r1s',-1)
            mean_r2s, std_r2s = kalman_filtering(ground,g,'r2s',-1)
            mean_r4s, std_r4s = kalman_filtering(ground,g,'r4s',-1)
            mean_r6s, std_r6s = kalman_filtering(ground,g,'r6s',-1)
            mean_rextras, std_rextras = kalman_filtering(ground,g,'rextras',-1)
            #mean_rwkts_bat, std_rwkts_bat = kalman_filtering(ground,g,'rwkts_bat',-1)
            mean_rwkts_bowl, std_rwkts_bowl = kalman_filtering(ground,g,'rwkts',-1)
            mean_bias, std_bias = kalman_filtering(bias[['start_date','short',f'{t}_bias']],g,f'{t}_bias',-1)
            agg_venue_stats.append([g,t,mean_bias[-1],mean_r0s[-1],mean_r1s[-1],mean_r2s[-1],mean_r4s[-1],mean_r6s[-1],mean_rextras[-1],mean_rwkts_bowl[-1]])
        except IndexError:
            print(g, "ERROR")
            agg_venue_stats.append([g,t,mean_bias.item(),mean_r0s.item(),mean_r1s.item(),mean_r2s.item(),mean_r4s.item(),mean_r6s.item(),mean_rextras.item(),mean_rwkts_bowl.item()])
    
    agg_venue_stats = pd.DataFrame(agg_venue_stats[1:], columns=agg_venue_stats[0])
    """
    print("venue matrix done")
    return avg_stats_bat, avg_stats_bowl, agg_venue_stats

def match_calculations(lg,df,bat_bowl):
    if(lg in test_leagues()): innings = 2; limit = 225*6
    elif(lg in short_leagues()): innings = 1; limit = 100/5
    elif(lg in odi_leagues()): innings = 1; limit = 300/5
    else: innings = 1; limit = 120/5
    
    if(bat_bowl == 1): df['balls'] = df['rBPD'] * df['BPD'] * df['BPD_ratio'] * innings
    else: 
        df['balls'] = df['rballs'] * df['BPG'] * innings
        df['excess'] = df['balls'] - limit
        df.loc[df['excess'] < 0, 'excess'] = 0
        df['balls'] -= 2*df['excess']  
        excess = df['excess'].sum()
        df['balls'] += excess/len(df) 
    
    df['0s'] = df['r0s'] * df['balls'] * df['0s_ball']
    df['1s'] = df['r1s'] * df['balls'] * df['1s_ball']
    df['2s'] = df['r2s'] * df['balls'] * df['2s_ball']
    df['4s'] = df['r4s'] * df['balls'] * df['4s_ball']
    df['6s'] = df['r6s'] * df['balls'] * df['6s_ball']
    if(bat_bowl == 1):
        if(lg not in test_leagues()): wkt_adj = 5*limit/df['balls'].sum()
        else: wkt_adj = 1 
        
        df['dismissals'] = wkt_adj * df['balls'] * df['bat_wkt_ball'] / df['rBPD']
        if(df['dismissals'].sum() >= innings*10): df['dismissals'] *= (innings*10)/(df['dismissals'].sum())
    else:
        if(lg not in test_leagues()): wkt_adj = 5*limit/df['balls'].sum()
        else: wkt_adj = 1 
            
        df['extras'] = df['rextras'] * df['balls'] * df['extras_ball']
        df['wickets'] = wkt_adj * df['balls'] * df['bowl_wkt_ball'] / df['rSR']
        if(df['wickets'].sum() >= innings*10*0.95): df['wickets'] *= (innings*10*0.95)/(df['wickets'].sum())
        
    if(bat_bowl == 0): df['runs'] = df['1s'] + 2*df['2s'] + 4*df['4s'] + 6*df['6s'] + df['extras']
    else: df['runs'] = df['1s'] + 2*df['2s'] + 4*df['4s'] + 6*df['6s']
    
    if(bat_bowl == 1): df = df[['player', 'team', 'age', 'Pos', 'balls', '0s', '1s', '2s', '4s', '6s', 'dismissals', 'runs']]
    else: 
        df = df[['player', 'team', 'age', 'type', 'Pos_bowler', 'balls', '0s', '1s', '2s', '4s', '6s', 'extras', 'wickets', 'runs']]
        #df['ECON'] = 6*df['runs']/df['balls']
    return df

def balance(lg,bat,bowl):
    if(lg in test_leagues()): limit = 225*6
    elif(lg in short_leagues()): limit = 100
    elif(lg in odi_leagues()): limit = 300
    else: limit = 120
    
    factors = ['rBPD','r0s', 'r1s', 'r2s', 'r4s', 'r6s', '0s_ball', '1s_ball', '2s_ball', '4s_ball', '6s_ball', 'bat_wkt_ball']
    
    for f in factors:
        if(f=='rBPD'): batf = 'rBPD'; bowlf = 'rSR'; ratio = 0.95 #bowl wkts by bat wickets
        elif(f=='bat_wkt_ball'): batf = 'bat_wkt_ball'; bowlf = 'bowl_wkt_ball'; ratio = 1/0.95
        else: batf = f; bowlf = f; ratio = 1
        
        bat_val = (bat[batf]*bat['BPD']*bat['BPD_ratio']).sum()/(bat['BPD']*bat['BPD_ratio']).sum()
        bowl_val = ratio * (bowl[bowlf]*bowl['BPG']).sum()/(bowl['BPG'].sum())
        
        equalized_val = np.sqrt(bat_val*bowl_val)
        
        if(f=='rBPD'): bowl['rballs'] = equalized_val#; print(bat_val,bowl_val,(bat[batf]*bat['BPD']*bat['BPD_ratio']).sum())
        bat[batf] *= equalized_val/bat_val
        bowl[bowlf] *= equalized_val/bowl_val
    
    #print((bat['rBPD']*bat['BPD']*bat['BPD_ratio']).sum())
    #print((bat['bat_wkt_ball']*bat['BPD']*bat['BPD_ratio']).sum())
    #print(limit*(bat['bat_wkt_ball']*bat['BPD']*bat['BPD_ratio']).sum()/(bat['rBPD']*bat['BPD']*bat['BPD_ratio']).sum())
    
    wickets_in_limit_balls = limit*(bat['bat_wkt_ball']*bat['BPD']*bat['BPD_ratio']).sum()/(bat['rBPD']*bat['BPD']*bat['BPD_ratio']).sum()
    data = np.random.poisson(lam=wickets_in_limit_balls, size=1000)
    data = limit*10/data
    data = [min(x, limit) for x in data]
    balls_game = sum(data)/1000
    
    reduction = balls_game/(bat['rBPD']*bat['BPD']*bat['BPD_ratio']).sum()
    bat['BPD_ratio'] *= reduction
    bowl['rballs'] *= reduction
    
    bat['dismissals'] = bat['bat_wkt_ball']*bat['BPD']*bat['BPD_ratio']
    #print(bat['dismissals'])
    bat['BPD_ratio'] = np.where(bat['dismissals'] >= .99, bat['BPD_ratio']*1/bat['dismissals'], bat['BPD_ratio'])
    bat['bat_wkt_ball'] = np.where(bat['dismissals'] >= .99, bat['bat_wkt_ball']*1/bat['dismissals'], bat['bat_wkt_ball'])
    
    bowl['rballs'] *= (bat['rBPD']*bat['BPD']*bat['BPD_ratio']).sum()/balls_game
    #print((bat['rBPD']*bat['BPD']*bat['BPD_ratio']).sum(), balls_game)
    return bat, bowl

def rebalance(bat,bowl):
    factors = ['0s', '1s', '2s', '4s', '6s', 'dismissals']
    
    for f in factors:
        if(f=='dismissals'):
            bat_val = bat['dismissals'].sum()
            #print(bat['dismissals'])
            bowl_val = bowl['wickets'].sum()
            equalized_val = bat_val
            bat['dismissals'] *= equalized_val/bat_val
            bowl['wickets'] *= 0.95*equalized_val/bowl_val
        else:
            bat_val = bat[f].sum()
            bowl_val = bowl[f].sum()
            equalized_val = np.sqrt(bat_val*bowl_val)      
            bat[f] *= equalized_val/bat_val
            bowl[f] *= equalized_val/bowl_val
            
    return bat, bowl

def venues_adj(df, bat_bowl):
    df['r0s'] *= df['v_r0s']
    df['r1s'] *= df['v_r1s']
    df['r2s'] *= df['v_r2s']
    df['r4s'] *= df['v_r4s']
    df['r6s'] *= df['v_r6s']
    if(bat_bowl==0): 
        df['rSR'] /= df['v_rwkts']
        df['BPG'] *= df['bias']
    else: df['rBPD'] /= df['v_rwkts']
    return df

def game_sim(lg,t1,t2,venue):
    if(lg in test_leagues()): sheet_p = 'tests'; sheet_matrix = 'test'; limit = 225*6/5
    elif(lg in short_leagues()): sheet_p = 'lo'; sheet_matrix = 'hundred'; limit = 100/5
    elif(lg in odi_leagues()): sheet_p = 'lo'; sheet_matrix = 'odi'; limit = 300/5
    else: sheet_p = 'lo'; sheet_matrix = 't20'; limit = 120/5
    
    batter_projections = pd.read_excel(f'{path}/excel/projections.xlsx',f'{sheet_p} batters')
    bowler_projections = pd.read_excel(f'{path}/excel/projections.xlsx',f'{sheet_p} bowlers')
    squads = pd.read_excel(f'{path}/excel/projections.xlsx','squads')
    bat_matrix = pd.read_excel(f'{path}/excel/matrix.xlsx',f'{sheet_matrix} batting')
    bowl_matrix = pd.read_excel(f'{path}/excel/matrix.xlsx',f'{sheet_matrix} bowling')
    venue_matrix = pd.read_excel(f'{path}/excel/matrix.xlsx',f'{sheet_matrix} venues')
    
    batter_projections = batter_projections.merge(squads[['player','team']], on=['player'], how='left')
    bowler_projections = bowler_projections.merge(squads[['player','team']], on=['player'], how='left')
    
    pace_avg = venue_matrix.loc[venue_matrix['type']=='pace','bias'].mean()
    spin_avg = venue_matrix.loc[venue_matrix['type']=='spin','bias'].mean()
    
    bat_t1 = batter_projections[batter_projections['team']==t1]
    bowl_t1 = bowler_projections[bowler_projections['team']==t1]
    bat_t2 = batter_projections[batter_projections['team']==t2]
    bowl_t2 = bowler_projections[bowler_projections['team']==t2]

    bat_t1.loc[bat_t1.index,'Pos'] = bat_t1['Pos'].rank(method='dense', ascending=True)
    bat_t2.loc[bat_t2.index,'Pos'] = bat_t2['Pos'].rank(method='dense', ascending=True)
    bowl_t1.loc[bowl_t1.index,'Pos_bowler'] = bowl_t1['Pos_bowler'].rank(method='dense', ascending=True)
    bowl_t2.loc[bowl_t2.index,'Pos_bowler'] = bowl_t2['Pos_bowler'].rank(method='dense', ascending=True)

    bat_t1 = bat_t1.merge(bat_matrix, on=['Pos'], how='left')
    bat_t2 = bat_t2.merge(bat_matrix, on=['Pos'], how='left')
    bowl_t1 = bowl_t1.merge(bowl_matrix, on=['Pos_bowler'], how='left')
    bowl_t2 = bowl_t2.merge(bowl_matrix, on=['Pos_bowler'], how='left')

    bowl_t1['bowler_bb'] *= limit
    bowl_t2['bowler_bb'] *= limit
    bowl_t1['BPG'] = (bowl_t1['BPG'].sum()/bowl_t1['bowler_bb'].sum()) * bowl_t1['bowler_bb']
    bowl_t2['BPG'] = (bowl_t2['BPG'].sum()/bowl_t2['bowler_bb'].sum()) * bowl_t2['bowler_bb']
    #bowl_t1['BPG'] = bowl_t1['bowler_bb'] * limit
    #bowl_t2['BPG'] = bowl_t2['bowler_bb'] * limit
    
    bat_t1['venue'] = venue
    bat_t2['venue'] = venue

    venue_d = venue_matrix[venue_matrix['venue']==venue]
    venue_d.columns = ['venue', 'type', 'bias', 'v_r0s', 'v_r1s', 'v_r2s', 'v_r4s', 'v_r6s', 'v_rextras', 'v_rwkts']
    venue_bat = venue_d.pivot_table(values=['v_r0s', 'v_r1s', 'v_r2s', 'v_r4s', 'v_r6s', 'v_rwkts'], index=['venue'], 
                              aggfunc=lambda rows: np.average(rows, weights=venue_d.loc[rows.index, 'bias']))
    venue_bat = venue_bat.reset_index()

    venue_d.loc[venue_d['type']=='pace','bias'] /= pace_avg
    venue_d.loc[venue_d['type']=='spin','bias'] /= spin_avg
    bowl_t1 = bowl_t1.merge(venue_d, on=['type'], how='left')
    bowl_t2 = bowl_t2.merge(venue_d, on=['type'], how='left')
    bat_t1 = bat_t1.merge(venue_bat, on=['venue'], how='left')
    bat_t2 = bat_t2.merge(venue_bat, on=['venue'], how='left')

    bowl_t1 = venues_adj(bowl_t1, 0)
    bowl_t2 = venues_adj(bowl_t2, 0)
    bat_t1 = venues_adj(bat_t1, 1)
    bat_t2 = venues_adj(bat_t2, 1)

    #balancing
    bat_t1_bowl_t2 = np.sqrt((bat_t1['BPD']*bat_t1['BPD_ratio']).sum()*bowl_t2['BPG'].sum())
    bat_t2_bowl_t1 = np.sqrt((bat_t2['BPD']*bat_t2['BPD_ratio']).sum()*bowl_t1['BPG'].sum())
    
    bowl_t1['BPG'] *= bat_t2_bowl_t1/bowl_t1['BPG'].sum()
    bowl_t2['BPG'] *= bat_t1_bowl_t2/bowl_t2['BPG'].sum()
    bat_t2['BPD_ratio'] *= bat_t2_bowl_t1/(bat_t2['BPD']*bat_t2['BPD_ratio']).sum()
    bat_t1['BPD_ratio'] *= bat_t1_bowl_t2/(bat_t1['BPD']*bat_t1['BPD_ratio']).sum()
    #print(bowl_t1['BPG'].sum())
    #print(bowl_t2['BPG'].sum())
    #print((bat_t1['BPD']*bat_t1['BPD_ratio']).sum())
    #print((bat_t2['BPD']*bat_t2['BPD_ratio']).sum())

    bat_t1, bowl_t2 = balance(lg,bat_t1,bowl_t2)
    bat_t2, bowl_t1 = balance(lg,bat_t2,bowl_t1)

    bat_t1 = match_calculations(lg,bat_t1,1)
    bat_t2 = match_calculations(lg,bat_t2,1)
    bowl_t1 = match_calculations(lg,bowl_t1,0)
    bowl_t2 = match_calculations(lg,bowl_t2,0)
    """
    print(bat_t1['balls'].sum(),bowl_t2['balls'].sum())
    print(bat_t2['balls'].sum(),bowl_t1['balls'].sum())
    print()
    print(bat_t1['dismissals'].sum(),bowl_t2['wickets'].sum())
    print(bat_t2['dismissals'].sum(),bowl_t1['wickets'].sum())
    print()
    print(bat_t1['runs'].sum(),bowl_t2['runs'].sum())
    print(bat_t2['runs'].sum(),bowl_t1['runs'].sum())
    """
    bat_t1, bowl_t2 = rebalance(bat_t1,bowl_t2)
    bat_t2, bowl_t1 = rebalance(bat_t2,bowl_t1)
    
    bat = pd.concat([bat_t1, bat_t2])
    bowl = pd.concat([bowl_t1, bowl_t2])
    
    bat = bat.dropna(subset=['0s'], how='any')
    #bat['AVG'] = bat['runs']/bat['dismissals']
    #bat['SR'] = 100*bat['runs']/bat['balls']
    bowl = bowl.dropna(subset=['0s'], how='any')
    #bowl['ECON'] = 6*bowl['runs']/bowl['balls']
    #bowl['SR'] = bowl['balls']/bowl['wickets']
    
    bat = bat.sort_values(by=['team','Pos'], ascending=[True,True])
    bowl = bowl.sort_values(by=['team','balls'], ascending=[True,False])
    
    if(lg in test_leagues()): draw = 1/(1+pow(80*(bat['dismissals'].sum()/bat['balls'].sum()),8.5))  #draw formula for tests
    else: draw = 0
    
    win_t1 = (1-draw)/(1+pow(bowl_t1['runs'].sum()/bowl_t2['runs'].sum(),5.5))
    win_t2 = (1-draw)/(1+pow(bowl_t2['runs'].sum()/bowl_t1['runs'].sum(),5.5))
    
    print()
    print(t1,"vs",t2)
    print('Competition -',lg)
    print("Venue -",venue)
    print()
    print(t1,round(bowl_t2['runs'].sum(),1),"/",round(bat_t1['dismissals'].sum(),1),"in",round(bat_t1['balls'].sum(),1),"balls")
    print(t2,round(bowl_t1['runs'].sum(),1),"/",round(bat_t2['dismissals'].sum(),1),"in",round(bat_t2['balls'].sum(),1),"balls")
    print()
    print(t1,round(100*win_t1,2))
    if(lg in test_leagues()): print("Draw",round(100*draw,2))
    print(t2,round(100*win_t2,2))
    return bat,bowl

#%% concat raw data files
concat_game_files('mlc')

#%% analysis
batter, factors, bowler, factors_bowler = extract_all_league_stats(leagues_considered(league))

aging_factors = aging_analysis(batter,1)
aging_factors_bowler = aging_analysis(bowler,0)
aging = [aging_factors_bowler,aging_factors]
del aging_factors, aging_factors_bowler

batter,scale = apply_factors(batter.copy(), factors, league, leagues_considered(league), 1)
scale = league_scaling(scale.copy(),league,1)
batter = stats_concat(batter.copy(),scale.copy(),1)

bowler,scale_bowler = apply_factors(bowler.copy(), factors_bowler, league, leagues_considered(league), 0)
scale_bowler = league_scaling(scale_bowler.copy(),league,0)
bowler = stats_concat(bowler.copy(),scale_bowler.copy(),0)

league_conversions = [factors_bowler, factors]
league_scaling = [scale_bowler, scale]
del scale, scale_bowler, factors_bowler, factors

#%% remove everyone who hasnt played in 4 years (to speed up sims)
batters_alive = batter.groupby('striker')['start_date'].max()
batters_alive = batters_alive.reset_index()
batters_alive.columns = ['player','latest_game']
batters_alive = batters_alive[batters_alive['latest_game'] > datetime(datetime.now().year-4, 1, 1, 0, 0, 0)]

bowlers_alive = bowler.groupby('bowler')['start_date'].max()
bowlers_alive = bowlers_alive.reset_index()
bowlers_alive.columns = ['player','latest_game']
bowlers_alive = bowlers_alive[bowlers_alive['latest_game'] > datetime(datetime.now().year-4, 1, 1, 0, 0, 0)]

active_list = batters_alive['player'].to_list() + bowlers_alive['player'].to_list()
active_list = list(set(active_list))

batter = batter[batter['striker'].isin(active_list)]
bowler = bowler[bowler['bowler'].isin(active_list)]

del batters_alive, bowlers_alive, active_list

#%% get projections
#kalman_stats_batting(batter,'SP Narine',1)
batter_projections = kalman_summary(batter.copy(), 1)
#kalman_stats_bowling(bowler,'SP Narine',1)
bowler_projections = kalman_summary(bowler.copy(), 0)

#%% aging applied
batter_projections = apply_aging_factors(batter_projections.copy(),aging[1],batter,1)
bowler_projections = apply_aging_factors(bowler_projections.copy(),aging[0],bowler,0)

adj_bowling_usage = bowling_usage(league,batter,bowler)
bowler_projections = bowler_projections.merge(adj_bowling_usage, left_on='player', right_on='bowler', how='left')
bowler_projections = bowler_projections[['player','type','age','Pos_bowler','bowler_bb','rSR','r0s','r1s','r2s','r4s','r6s','rextras']]

del batter, bowler, adj_bowling_usage

#%% game level matrix
bat_matrix, bowl_matrix, venue_matrix = game_matrix(league)

#%% get team and bio info for players
squads = squad_info()
#lineups = active_lineups('t20i')

#%% game sims
#batters,bowlers = game_sim(league,'Australia','Pakistan','Lahore')
#batters,bowlers = game_sim(league,'South Africa','West Indies','Wanderers')
#batters,bowlers = game_sim(league,'Sri Lanka','England','Pallekele')
batters,bowlers = game_sim(league,'India','New Zealand','Greenfield')