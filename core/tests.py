# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 17:42:10 2026
monte carlo cricket projections
@author: Subramanya.Ganti
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
import random
from datetime import datetime

np.seterr(divide='ignore')
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

league = 'ipl'
path = 'C:/Users/Subramanya.Ganti/Downloads/Sports/cricket'

#%% read files and basic pre processing
def test_leagues(): l = ['tests','cc','shield','pks']; return l
def odi_leagues(): l = ['odi','odib','rlc','odc']; return l
def t20_leagues(): l = ['t20i','t20ib','ipl','psl','cpl','mlc','sa20','blast','bbl','lpl','ilt','smash','bpl','smat','msl','npl']; return l
def short_leagues(): l = ['hundred']; return l

def player_name_changes():
    name_changes = [['NR Sciver','NR Sciver-Brunt'],['KH Brunt','KH Sciver-Brunt'],['L Winfield','L Winfield-Hill'],
                ['NA Saini','Navdeep Saini'],['Josh Brown','J Brown'],['Mohammad Nawaz (3)','Mohammad Nawaz'],
                ['Arshad Khan (2)','Arshad Khan'],['Mohsin Khan (2)','Mohsin Khan'],['Steven Ryan Taylor','SR Taylor'],
                ['Aaron Beard','AP Beard'],['A Aitken','A Aitken-Drummond'],['Duan Jansen','D Jansen'],['S Rana','Sneh Rana']]
    name_changes = pd.DataFrame(name_changes, columns=['old', 'new'])
    mapping_series = name_changes.set_index('old')['new']
    return mapping_series
    
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
    if(comp == 'odib'):
        path_files = f"{path}/raw/odi"
    elif(comp == 't20ib'):
        path_files = f"{path}/raw/t20i"
    elif(comp == 't20iwb'):
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
    
    if(comp == 'odi' or comp == 't20i' or comp == 'tests'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Afghanistan"]
    elif(comp == 'odib'):
        countries = ["Zimbabwe","Netherlands","Nepal","United States of America","Ireland","Scotland","Oman","United Arab Emirates",'Namibia','Canada']
    elif(comp == 't20iw'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","Bangladesh","West Indies","Pakistan"]
    elif(comp == 't20iwb'):
        countries = ["Ireland","Scotland","Thailand","Zimbabwe","Papua New Guinea","Netherlands","Namibia","United Arab Emirates","Uganda",
                     "Tanzania","Indonesia","Nepal"]
    elif(comp == 'odiw'):
        countries = ["Australia","England","New Zealand","India","South Africa","Sri Lanka","West Indies","Pakistan","Bangladesh","Thailand","Ireland"]
    elif(comp == 't20ib'):
        countries = ["Ireland","Zimbabwe","Scotland","Netherlands","Namibia","United Arab Emirates","Nepal","Oman","Canada","United States of America",
                     'Italy',"Uganda","Jersey","Kenya","Bahrain","Papua New Guinea"]
    #elif(comp == 't20ic'):
    #    countries = ["Jersey","Germany","Denmark","Austria","Nigeria","Rwanda","Tanzania","Kenya","Bahrain","Hong Kong","Kuwait",
    #                 "Malaysia","Singapore","Japan","Papua New Guinea","Philippines"]
    elif(comp == 'smat'):
        countries = ['Meghalaya','Mizoram','Sikkim','Arunachal Pradesh','Manipur','Nagaland','Pondicherry']
    else:
        league = 1

    for file in file_list:
        if(file[-8:] != "info.csv"):
            df = pd.read_csv(file)
            date = datetime.strptime(df['start_date'][0], '%Y-%m-%d')
            
            if(league == 0 and comp == 'tests'):check = df['batting_team'][0] in countries and df['bowling_team'][0] in countries
            if(league == 0 and (comp == 't20i' or comp == 'odi')):
                check = df['batting_team'][0] in countries or df['bowling_team'][0] in countries
            if(league == 0 and (comp == 't20ib' or comp == 'odib')):
                check = df['batting_team'][0] in countries and df['bowling_team'][0] in countries
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
       
    try:
        existing = pd.read_excel(f'{path}/excel/projections.xlsx','squads')
        agg = agg.merge(existing[['player','team']], on='player', how='left')
    except ValueError:
        agg['team'] = np.nan
        
    agg = agg[['player','team','tests','odi','t20i','odib','t20ib','ipl','psl','cpl','mlc','sa20','blast','bbl','lpl',
               'ilt','smash','bpl','smat','npl','hundred','cc','shield','pks','rlc','odc']]
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
    
    pivot = sample.pivot_table(index=['match_id'],values=['bowler_bb','batter_bf','runs_off_bat','0s','1s','2s','4s','6s',
                                                          'extras','wicket_bowler','wicket_striker','wicket_non_striker'],aggfunc='sum')
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
    
    sample = sample.merge(pivot[['match_id','bat_runs_ball','bat_wkt_ball','bowl_runs_ball','bowl_wkt_ball','0s_ball','1s_ball',
                                 '2s_ball','4s_ball','6s_ball','extras_ball']], on=['match_id'])
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

def league_conversion_factors(df, leagues, bat_bowl, btype):
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
            
            #pace or spin
            from_df = from_df[from_df['type']==btype]
            to_df = to_df[to_df['type']==btype]
            
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

def extract_all_league_stats(leagues):
    df_game_stats = []; df_conversion = []
    df_game_stats_bowl = []; df_conversion_bowl = []
    player_age = pd.read_excel(f'{path}/excel/people.xlsx','people')
    player_age = player_age[['unique_name', 'dob', 'batType', 'bowlType']]
    player_age['type'] = np.where(player_age['bowlType'].isin(['Right-arm offbreak','Legbreak googly','Legbreak','Slow left-arm orthodox',
                                                                        'Left-arm wrist-spin','Right-arm offbreak (underarm)']), 'spin', 'pace')
    
    leagues = leagues_considered('ipl')
    for l in leagues:
        sample = league_data(l)
        sample = sample.merge(player_age[['unique_name', 'type']], left_on='bowler', right_on='unique_name', how='left')
        
        batter = sample.pivot_table(index=['striker','batting_team','start_date','type'],values=['batter_bf','runs_off_bat','wicket_bowler','wicket_striker',
                                                                                          'wicket_non_striker','bat_runs_ball','bat_wkt_ball',
                                                                                          '0s','1s','2s','4s','6s','0s_ball','1s_ball','2s_ball',
                                                                                          '4s_ball','6s_ball'],aggfunc='sum')
        batter = batter.reset_index()
        batterp = sample.pivot_table(index=['striker','batting_team','start_date'],values=['Pos'],aggfunc='mean')
        batterp = batterp.reset_index()
        batter = batter.merge(batterp, on=['striker','batting_team','start_date'], how='left')
        
        batter2 = sample.pivot_table(index=['non_striker','batting_team','start_date'],values=['wicket_non_striker'],aggfunc='sum')
        batter2 = batter2.reset_index()
        batter2.columns = ['striker','batting_team','start_date','wicket_non_striker']
        
        batter = batter.merge(batter2, on=['striker','batting_team','start_date'], how='left')
        batter = batter.merge(player_age[['unique_name', 'dob']], left_on=['striker'], right_on=['unique_name'], how='left')
        batter['wicket_non_striker_y'] = batter['wicket_non_striker_y'].fillna(0)
        batter['dismissals'] = batter['wicket_striker']+batter['wicket_non_striker_y']
        batter['start_date'] = pd.to_datetime(batter['start_date'], format='%Y-%m-%d')
        
        batter['delta'] = datetime.now() - batter['start_date']
        batter['delta'] = batter['delta'].dt.total_seconds()/(60*60*24)
        batter['delta'] = pow(.999,batter['delta'])
        
        batter['season'] = batter['start_date'].dt.year
        batter['dob'] = pd.to_datetime(batter['dob'],errors='coerce')
        batter['age'] = (batter['start_date'] - batter['dob']) / (pd.Timedelta(days=1)*365.25)
        df_game_stats.append(batter)
        
        batter_season = batter.pivot_table(index=['striker','season','type'],values=['bat_runs_ball','bat_wkt_ball','batter_bf','runs_off_bat','dismissals','0s',
                                                                              '1s','2s','4s','6s','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball'],aggfunc='sum')
        batter_season = batter_season.reset_index()
        batter_season2 = batter.pivot_table(index=['striker','season','type'],values=['age'],aggfunc='mean')
        batter_season2 = batter_season2.reset_index()
        batter_season['rRuns'] = batter_season['runs_off_bat'] / batter_season['bat_runs_ball']
        batter_season['r0s'] = batter_season['0s'] / batter_season['0s_ball']
        batter_season['r1s'] = batter_season['1s'] / batter_season['1s_ball']
        batter_season['r2s'] = batter_season['2s'] / batter_season['2s_ball']
        batter_season['r4s'] = batter_season['4s'] / batter_season['4s_ball']
        batter_season['r6s'] = batter_season['6s'] / batter_season['6s_ball']
        batter_season['rWkts'] = batter_season['dismissals'] / batter_season['bat_wkt_ball']
        batter_season = batter_season.merge(batter_season2, on=['striker','season','type'], how='left')
        df_conversion.append(batter_season)
        
        bowler = sample.pivot_table(index=['bowler','bowling_team','start_date','type'],values=['bowler_bb','runs_off_bat','wicket_bowler','bowl_runs_ball',
                                                                                         'bowl_wkt_ball','0s','1s','2s','4s','6s','0s_ball','1s_ball',
                                                                                         '2s_ball','4s_ball','6s_ball','extras','extras_ball'],aggfunc='sum')
        bowler = bowler.reset_index()
        #bowler['Pos_bowler'] /= bowler['bowler_bb']
        bowlerp = sample.pivot_table(index=['bowler','bowling_team','start_date'],values=['Pos_bowler'],aggfunc='mean')
        bowler = bowler.merge(bowlerp, on=['bowler','bowling_team','start_date'], how='left')
        
        bowler = bowler.merge(player_age[['unique_name', 'dob']], left_on=['bowler'], right_on=['unique_name'], how='left')
        bowler['dismissals'] = bowler['wicket_bowler']
        bowler['start_date'] = pd.to_datetime(bowler['start_date'], format='%Y-%m-%d')
        
        bowler['delta'] = datetime.now() - bowler['start_date']
        bowler['delta'] = bowler['delta'].dt.total_seconds()/(60*60*24)
        bowler['delta'] = pow(.999,bowler['delta'])
        
        bowler['season'] = bowler['start_date'].dt.year
        bowler['dob'] = pd.to_datetime(bowler['dob'],errors='coerce')
        bowler['age'] = (bowler['start_date'] - bowler['dob']) / (pd.Timedelta(days=1)*365.25)
        df_game_stats_bowl.append(bowler)
        
        bowler_season = bowler.pivot_table(index=['bowler','season','type'],values=['bowl_runs_ball','bowl_wkt_ball','bowler_bb','runs_off_bat','dismissals','0s',
                                                                             '1s','2s','4s','6s','0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras','extras_ball'],aggfunc='sum')
        bowler_season = bowler_season.reset_index()
        bowler_season2 = bowler.pivot_table(index=['bowler','season','type'],values=['age'],aggfunc='mean')
        bowler_season2 = bowler_season2.reset_index()
        bowler_season['rRuns'] = (bowler_season['runs_off_bat']+bowler_season['extras']) / bowler_season['bowl_runs_ball']
        bowler_season['r0s'] = bowler_season['0s'] / bowler_season['0s_ball']
        bowler_season['r1s'] = bowler_season['1s'] / bowler_season['1s_ball']
        bowler_season['r2s'] = bowler_season['2s'] / bowler_season['2s_ball']
        bowler_season['r4s'] = bowler_season['4s'] / bowler_season['4s_ball']
        bowler_season['r6s'] = bowler_season['6s'] / bowler_season['6s_ball']
        bowler_season['rextras'] = bowler_season['extras'] / bowler_season['extras_ball']
        bowler_season['rWkts'] = bowler_season['dismissals'] / bowler_season['bowl_wkt_ball']
        bowler_season = bowler_season.merge(bowler_season2, on=['bowler','season','type'], how='left')
        df_conversion_bowl.append(bowler_season)
        
    conversions_pace = league_conversion_factors(df_conversion, leagues, 1, 'pace')
    conversions_spin = league_conversion_factors(df_conversion, leagues, 1, 'spin')
    conversions_pace_bowl = league_conversion_factors(df_conversion_bowl, leagues, 0, 'pace')
    conversions_spin_bowl = league_conversion_factors(df_conversion_bowl, leagues, 0, 'spin')
    return df_game_stats, conversions_pace, conversions_spin, df_game_stats_bowl, conversions_pace_bowl, conversions_spin_bowl

def aging_analysis(df, bat_bowl):
    if(bat_bowl == 0): key = 'bowler'; bx = 'bowler_bb_x'; by = 'bowler_bb_y'
    else: key = 'striker'; bx = 'batter_bf_x'; by = 'batter_bf_y'
    
    df = pd.concat(df)
    df['age'] = (pd.to_datetime(df['season'], format='%Y')-df['dob']) / (pd.Timedelta(days=1)*365.25)
    df['age'] = df['age'].apply(np.floor)
    df = df[df['age']<=45]
    df = df[df['age']>=14]
    df['age'] = df['age'].astype(int)
    
    if(bat_bowl == 0): 
        df_agg = df.pivot_table(index=[key,'age'],values=['bowler_bb','0s','1s','2s','4s','6s','extras','dismissals','0s_ball',
                                                          '1s_ball','2s_ball','4s_ball','6s_ball','extras_ball','bowl_wkt_ball'],aggfunc='sum')
    else: 
        df_agg = df.pivot_table(index=[key,'age'],values=['batter_bf','0s','1s','2s','4s','6s','dismissals','0s_ball','1s_ball',
                                                          '2s_ball','4s_ball','6s_ball','bat_wkt_ball'],aggfunc='sum')
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

def apply_factors(df_list, df_factors_pace, df_factors_spin, target, league_list, bat_bowl):
    c=0; df_list_modified = [];
    if(bat_bowl == 0): df_scale = [['league','scaled_balls','scaled_runs','scaled_dismissals', 'scaled_0s','scaled_1s','scaled_2s','scaled_4s','scaled_6s','scaled_extras','matches']]
    else: df_scale = [['league','scaled_balls','scaled_runs','scaled_dismissals', 'scaled_0s','scaled_1s','scaled_2s','scaled_4s','scaled_6s','matches']]

    for l in league_list:
        df = df_list[c]
        df['runs_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[0], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[0])
        df['wickets_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[1], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[1])
        df['0s_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[2], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[2])
        df['1s_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[3], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[3])
        df['2s_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[4], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[4])
        df['4s_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[5], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[5])
        df['6s_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[6], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[6])
        if(bat_bowl == 0): df['extras_factor'] = np.where(df['type']=='pace', np.exp(df_factors_pace.loc[l] - df_factors_pace.loc[target]).values[7], np.exp(df_factors_spin.loc[l] - df_factors_spin.loc[target]).values[7])
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

def bat_bowl_usage_matrix(lg):
    if(lg in test_leagues()): l = 'tests'
    elif(lg in short_leagues()): l = 'hundred'
    elif(lg in odi_leagues()): l = 'odi'
    else: l = 't20i'
    
    sample = league_data(l)
    sample['start_date'] = pd.to_datetime(sample['start_date'], format='%Y-%m-%d')
    """
    bowl_pivot = sample.pivot_table(index=['bowler','start_date'],columns='over',values='ball',aggfunc='count')
    bowl_pivot = bowl_pivot.reset_index()
    bowl_pivot['weight'] = datetime.now() - bowl_pivot['start_date']
    bowl_pivot['weight'] = bowl_pivot['weight'].dt.total_seconds()/(60*60*24)
    bowl_pivot['weight'] = pow(.999,bowl_pivot['weight'])
    bowl_pivot = bowl_pivot.fillna(0)
    bowl_pivot = bowl_pivot.pivot_table(index='bowler', values=range(1,21), aggfunc= lambda rows: np.average(rows, weights = bowl_pivot.loc[rows.index, 'weight']))
    bowl_pivot = bowl_pivot.div(bowl_pivot.sum(axis=1), axis=0)
    bowl_pivot = bowl_pivot.fillna(1/20)
    """
    sequences = sample[['match_id','innings','over','Pos_bowler']].drop_duplicates()
    sequences = sequences['Pos_bowler'].to_list()
    matrix = pd.crosstab(
        pd.Series(sequences[:-1], name='From'), 
        pd.Series(sequences[1:], name='To'), 
        normalize='index'  # Ensures rows sum to 1.0
    )
    matrix += 0.01 #verify this
    np.fill_diagonal(matrix.values, 0)
    matrix = matrix.div(matrix.sum(axis=1), axis=0)
    """
    bat_pivot = sample.pivot_table(index=['striker','start_date'],columns='Pos',values='ball',aggfunc='count')
    bat_pivot = bat_pivot.reset_index()
    bat_pivot['weight'] = datetime.now() - bat_pivot['start_date']
    bat_pivot['weight'] = bat_pivot['weight'].dt.total_seconds()/(60*60*24)
    bat_pivot['weight'] = pow(.999,bat_pivot['weight'])
    bat_pivot = bat_pivot.fillna(0)
    bat_pivot = bat_pivot.pivot_table(index='striker', values=range(1,12), aggfunc= lambda rows: np.average(rows, weights = bat_pivot.loc[rows.index, 'weight']))
    bat_pivot += 0.1 #check this
    bat_pivot = bat_pivot.div(bat_pivot.sum(axis=1), axis=0)
    bat_pivot = bat_pivot.fillna(1/11)
    """
    return matrix

def mc_steady_state(P):
    eigenvalues, eigenvectors = np.linalg.eig(P.T)
    
    idx = np.argmin(np.abs(eigenvalues - 1))
    steady_state = np.real(eigenvectors[:, idx])
    
    steady_state = steady_state / steady_state.sum()
    #print(steady_state)
    return steady_state

def apply_aging_factors(df,af,df_full,bat_bowl):
    if(bat_bowl == 0): key = 'player'
    else: key = 'player'
        
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
        df = df[['player','type','age','Pos_bowler','Pos_bowler_std','rSR','r0s', 'r1s', 'r2s', 'r4s', 'r6s', 'rextras']]
    else:
        df['rBPD'] /= df['rWkts_aging']
        df = df[['player','type','age','Pos','Pos_std','rBPD','r0s', 'r1s', 'r2s', 'r4s', 'r6s']]
    return df

def player_projections(df,bat_bowl,full_player_list):    
    if(bat_bowl == 1):
        columns = ['0s', '0s_ball', '1s', '1s_ball', '2s', '2s_ball', '4s', '4s_ball', '6s', '6s_ball', 
                   'bat_runs_ball', 'bat_wkt_ball', 'batter_bf', 'runs_off_bat', 'wicket_striker','wicket_non_striker_y']
        df.rename(columns={'striker': 'player'}, inplace=True)
    else:
        columns = ['0s', '0s_ball', '1s', '1s_ball', '2s', '2s_ball', '4s', '4s_ball', '6s', '6s_ball', 'extras', 'extras_ball',
                   'bowl_runs_ball', 'bowl_wkt_ball', 'bowler_bb', 'runs_off_bat', 'wicket_bowler']
        df.rename(columns={'bowler': 'player'}, inplace=True)
        
    df_projection = df.copy()
    for c in columns:
        df_projection[c] *= df_projection['delta']
        
    df_projection = df_projection.pivot_table(index=['player','type'],values=columns,aggfunc="sum")
    df_replacement = df_projection.sum()
    
    if(bat_bowl == 1): df_replacement *= 100/df_replacement['batter_bf'].sum()
    else: df_replacement *= 100/df_replacement['bowler_bb'].sum()
    
    df_projection += df_replacement
    if(bat_bowl == 1): df_projection['RAA/ball'] = (df_projection['runs_off_bat']-df_projection['bat_runs_ball'])/df_projection['batter_bf']
    else: df_projection['RAA/ball'] = (df_projection['runs_off_bat']+df_projection['extras']-df_projection['bowl_runs_ball'])/df_projection['bowler_bb']

    df_projection['r0s'] = df_projection['0s']/df_projection['0s_ball']
    df_projection['r1s'] = df_projection['1s']/df_projection['1s_ball']
    df_projection['r2s'] = df_projection['2s']/df_projection['2s_ball']
    df_projection['r4s'] = df_projection['4s']/df_projection['4s_ball']
    df_projection['r6s'] = df_projection['6s']/df_projection['6s_ball']
    if(bat_bowl == 1): 
        df_projection['rBPD'] = df_projection['bat_wkt_ball']/(df_projection['wicket_striker']+df_projection['wicket_non_striker_y'])
    else:
        df_projection['rextras'] = df_projection['extras']/df_projection['extras_ball']
        df_projection['rSR'] = df_projection['bowl_wkt_ball']/df_projection['wicket_bowler']
        
    df_projection = df_projection.reset_index()
    df['age'] = df['age'].fillna(28)
    
    if(bat_bowl == 1): key = 'Pos'
    else: key = 'Pos_bowler'
    
    df_age = df[['player','age',key,'delta']].drop_duplicates()
    df_age['age_sum'] = df['age'] * df['delta']
    df_age['Pos_sum'] = df[key] * df['delta']
    df_agep = df_age.pivot_table(index=['player'],values=['age_sum','Pos_sum','delta'],aggfunc="sum")
    df_agep['w_age'] = df_agep['age_sum']/df_agep['delta']
    df_agep[key] = df_agep['Pos_sum']/df_agep['delta']
    df_agep = df_agep.reset_index()

    df_ages = df_age.pivot_table(index=['player'],values=[key],aggfunc="std")
    df_ages[f'{key}_std'] = df_ages[key]
    df_ages[f'{key}_std'] = df_ages[f'{key}_std'].fillna(0)
    df_ages[f'{key}_std'] += 0.25
    df_ages = df_ages.reset_index()

    df_projection = df_projection.merge(df_agep[['player','w_age',key]],on='player',how='left')
    df_projection = df_projection.merge(df_ages[['player',f'{key}_std']],on='player',how='left')
    
    if(bat_bowl == 1):
        df_projection_full = pd.DataFrame(columns = ['player','type'])
        df_projection_full['player'] = full_player_list*2
        df_projection_full['type'] = ['pace'] * len(full_player_list) + ['spin'] * len(full_player_list)
        df_projection_full = df_projection_full.merge(df_projection, on=['player','type'], how='left')
        
        df_projection_full[df_replacement.index] = df_projection_full[df_replacement.index].fillna(df_replacement)
        df_projection_full['r0s'] = df_projection_full['0s']/df_projection_full['0s_ball']
        df_projection_full['r1s'] = df_projection_full['1s']/df_projection_full['1s_ball']
        df_projection_full['r2s'] = df_projection_full['2s']/df_projection_full['2s_ball']
        df_projection_full['r4s'] = df_projection_full['4s']/df_projection_full['4s_ball']
        df_projection_full['r6s'] = df_projection_full['6s']/df_projection_full['6s_ball']
        df_projection_full['rBPD'] = df_projection_full['bat_wkt_ball']/(df_projection_full['wicket_striker']+df_projection_full['wicket_non_striker_y'])
        df_projection_full['Pos'] = df_projection_full['Pos'].fillna(11)
        df_projection_full['w_age'] = df_projection_full['w_age'].fillna(28)
        df_projection_full['Pos_std'] = df_projection_full['Pos_std'].fillna(0.25)
        
        pos_ex = df_projection_full.pivot_table(index='player',values='Pos',aggfunc='mean')
        pos_ex = pos_ex.reset_index()
        df_projection_full = df_projection_full.drop(columns=['Pos'])
        df_projection_full = df_projection_full.merge(pos_ex, on='player', how='left')
        
        df_projection = df_projection_full.copy()
        
    return df_projection

def bowling_usage(lg,df_bat,df_bowl):
    if(lg in test_leagues()): limit = 225*6
    elif(lg in short_leagues()): limit = 100
    elif(lg in odi_leagues()): limit = 300
    else: limit = 120
    
    bowler_usage = df_bowl[['player','bowling_team','start_date','bowler_bb','delta']].merge(df_bat[['player','batting_team','start_date','delta']], 
                                                                                    left_on=['player','bowling_team','start_date'], 
                                                                                    right_on=['player','batting_team','start_date'], how='outer')
    
    bowler_usage['player'] = bowler_usage['player'].fillna(bowler_usage['player'])
    bowler_usage['delta'] = bowler_usage['delta_x'].fillna(bowler_usage['delta_y'])
    bowler_usage['bowler_bb'] = bowler_usage['bowler_bb'].fillna(0)
    bowler_usage = bowler_usage[['player','start_date','bowler_bb','delta']]
    bowler_usage = bowler_usage.sort_values(by=['player','start_date'], ascending=[True,True])
    bowler_usage = bowler_usage.drop_duplicates()
    bowler_usage['bowler_bb'] = bowler_usage['bowler_bb'] * bowler_usage['delta']
    
    adj_usage = bowler_usage.pivot_table(index='player',values=['delta','bowler_bb'],aggfunc="sum")
    adj_usage['usage'] = adj_usage['bowler_bb']/adj_usage['delta']   
    adj_usage['usage'] /= limit
    if(limit != 225*6): adj_usage['usage'] = adj_usage['usage'].clip(upper=0.2)
    else: adj_usage['usage'] = adj_usage['usage'].clip(upper=1)
    adj_usage = adj_usage.reset_index()
    adj_usage = adj_usage[['player','usage']]
    
    return adj_usage

def venue_league_matrix(l):
    venues = pd.read_excel(f'{path}/excel/venues.xlsx','Sheet1')
    people = pd.read_excel(f'{path}/excel/people.xlsx','people')
    #people = people[['unique_name','bowlType']]
    
    if(l in ['tests']): target_list = test_leagues()
    else: target_list = odi_leagues() + short_leagues() + t20_leagues()
    
    league_stats_concat = []
    for l2 in target_list:
        sample = league_data(l2)
        league_stats_concat.append(sample)
        
    league_stats_concat = pd.concat(league_stats_concat)
    league_stats_concat['start_date'] = pd.to_datetime(league_stats_concat['start_date'], format='%Y-%m-%d')
    #league_stats_concat = league_stats_concat.sort_values(by=['start_date'], ascending=[True])
    league_stats_concat['weight'] = (datetime.now() - league_stats_concat['start_date']) / (pd.Timedelta(days=1))
    league_stats_concat['weight'] = pow(.9995,league_stats_concat['weight'])    
    league_stats_concat = league_stats_concat.merge(venues, on=['venue'], how='left')
    league_stats_concat = league_stats_concat.merge(people[['unique_name','bowlType']], left_on=['bowler'], right_on=['unique_name'], how='left')
    league_stats_concat['type'] = league_stats_concat['bowlType'].isin(['Right-arm offbreak','Legbreak googly','Legbreak','Slow left-arm orthodox',
                                                                        'Left-arm wrist-spin','Right-arm offbreak (underarm)'])
    league_stats_concat['type'] = league_stats_concat['type'].replace({True: 'spin', False: 'pace'})
    
    venue_stats = league_stats_concat.pivot_table(index=['start_date','match_id','short','type'], values=['batter_bf','bowler_bb','wicket_bowler',
                                                                                                   '0s','1s','2s','4s','6s','extras','bowl_wkt_ball',
                                                                                                   '0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras_ball'], aggfunc='sum')
    venue_stats = venue_stats.reset_index()
    
    venue_stats['r0s'] = (venue_stats['0s']/venue_stats['batter_bf']) / (venue_stats['0s'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r1s'] = (venue_stats['1s']/venue_stats['batter_bf']) / (venue_stats['1s'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r2s'] = (venue_stats['2s']/venue_stats['batter_bf']) / (venue_stats['2s'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r4s'] = (venue_stats['4s']/venue_stats['batter_bf']) / (venue_stats['4s'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['r6s'] = (venue_stats['6s']/venue_stats['batter_bf']) / (venue_stats['6s'].sum()/venue_stats['batter_bf'].sum())
    venue_stats['rextras'] = (venue_stats['extras']/venue_stats['bowler_bb']) / (venue_stats['extras'].sum()/venue_stats['bowler_bb'].sum())
    venue_stats['rwkts'] = (venue_stats['wicket_bowler']/venue_stats['bowler_bb']) / (venue_stats['wicket_bowler'].sum()/venue_stats['bowler_bb'].sum())
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
    
    regression_weight = venue_stats['bowler_bb'].mean()
    
    agg_venue_stats['r0s'] = (agg_venue_stats['r0s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r1s'] = (agg_venue_stats['r1s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r2s'] = (agg_venue_stats['r2s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r4s'] = (agg_venue_stats['r4s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['r6s'] = (agg_venue_stats['r6s']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['rextras'] = (agg_venue_stats['rextras']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats['rwkts'] = (agg_venue_stats['rwkts']*agg_venue_stats['bowler_bb'] + regression_weight)/(agg_venue_stats['bowler_bb'] + regression_weight)
    agg_venue_stats = agg_venue_stats.reset_index()
    agg_venue_stats = agg_venue_stats.merge(bias, on=['short'], how='left')
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
    return agg_venue_stats

def comp_matrix(league):
    sample = league_data(league)
    
    sample['start_date'] = pd.to_datetime(sample['start_date'], format='%Y-%m-%d')
    sample['delta'] = datetime.now() - sample['start_date']
    sample['delta'] = sample['delta'].dt.total_seconds()/(60*60*24)
    sample['delta'] = pow(.999,sample['delta'])
    
    columns = ['0s_ball','1s_ball','2s_ball','4s_ball','6s_ball','extras_ball','bowl_wkt_ball','bat_wkt_ball']
    for c in columns:
        sample[c] *= sample['delta']
    
    sample_pivot = sample.pivot_table(index='over',values=columns+['delta'], aggfunc='mean')
    for c in columns:
        sample_pivot[c] /= sample_pivot['delta']
    return sample_pivot

def randomize_pos(df,bat_bowl):
    if(bat_bowl == 1): key = 'Pos'; f=1
    else: key = 'Pos_bowler'; f=1
    
    df[key] += (2*np.random.rand(*df[key].shape)-1)*df[f'{key}_std']*f
    df = df.sort_values(by=key)
    df[key] = range(1, len(df) + 1)
    return df

def mc_game_engine(t1_name,t2_name,venue,t1_bat,t1_bowl,t2_bat,t2_bowl,full_bowl_matrix,print_val):
    #t1_name = 'SRH'
    #t2_name = 'RCB'
    #venue = 'Uppal'
    
    #t2 = ['JR Hazlewood', 'B Kumar', 'D Padikkal', 'Rasikh Salam', 'JM Sharma', 'KH Pandya', 'PD Salt', 'R Shepherd', 'RM Patidar', 'Suyash Sharma', 'TH David', 'V Kohli']
    #t1 = ['Abhishek Sharma', 'Aniket Verma', 'DA Payne', 'E Malinga', 'H Klaasen', 'HV Patel', 'Harsh Dubey', 'Ishan Kishan', 'JD Unadkat', 'Nithish Kumar Reddy', 'S Arora', 'TM Head']
    #t1_bat = batter_projection[batter_projection['player'].isin(t1)]
    #t2_bowl = bowler_projection[bowler_projection['player'].isin(t2)]
    #t2_bat = batter_projection[batter_projection['player'].isin(t2)]
    #t1_bowl = bowler_projection[bowler_projection['player'].isin(t1)]
    
    match_bat_outcome = []; match_bowl_outcome = []; match_ongoing = True; innings = 1; target = -1
    
    while(match_ongoing):
        
        innings_ongoing = True 
        if(innings == 1): 
            bat_outcome = t1_bat[['player','age','Pos','Pos_std']].drop_duplicates(); bat_ref = t1_bat.copy()
            bat_outcome['team'] = t1_name
            bat_team_name = t1_name
        else: 
            bat_outcome = t2_bat[['player','age','Pos','Pos_std']].drop_duplicates(); bat_ref = t2_bat.copy()
            bat_outcome['team'] = t2_name
            bat_team_name = t2_name
        
        bat_outcome = bat_outcome.drop_duplicates()
        bat_outcome = randomize_pos(bat_outcome.copy(),1)
        bat_outcome[['balls_faced','0s','1s','2s','4s','6s','dismissals','runs']] = 0
        
        if(innings == 1): 
            bowl_outcome = t2_bowl[['player','age','type','Pos_bowler','Pos_bowler_std','usage']].drop_duplicates(); bowl_ref = t2_bowl.copy()
            bowl_outcome['team'] = t2_name
        else: 
            bowl_outcome = t1_bowl[['player','age','type','Pos_bowler','Pos_bowler_std','usage']].drop_duplicates(); bowl_ref = t1_bowl.copy()
            bowl_outcome['team'] = t1_name
        
        bowl_outcome = bowl_outcome.drop_duplicates()
        bowl_outcome = randomize_pos(bowl_outcome.copy(),0)
        bowl_outcome[['balls_bowled','0s','1s','2s','4s','6s','extras','wickets','runs']] = 0
        
        striker = 1; non_striker = 2; bowler = 1; over = 1; ball = 1; wickets_innings = 0; newm = 1; score = 0
        
        bowl_matrix = full_bowl_matrix.copy()
        ss = mc_steady_state(bowl_matrix)
        ss_factor = bowl_outcome['usage'].to_list()[:len(ss)]/ss
        #print(ss_factor)
        for b in bowl_matrix.columns:
            try: bowl_matrix[b] *= ss_factor[b-1]
            except: bowl_matrix[b] *= 0
        bowl_matrix = bowl_matrix.div(bowl_matrix.sum(axis=1), axis=0)
        #print(bowl_matrix)
        
        while(innings_ongoing):
            flag = random.random()
            flag_extra = random.random()
            flag_wicket_other = random.random()
            
            if(newm != 0):
                striker_name = bat_outcome.loc[bat_outcome['Pos']==striker,'player'].values[0]
                bowler_name = bowl_outcome.loc[bowl_outcome['Pos_bowler']==bowler,'player'].values[0]
                b_type = bowl_outcome.loc[bowl_outcome['Pos_bowler']==bowler,'type'].values[0]
                        
                p_ball_0 = league_matrix.loc[over]['0s_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['r0s'].values[0] * bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['r0s'].values[0] * bowl_ref.loc[bowl_ref['player']==bowler_name]['r0s'].values[0]
                p_ball_1 = league_matrix.loc[over]['1s_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['r1s'].values[0] * bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['r1s'].values[0] * bowl_ref.loc[bowl_ref['player']==bowler_name]['r1s'].values[0]
                p_ball_2 = league_matrix.loc[over]['2s_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['r2s'].values[0] * bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['r2s'].values[0] * bowl_ref.loc[bowl_ref['player']==bowler_name]['r2s'].values[0]
                p_ball_4 = league_matrix.loc[over]['4s_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['r4s'].values[0] * bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['r4s'].values[0] * bowl_ref.loc[bowl_ref['player']==bowler_name]['r4s'].values[0]
                p_ball_6 = league_matrix.loc[over]['6s_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['r6s'].values[0] * bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['r6s'].values[0] * bowl_ref.loc[bowl_ref['player']==bowler_name]['r6s'].values[0]
                p_ball_extra = league_matrix.loc[over]['extras_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['rextras'].values[0] * bowl_ref.loc[bowl_ref['player']==bowler_name]['rextras'].values[0]
                p_ball_wicket_bowler = league_matrix.loc[over]['bowl_wkt_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['rwkts'].values[0] * (1/bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['rBPD'].values[0]) * (1/bowl_ref.loc[bowl_ref['player']==bowler_name]['rSR'].values[0])
                p_ball_wicket_batsman = league_matrix.loc[over]['bat_wkt_ball'] * venue_matrix[(venue_matrix['venue']==venue)&(venue_matrix['type']==b_type)]['rwkts'].values[0] * (1/bat_ref.loc[(bat_ref['player']==striker_name)*(bat_ref['type']==b_type)]['rBPD'].values[0]) * (1/bowl_ref.loc[bowl_ref['player']==bowler_name]['rSR'].values[0])
                
                p_sum = p_ball_0 + p_ball_1 + p_ball_2 + p_ball_4 + p_ball_6 + p_ball_wicket_bowler
                p_ball_0 /= p_sum
                p_ball_1 /= p_sum
                p_ball_2 /= p_sum
                p_ball_4 /= p_sum
                p_ball_6 /= p_sum
                p_ball_extra /= p_sum
                p_ball_wicket_bowler /= p_sum
                p_ball_wicket_batsman /= p_sum
                p_ball_wicket_other = p_ball_wicket_batsman - p_ball_wicket_bowler
            
            if(flag_extra <= p_ball_extra):
                score += 1
                newm = 0
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'extras'] += 1 
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"extra")
                if(flag_wicket_other <= p_ball_wicket_other):
                    newm = 1
                    #assuming its the striker whos out here
                    if(print_val == 1):print(over,ball,bowler_name,striker_name,"non-bowler wicket")
                    bat_outcome.loc[bat_outcome['player']==striker_name,'dismissals'] += 1
                    striker = max(striker,non_striker) + 1
                    wickets_innings += 1
            elif(flag <= p_ball_0): 
                newm = 0
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"dot")
                bat_outcome.loc[bat_outcome['player']==striker_name,'0s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'0s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'balls_bowled'] += 1
                ball += 1
                if(flag_wicket_other <= p_ball_wicket_other): 
                    newm = 1
                    #assuming its the striker whos out here
                    if(print_val == 1):print(over,ball,bowler_name,striker_name,"non-bowler wicket")
                    bat_outcome.loc[bat_outcome['player']==striker_name,'dismissals'] += 1
                    striker = max(striker,non_striker) + 1
                    wickets_innings += 1
            elif(flag > p_ball_0 and flag <= (p_ball_0 + p_ball_1)):
                score += 1
                newm = 1
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"single")
                bat_outcome.loc[bat_outcome['player']==striker_name,'1s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'1s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'balls_bowled'] += 1
                ball += 1
                if(flag_wicket_other <= p_ball_wicket_other):
                    newm = 1
                    #assuming its the striker whos out here
                    if(print_val == 1):print(over,ball,bowler_name,striker_name,"non-bowler wicket")
                    bat_outcome.loc[bat_outcome['player']==striker_name,'dismissals'] += 1
                    striker = max(striker,non_striker) + 1
                    wickets_innings += 1
                copy = non_striker
                non_striker = striker
                striker = copy
            elif(flag > (p_ball_0 + p_ball_1) and flag <= (p_ball_0 + p_ball_1 + p_ball_2)):
                score += 2
                newm = 0
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"two")
                bat_outcome.loc[bat_outcome['player']==striker_name,'2s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'2s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'balls_bowled'] += 1
                ball += 1
                if(flag_wicket_other <= p_ball_wicket_other):
                    newm = 1
                    #assuming its the striker whos out here
                    if(print_val == 1):print(over,ball,bowler_name,striker_name,"non-bowler wicket")
                    bat_outcome.loc[bat_outcome['player']==striker_name,'dismissals'] += 1
                    striker = max(striker,non_striker) + 1
                    wickets_innings += 1
            elif(flag > (p_ball_0 + p_ball_1 + p_ball_2) and flag <= (p_ball_0 + p_ball_1 + p_ball_2 + p_ball_4)):
                score += 4
                newm = 0
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"four")
                bat_outcome.loc[bat_outcome['player']==striker_name,'4s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'4s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'balls_bowled'] += 1
                ball += 1
            elif(flag > (p_ball_0 + p_ball_1 + p_ball_2 + p_ball_4) and flag <= (p_ball_0 + p_ball_1 + p_ball_2 + p_ball_4 + p_ball_6)):
                score += 6
                newm = 0
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"six")
                bat_outcome.loc[bat_outcome['player']==striker_name,'6s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'6s'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'balls_bowled'] += 1
                ball += 1
            elif(flag > (p_ball_0 + p_ball_1 + p_ball_2 + p_ball_4 + p_ball_6)):
                newm = 1
                if(print_val == 1):print(over,ball,bowler_name,striker_name,"wicket")
                bat_outcome.loc[bat_outcome['player']==striker_name,'dismissals'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'wickets'] += 1
                bowl_outcome.loc[bowl_outcome['player']==bowler_name,'balls_bowled'] += 1
                ball += 1
                striker = max(striker,non_striker) + 1
                wickets_innings += 1
                
            if(ball > 6): 
                ball = 1; over += 1; newm = 1
                bowler_bb = bowl_outcome.loc[bowl_outcome['Pos_bowler']==bowler,'balls_bowled'].sum()
                if(bowler_bb >= 24): 
                    bowl_matrix[bowler] = 0
                    bowl_matrix = bowl_matrix.div(bowl_matrix.sum(axis=1), axis=0)
                bowler = np.random.choice(range(1,len(bowl_matrix)+1), p=bowl_matrix.loc[bowler])
                copy = non_striker
                non_striker = striker
                striker = copy
                
            if(over >= 21 or wickets_innings >= 10): innings_ongoing = False
            if(innings > 1 and score > target): innings_ongoing = False
            if(innings_ongoing == False): print(bat_team_name,score,"/",wickets_innings,"in",6*over-6+ball-1,"balls")
         
        bat_outcome['balls_faced'] = bat_outcome[['0s','1s','2s','4s','6s','dismissals']].sum(axis=1)
        bat_outcome['runs'] = bat_outcome['1s'] + bat_outcome['2s']*2 + bat_outcome['4s']*4 + bat_outcome['6s']*6
        bowl_outcome['balls_bowled'] = bowl_outcome[['0s','1s','2s','4s','6s','wickets']].sum(axis=1)
        bowl_outcome['runs'] = bowl_outcome['1s'] + bowl_outcome['2s']*2 + bowl_outcome['4s']*4 + bowl_outcome['6s']*6 + bowl_outcome['extras']
        bat_outcome = bat_outcome.drop('Pos_std',axis=1)
        bowl_outcome = bowl_outcome.drop(['Pos_bowler_std','usage'],axis=1)
        
        if(print_val == 1): print(bat_outcome['runs'].sum(),bat_outcome['dismissals'].sum(),bowl_outcome['runs'].sum(),bowl_outcome['wickets'].sum(),over,ball)
                
        match_bat_outcome.append(bat_outcome)
        match_bowl_outcome.append(bowl_outcome)
        innings += 1
        
        if(innings > 2): match_ongoing = False
        elif(innings == 2): target = score
      
    match_bat_outcome = pd.concat(match_bat_outcome)
    match_bowl_outcome = pd.concat(match_bowl_outcome)
    return match_bat_outcome, match_bowl_outcome

def mc_game_engine2(t1_name,t2_name,venue,t1_bat,t1_bowl,t2_bat,t2_bowl,full_bowl_matrix,lg_matrix,print_val):

    match_bat_outcome = []
    match_bowl_outcome = []

    innings = 1
    match_ongoing = True
    target = -1

    while match_ongoing:

        if innings == 1:
            bat_df = t1_bat.copy()
            bowl_df = t2_bowl.copy()
            bat_team = t1_name
        else:
            bat_df = t2_bat.copy()
            bowl_df = t1_bowl.copy()
            bat_team = t2_name

        # ------------------ Batting setup ------------------
        bat_out = bat_df[['player','age','Pos','Pos_std']].drop_duplicates()
        bat_out['team'] = bat_team
        bat_out = randomize_pos(bat_out, 1)

        bat_players = bat_out['player'].to_numpy()
        n_bat = len(bat_players)

        bat_0 = np.zeros(n_bat, int)
        bat_1 = np.zeros(n_bat, int)
        bat_2 = np.zeros(n_bat, int)
        bat_4 = np.zeros(n_bat, int)
        bat_6 = np.zeros(n_bat, int)
        bat_w = np.zeros(n_bat, int)

        # ------------------ Bowling setup ------------------
        bowl_out = bowl_df[['player','age','type','Pos_bowler','Pos_bowler_std','usage']].drop_duplicates()
        bowl_out['team'] = t2_name if innings == 1 else t1_name
        bowl_out = randomize_pos(bowl_out, 0)

        bowl_players = bowl_out['player'].to_numpy()
        bowl_types = bowl_out['type'].to_numpy()
        n_bowl = len(bowl_players)

        bowl_0 = np.zeros(n_bowl, int)
        bowl_1 = np.zeros(n_bowl, int)
        bowl_2 = np.zeros(n_bowl, int)
        bowl_4 = np.zeros(n_bowl, int)
        bowl_6 = np.zeros(n_bowl, int)
        bowl_w = np.zeros(n_bowl, int)
        bowl_ex = np.zeros(n_bowl, int)
        bowl_bb = np.zeros(n_bowl, int)

        # ------------------ Cached parameters ------------------
        bat_params = bat_df.set_index(['player','type'])[
            ['r0s','r1s','r2s','r4s','r6s','rBPD']
        ].to_dict('index')

        bowl_params = bowl_df.set_index('player')[
            ['r0s','r1s','r2s','r4s','r6s','rSR','rextras']
        ].to_dict('index')

        venue_params = venue_matrix.set_index(['venue','type'])[
            ['r0s','r1s','r2s','r4s','r6s','rwkts','rextras']
        ].to_dict('index')

        # ------------------ Bowling rotation ------------------
        bowl_matrix = full_bowl_matrix.copy()
        ss = mc_steady_state(bowl_matrix)
        try: ss_factor = bowl_out['usage'].to_numpy()[:len(ss)] / ss
        except ValueError: ss_factor = bowl_out['usage'].to_numpy() / ss[:len(bowl_out)]

        for i, col in enumerate(bowl_matrix.columns):
            bowl_matrix[col] *= ss_factor[i] if i < len(ss_factor) else 0
        bowl_matrix = bowl_matrix.div(bowl_matrix.sum(axis=1), axis=0)

        # ------------------ Innings state ------------------
        striker = 0
        non_striker = 1
        next_batsman = 2
        bowler = 0

        score = 0
        wickets = 0
        over = 1
        ball = 1

        innings_ongoing = True

        def get_probs(over, striker_i, bowler_i):
            bname = bat_players[striker_i]
            blname = bowl_players[bowler_i]
            btype = bowl_types[bowler_i]

            bp = bat_params[(bname, btype)]
            blp = bowl_params[blname]
            vp = venue_params[(venue, btype)]
            lm = lg_matrix.loc[over]

            p0 = lm['0s_ball'] * vp['r0s'] * bp['r0s'] * blp['r0s']
            p1 = lm['1s_ball'] * vp['r1s'] * bp['r1s'] * blp['r1s']
            p2 = lm['2s_ball'] * vp['r2s'] * bp['r2s'] * blp['r2s']
            p4 = lm['4s_ball'] * vp['r4s'] * bp['r4s'] * blp['r4s']
            p6 = lm['6s_ball'] * vp['r6s'] * bp['r6s'] * blp['r6s']
            pw = lm['bowl_wkt_ball'] * vp['rwkts'] / (bp['rBPD'] * blp['rSR'])

            probs = np.array([p0,p1,p2,p4,p6,pw])
            probs /= probs.sum()

            p_extra = lm['extras_ball'] * vp['rextras'] * blp['rextras']
            return probs, p_extra

        # ================== BALL LOOP ==================
        while innings_ongoing:
            probs, p_extra = get_probs(over, striker, bowler)
            striker_name = bat_players[striker]
            bowler_name = bowl_players[bowler]

            if random.random() <= p_extra:
                score += 1
                bowl_ex[bowler] += 1
                if print_val == 1:
                    print(over, ball, bowler_name, striker_name, "extra")

            else:
                outcome = np.random.choice(6, p=probs)

                if outcome == 0:
                    bat_0[striker] += 1
                    bowl_0[bowler] += 1
                    if print_val == 1:
                        print(over, ball, bowler_name, striker_name, "dot")

                elif outcome == 1:
                    bat_1[striker] += 1
                    bowl_1[bowler] += 1
                    score += 1
                    if print_val == 1:
                        print(over, ball, bowler_name, striker_name, "single")
                    striker, non_striker = non_striker, striker

                elif outcome == 2:
                    bat_2[striker] += 1
                    bowl_2[bowler] += 1
                    score += 2
                    if print_val == 1:
                        print(over, ball, bowler_name, striker_name, "two")

                elif outcome == 3:
                    bat_4[striker] += 1
                    bowl_4[bowler] += 1
                    score += 4
                    if print_val == 1:
                        print(over, ball, bowler_name, striker_name, "four")

                elif outcome == 4:
                    bat_6[striker] += 1
                    bowl_6[bowler] += 1
                    score += 6
                    if print_val == 1:
                        print(over, ball, bowler_name, striker_name, "six")

                else:
                    bat_w[striker] += 1
                    bowl_w[bowler] += 1
                    wickets += 1
                    if print_val == 1:
                        print(over, ball, bowler_name, striker_name, "wicket")
                    striker = next_batsman
                    next_batsman += 1
                    if wickets >= 10:
                        break

                bowl_bb[bowler] += 1
                ball += 1

            # ---- Over end ----
            if ball > 6:
                ball = 1
                over += 1
                striker, non_striker = non_striker, striker

                if bowl_bb[bowler] >= 24:
                    bowl_matrix.iloc[:, bowler] = 0
                    bowl_matrix = bowl_matrix.div(bowl_matrix.sum(axis=1), axis=0)

                bowler = np.random.choice(range(len(bowl_matrix)), p=bowl_matrix.iloc[bowler].to_numpy())

            if over >= 21:
                innings_ongoing = False
            if innings == 2 and score > target:
                innings_ongoing = False

        # ------------------ Innings print ------------------
        if print_val == 1:
            balls = 6*(over-1) + ball - 1
            print(bat_team, score, "/", wickets, "in", balls, "balls")

        # ------------------ Write back ------------------
        bat_out['0s'] = bat_0
        bat_out['1s'] = bat_1
        bat_out['2s'] = bat_2
        bat_out['4s'] = bat_4
        bat_out['6s'] = bat_6
        bat_out['dismissals'] = bat_w
        bat_out['balls_faced'] = bat_0 + bat_1 + bat_2 + bat_4 + bat_6 + bat_w
        bat_out['runs'] = bat_1 + 2*bat_2 + 4*bat_4 + 6*bat_6
        bat_out = bat_out.drop(columns=['Pos_std'])

        bowl_out['0s'] = bowl_0
        bowl_out['1s'] = bowl_1
        bowl_out['2s'] = bowl_2
        bowl_out['4s'] = bowl_4
        bowl_out['6s'] = bowl_6
        bowl_out['wickets'] = bowl_w
        bowl_out['extras'] = bowl_ex
        bowl_out['balls_bowled'] = bowl_bb
        bowl_out['runs'] = bowl_1 + 2*bowl_2 + 4*bowl_4 + 6*bowl_6 + bowl_ex
        bowl_out = bowl_out.drop(columns=['Pos_bowler_std','usage'])

        match_bat_outcome.append(bat_out)
        match_bowl_outcome.append(bowl_out)

        innings += 1
        if innings == 2:
            target = score
        elif innings > 2:
            match_ongoing = False

    return pd.concat(match_bat_outcome), pd.concat(match_bowl_outcome)

def pick_lineup_probabalistically2(lg, df, t):
    tot = 12 if lg in ['ipl', 'ilt'] else 11
    df = df[df[lg] == t]

    # Step 1: force-include prob = 1 players
    sure = df[df['team'] >= 1]
    forced_players = sure['player'].tolist()

    remaining_slots = tot - len(forced_players)
    if remaining_slots <= 0:
        return forced_players[:tot]

    # Step 2: sample from remaining players
    rest = df[df['team'] < 1]
    sampled_rest = rest.sample(
        n=remaining_slots,
        weights='team',
        replace=False
    )['player'].tolist()

    return forced_players + sampled_rest

def multiple_mc_sims(lg,ta_name,tb_name,venue,squads,batter_projection,bowler_projection,lg_matrix,n,print_val2):
    start_time = datetime.now()
    bat_sims = []; bowl_sims=[]; 
    match_outcomes = [['t1','t2','venue','t1_runs','t2_runs','t1_wickets','t2_wickets','t1_balls','t2_balls','t1_win','t2_win']]
    i=0;
    
    #squads = pd.read_excel(f'{path}/excel/projections.xlsx','squads')
    #t2_name = 'SRH'
    #t1_name = 'RCB'
    #venue = 'Uppal'
    #t1 = ['JR Hazlewood', 'B Kumar', 'D Padikkal', 'Rasikh Salam', 'JM Sharma', 'KH Pandya', 'PD Salt', 'R Shepherd', 'RM Patidar', 'Suyash Sharma', 'TH David', 'V Kohli']
    #t2 = ['Abhishek Sharma', 'Aniket Verma', 'DA Payne', 'E Malinga', 'H Klaasen', 'HV Patel', 'Harsh Dubey', 'Ishan Kishan', 'JD Unadkat', 'Nithish Kumar Reddy', 'S Arora', 'TM Head']
    
    print(ta_name,"vs",tb_name,"at",venue)
    squad_pool = squads[((squads[lg] == ta_name) | (squads[lg] == tb_name)) & (squads['team'] > 0)]['player'].to_list()
    bat_proj = batter_projection[batter_projection['player'].isin(squad_pool)]
    bowl_proj = bowler_projection[bowler_projection['player'].isin(squad_pool)]
    
    while(i<n):
        toss = random.random()
        if(toss <= 0.5): 
            t1_name, t2_name = ta_name, tb_name
        else: 
            t1_name, t2_name = tb_name, ta_name
        
        t1 = pick_lineup_probabalistically2(lg,squads,t1_name)
        t2 = pick_lineup_probabalistically2(lg,squads,t2_name)
        """
        t1_bat = bat_proj[bat_proj['player'].isin(t1)]
        t2_bowl = bowl_proj[bowl_proj['player'].isin(t2)]
        t2_bat = bat_proj[bat_proj['player'].isin(t2)]
        t1_bowl = bowl_proj[bowl_proj['player'].isin(t1)]
        """        
        t1_set = set(t1)
        t2_set = set(t2)
        
        t1_bat  = bat_proj[[p in t1_set for p in bat_proj['player'].values]]
        t1_bowl = bowl_proj[[p in t1_set for p in bowl_proj['player'].values]]
        
        t2_bat  = bat_proj[[p in t2_set for p in bat_proj['player'].values]]
        t2_bowl = bowl_proj[[p in t2_set for p in bowl_proj['player'].values]]

        #print("sim",i+1)
        bat_game,bowl_game = mc_game_engine2(t1_name,t2_name,venue,t1_bat,t1_bowl,t2_bat,t2_bowl,bowl_pos_matrix.copy(),lg_matrix,0)
        
        bat_game['played'] = 1
        bowl_game['played'] = 1
        
        bat_sims.append(bat_game)
        bowl_sims.append(bowl_game)
        
        t1_runs = bowl_game.loc[bowl_game['team']==t2_name,'runs'].sum()
        t2_runs = bowl_game.loc[bowl_game['team']==t1_name,'runs'].sum()
        t1_wkts = bat_game.loc[bat_game['team']==t1_name,'dismissals'].sum()
        t2_wkts = bat_game.loc[bat_game['team']==t2_name,'dismissals'].sum()
        t1_bf = bat_game.loc[bat_game['team']==t1_name,'balls_faced'].sum()
        t2_bf = bat_game.loc[bat_game['team']==t2_name,'balls_faced'].sum()
        
        if(t1_runs > t2_runs): t1_win = 1; t2_win = 0
        elif(t1_runs < t2_runs): t1_win = 0; t2_win = 1
        else: t1_win = 0.5; t2_win = 0.5
        
        match_outcomes.append([t1_name,t2_name,venue,t1_runs,t2_runs,t1_wkts,t2_wkts,t1_bf,t2_bf,t1_win,t2_win])
        i+=1
        #print()
        
    match_outcomes = pd.DataFrame(match_outcomes)
    match_outcomes.columns = match_outcomes.iloc[0];match_outcomes = match_outcomes.drop(0)
    match_outcomes = match_outcomes.apply(pd.to_numeric, errors='ignore')
    
    if(print_val2 == 1):
        print()
        ta_wins = round(match_outcomes.loc[match_outcomes['t1']==ta_name,'t1_win'].sum() + match_outcomes.loc[match_outcomes['t2']==ta_name,'t2_win'].sum(),2)/n
        ta_runs = round(match_outcomes.loc[match_outcomes['t1']==ta_name,'t1_runs'].sum() + match_outcomes.loc[match_outcomes['t2']==ta_name,'t2_runs'].sum(),2)/n
        ta_balls = round(match_outcomes.loc[match_outcomes['t1']==ta_name,'t1_balls'].sum() + match_outcomes.loc[match_outcomes['t2']==ta_name,'t2_balls'].sum(),2)/n
        ta_wickets = round(match_outcomes.loc[match_outcomes['t1']==ta_name,'t1_wickets'].sum() + match_outcomes.loc[match_outcomes['t2']==ta_name,'t2_wickets'].sum(),2)/n
        tb_wins = round(match_outcomes.loc[match_outcomes['t1']==tb_name,'t1_win'].sum() + match_outcomes.loc[match_outcomes['t2']==tb_name,'t2_win'].sum(),2)/n
        tb_runs = round(match_outcomes.loc[match_outcomes['t1']==tb_name,'t1_runs'].sum() + match_outcomes.loc[match_outcomes['t2']==tb_name,'t2_runs'].sum(),2)/n
        tb_balls = round(match_outcomes.loc[match_outcomes['t1']==tb_name,'t1_balls'].sum() + match_outcomes.loc[match_outcomes['t2']==tb_name,'t2_balls'].sum(),2)/n
        tb_wickets = round(match_outcomes.loc[match_outcomes['t1']==tb_name,'t1_wickets'].sum() + match_outcomes.loc[match_outcomes['t2']==tb_name,'t2_wickets'].sum(),2)/n
        print(ta_name,"p(win)",ta_wins,"score",ta_runs,"/",ta_wickets,"in",ta_balls)
        print(tb_name,"p(win)",tb_wins,"score",tb_runs,"/",tb_wickets,"in",tb_balls)
        print()
        
    print("total minutes for run",round((datetime.now()-start_time).total_seconds()/60,2))
    return bat_sims,bowl_sims,match_outcomes

def mc_tournament(lg,squads,batter_projection,bowler_projection,lg_matrix,n):
    schedule = pd.read_excel(f'{path}/excel/projections.xlsx','schedule', index_col=0)
    schedule = schedule.fillna(0)
    
    table = pd.DataFrame(columns=['team','wins','playoffs'])
    table['team'] = list(set(schedule['Home'].to_list() + schedule['Away'].to_list()))
    table['wins'] = table['wins'].fillna(0)
    table['playoffs'] = table['playoffs'].fillna(0)
    home_wins = schedule.pivot_table(index='Home',values='home_win',aggfunc="sum")
    away_wins = schedule.pivot_table(index='Away',values='away_win',aggfunc="sum")
    table['wins'] = table['team'].map(home_wins['home_win'] + away_wins['away_win'])
    
    pending = schedule[(schedule['home_win']+schedule['away_win'])<=0]    
    bat_game_t = []; bowl_game_t = []; results_t = []
    
    for p in pending.values:
        bat_game_i,bowl_game_i,game_result_i = multiple_mc_sims(lg,p[1],p[2],p[3],squads,batter_projection,bowler_projection,lg_matrix,n,0)
        bat_game_i,bowl_game_i = summarize_df(bat_game_i,bowl_game_i,n)
        
        bat_game_t.append(bat_game_i)
        bowl_game_t.append(bowl_game_i)
        results_t.append(game_result_i)
    
    r = 0; all_tables = []
    while(r<n):
        r2 = 0; table_i = table.copy()
        while(r2<len(pending)):
            table_i.loc[table_i['team']==results_t[r2].iloc[r]['t1'],'wins'] += results_t[r2].iloc[r]['t1_win']
            table_i.loc[table_i['team']==results_t[r2].iloc[r]['t2'],'wins'] += results_t[r2].iloc[r]['t2_win']
            r2+=1
        table_i.loc[table_i.nlargest(4, 'wins').index, 'playoffs'] = 1
        all_tables.append(table_i)
        r+=1
    all_tables = pd.concat(all_tables)
    all_tables = all_tables.groupby(['team']).mean().reset_index()
    
    return bat_game_t,bowl_game_t,all_tables
        
def summarize_df(bat_sims,bowl_sims,n):    
    bat_sims = pd.concat(bat_sims)
    bat_sims = bat_sims.groupby(['player','team']).sum().reset_index()
    bat_sims['Pos'] /= bat_sims['played']
    bat_sims['age'] /= bat_sims['played']
    bat_sims[['0s', '1s', '2s', '4s', '6s', 'dismissals', 'balls_faced', 'runs', 'played']] /= n

    bowl_sims = pd.concat(bowl_sims)
    bowl_sims = bowl_sims.groupby(['player','team','type']).sum().reset_index()
    bowl_sims['age'] /= bowl_sims['played']
    bowl_sims['Pos_bowler'] /= bowl_sims['played']
    bowl_sims[['0s', '1s', '2s', '4s', '6s', 'wickets', 'extras', 'balls_bowled', 'runs', 'played']] /= n
    
    return bat_sims,bowl_sims

def generate_projections(league,read_file):
    if(league in test_leagues()): sheet_p = 'tests'; sheet_m = 'tests'
    elif(league in short_leagues()): sheet_p = 'lo'; sheet_m = 'hundred'
    elif(league in odi_leagues()): sheet_p = 'lo'; sheet_m = 'odi'
    else: sheet_p = 'lo'; sheet_m = 't20i'
    
    if(read_file == 0):     
        batter, factors_bat_pace, factors_bat_spin, bowler, factors_bowler_pace, factors_bowler_spin = extract_all_league_stats(leagues_considered(league))
    
        aging_factors = aging_analysis(batter,1)
        aging_factors_bowler = aging_analysis(bowler,0)
        print(aging_factors,aging_factors_bowler)
        aging = [aging_factors_bowler,aging_factors]
    
        batter,scale = apply_factors(batter, factors_bat_pace, factors_bat_spin, league, leagues_considered(league), 1)
        scale = league_scaling(scale.copy(),league,1)
        batter = stats_concat(batter.copy(),scale.copy(),1)
    
        bowler,scale_bowler = apply_factors(bowler.copy(), factors_bowler_pace, factors_bowler_spin, league, leagues_considered(league), 0)
        scale_bowler = league_scaling(scale_bowler.copy(),league,0)
        bowler = stats_concat(bowler.copy(),scale_bowler.copy(),0)
    
        print(factors_bowler_pace,factors_bowler_spin,factors_bat_pace,factors_bat_spin)
        league_conversions = [factors_bowler_pace, factors_bowler_spin, factors_bat_pace, factors_bat_spin]
        league_scales = [scale_bowler, scale]
    
        player_name_changes_list = player_name_changes()
        batter['striker'] = batter['striker'].map(player_name_changes_list).fillna(batter['striker'])
        bowler['bowler'] = bowler['bowler'].map(player_name_changes_list).fillna(bowler['bowler'])    
    
        full_player_list = list(set(batter['striker'].to_list() + bowler['bowler'].to_list()))
        batter_projection = player_projections(batter,1,full_player_list)
        bowler_projection = player_projections(bowler,0,full_player_list)
        
        batter_projection = apply_aging_factors(batter_projection.copy(),aging[1],batter,1)
        bowler_projection = apply_aging_factors(bowler_projection.copy(),aging[0],bowler,0)
    
        adj_bowling_usage = bowling_usage(league,batter,bowler)
        bowler_projection = bowler_projection.merge(adj_bowling_usage, on='player', how='left')
    
        batter_projection = batter_projection.drop_duplicates(subset=['player','type'])
        bowler_projection = bowler_projection.drop_duplicates(subset=['player','type'])
        
        bowl_pos_matrix = bat_bowl_usage_matrix(league)
        venue_matrix = venue_league_matrix(league)
        
        with pd.ExcelWriter(f'{path}/excel/projections.xlsx', engine="openpyxl") as writer:
            batter_projection.to_excel(writer, sheet_name=f"{sheet_p} batters")
            bowler_projection.to_excel(writer, sheet_name=f"{sheet_p} bowlers")
            bowl_pos_matrix.to_excel(writer, sheet_name=f"{sheet_m} bowl matrix")
            venue_matrix.to_excel(writer, sheet_name=f"{sheet_p} venues")
            
    else:
        batter_projection = pd.read_excel(f'{path}/excel/projections.xlsx',f'{sheet_p} batters', index_col=0)
        bowler_projection = pd.read_excel(f'{path}/excel/projections.xlsx',f'{sheet_p} bowlers', index_col=0)
        bowl_pos_matrix = pd.read_excel(f'{path}/excel/projections.xlsx',f'{sheet_m} bowl matrix', index_col=0)
        venue_matrix = pd.read_excel(f'{path}/excel/projections.xlsx',f'{sheet_p} venues', index_col=0)

    return batter_projection, bowler_projection, bowl_pos_matrix, venue_matrix

#%% concat raw data files
concat_game_files('mlc')

#%% venue stats derived
batter_projection, bowler_projection, bowl_pos_matrix, venue_matrix = generate_projections(league,1)
league_matrix = comp_matrix(league)

#%% squad info
#squads = squad_info()
squads = pd.read_excel(f'{path}/excel/projections.xlsx','squads')
#lineups = active_lineups(league)

#%% sims
#bat_game,bowl_game = mc_game_engine(bowl_pos_matrix.copy(),1)

#bat_game,bowl_game,game_result = multiple_mc_sims(league,'Gujarat Titans','Royal Challengers Bengaluru','Chinnaswamy',squads,batter_projection,bowler_projection,league_matrix,1000,1)
#bat_game,bowl_game = summarize_df(bat_game,bowl_game,1000)

bat_game,bowl_game,game_result = mc_tournament(league,squads,batter_projection,bowler_projection,league_matrix,1000)
