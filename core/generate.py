# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 18:00:04 2024
converting cricsheet data into league summary tables
updated version of generate.py
@author: Subramanya.Ganti
"""
import numpy as np
import pandas as pd
from sys import getsizeof
import datetime
pd.options.mode.chained_assignment = None  # default='warn'
np.seterr(divide='ignore', invalid='ignore')
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

comp = 'blast'
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'

if(comp=='hundred' or comp=='hundredw'):
    p1 = 6; p2 = 12; p3 = 17; factor = (5/6);  #hundred
elif(comp=='odi' or comp=='odiw' or comp=='odiq' or comp=='rlc' or comp=='cwc' or comp=='rhf'):
    p1 = 10; p2 = 26; p3 = 40; factor = 2.5;   #odi
elif(comp=='tests' or comp == 'cc' or comp == 'shield' or comp == 'pks' or comp == 'testsw'):
    p1 = 30; p2 = 55; p3 = 80; factor = 11.25; #test
else:
    p1 = 6; p2 = 12; p3 = 17; factor = 1;      #assume its a t20 by default

file0 = f'{path}/raw/{comp}.csv'
games_played = f'{path}/raw/{comp}_GP.csv'
venues = f'{path}/excel/venues.xlsx'
people = f'{path}/excel/people.xlsx'
output_file = f"{path}/summary/{comp}_summary.xlsx"

file0 = pd.read_csv(file0,sep=',',low_memory=False)
games_played = pd.read_csv(games_played,sep=',',low_memory=False)
venues = pd.read_excel(venues,'Sheet1')
file0 = file0.fillna(0)
now = datetime.datetime.now()
print(now.time())
start_size = getsizeof(file0)/(1024.0**2)
print(comp,'Dataframe size: %2.2f MB'%start_size)

file0['balls_batsman'] = 1
file0['balls_bowler'] = 1
file0['dots'] = 0
file0['ones'] = 0
file0['twos'] = 0
file0['threes'] = 0
file0['fours'] = 0
file0['sixes'] = 0
file0['outs_batsman'] = 0
file0['outs_ns'] = 0
file0['outs_bowler'] = 0
file0['powerplay'] = 0
file0['middle'] = 0
file0['setup'] = 0
file0['death'] = 0

file0.loc[file0['wides']>0,'balls_batsman'] = 0
file0.loc[(file0['wides']>0)|(file0['noballs']>0),'balls_bowler'] = 0
file0.loc[(file0['runs_off_bat']==0)&(file0['noballs']==0)&(file0['wides']==0),'dots'] = 1
file0.loc[file0['runs_off_bat']==1,'ones'] = 1
file0.loc[file0['runs_off_bat']==2,'twos'] = 1
file0.loc[file0['runs_off_bat']==3,'threes'] = 1
file0.loc[file0['runs_off_bat']==4,'fours'] = 1
file0.loc[file0['runs_off_bat']==6,'sixes'] = 1
file0.loc[file0['striker']==file0['player_dismissed'],'outs_batsman'] = 1
file0.loc[file0['non_striker']==file0['player_dismissed'],'outs_ns'] = 1
file0.loc[(file0['striker']==file0['player_dismissed'])&(file0['wicket_type']!='run out')&(file0['wicket_type']!='retired hurt')&(file0['wicket_type']!='retired out')&(file0['wicket_type']!='obstructing the field'),'outs_bowler'] = 1

file0.loc[file0['ball']<p1,'powerplay'] = 1
file0.loc[(file0['ball']>=p1)&(file0['ball']<p2),'middle'] = 1
file0.loc[(file0['ball']>=p2)&(file0['ball']<p3),'setup'] = 1
file0.loc[file0['ball']>=p3,'death'] = 1

file0['balls_batsman_powerplay'] = file0['balls_batsman'] * file0['powerplay']
file0['runs_off_bat_powerplay'] = file0['runs_off_bat'] * file0['powerplay']
file0['outs_batsman_powerplay'] = (file0['outs_batsman']+file0['outs_ns']) * file0['powerplay']
file0['balls_batsman_middle'] = file0['balls_batsman'] * file0['middle']
file0['runs_off_bat_middle'] = file0['runs_off_bat'] * file0['middle']
file0['outs_batsman_middle'] = (file0['outs_batsman']+file0['outs_ns']) * file0['middle']
file0['balls_batsman_setup'] = file0['balls_batsman'] * file0['setup']
file0['runs_off_bat_setup'] = file0['runs_off_bat'] * file0['setup']
file0['outs_batsman_setup'] = (file0['outs_batsman']+file0['outs_ns']) * file0['setup']
file0['balls_batsman_death'] = file0['balls_batsman'] * file0['death']
file0['runs_off_bat_death'] = file0['runs_off_bat'] * file0['death']
file0['outs_batsman_death'] = (file0['outs_batsman']+file0['outs_ns']) * file0['death']

file0['balls_bowler_powerplay'] = file0['balls_bowler'] * file0['powerplay']
file0['runs_bowl_powerplay'] = (file0['runs_off_bat']+file0['extras']) * file0['powerplay']
file0['outs_bowler_powerplay'] = file0['outs_bowler'] * file0['powerplay']
file0['balls_bowler_middle'] = file0['balls_bowler'] * file0['middle']
file0['runs_bowl_middle'] = (file0['runs_off_bat']+file0['extras']) * file0['middle']
file0['outs_bowler_middle'] = file0['outs_bowler'] * file0['middle']
file0['balls_bowler_setup'] = file0['balls_bowler'] * file0['setup']
file0['runs_bowl_setup'] = (file0['runs_off_bat']+file0['extras']) * file0['setup']
file0['outs_bowler_setup'] = file0['outs_bowler'] * file0['setup']
file0['balls_bowler_death'] = file0['balls_bowler'] * file0['death']
file0['runs_bowl_death'] = (file0['runs_off_bat']+file0['extras']) * file0['death']
file0['outs_bowler_death'] = file0['outs_bowler'] * file0['death']

print("team balls faced dumped")
now = datetime.datetime.now()
print(now.time())

year_bat = pd.pivot_table(file0,values=['balls_batsman','runs_off_bat','dots','ones','twos','threes','fours','sixes','outs_batsman','outs_ns','balls_batsman_powerplay','balls_batsman_middle','balls_batsman_setup','balls_batsman_death'],index=['season'],aggfunc=np.sum)
year_bat['outs'] = year_bat['outs_batsman'] + year_bat['outs_ns']
year_bat = year_bat.reset_index()
year_bat.rename(columns = {'season':'Season', 'balls_batsman':'Sum of balls_batsman', 'runs_off_bat':'Sum of runs_off_bat', 'outs':'Sum of outs_batsman', 'dots':'Sum of 0s', 'ones':'Sum of 1s', 
                           'twos':'Sum of 2s', 'threes':'Sum of 3s', 'fours':'Sum of 4s', 'sixes':'Sum of 6s', 'balls_batsman_powerplay':'Sum of powerplay', 'balls_batsman_middle':'Sum of middle',
                           'balls_batsman_setup':'Sum of setup', 'balls_batsman_death':'Sum of death'}, inplace = True)

year_bat = year_bat[["Season","Sum of balls_batsman","Sum of runs_off_bat","Sum of 0s","Sum of 1s","Sum of 2s","Sum of 3s","Sum of 4s","Sum of 6s","Sum of outs_batsman","Sum of powerplay","Sum of middle","Sum of setup","Sum of death"]]
year_bat['runs/ball'] = year_bat['Sum of runs_off_bat']/year_bat['Sum of balls_batsman']
year_bat['0s/ball'] = year_bat['Sum of 0s']/year_bat['Sum of balls_batsman']
year_bat['1s/ball'] = year_bat['Sum of 1s']/year_bat['Sum of balls_batsman']
year_bat['2s/ball'] = year_bat['Sum of 2s']/year_bat['Sum of balls_batsman']
year_bat['3s/ball'] = year_bat['Sum of 3s']/year_bat['Sum of balls_batsman']
year_bat['4s/ball'] = year_bat['Sum of 4s']/year_bat['Sum of balls_batsman']
year_bat['6s/ball'] = year_bat['Sum of 6s']/year_bat['Sum of balls_batsman']
year_bat['wickets/ball'] = year_bat['Sum of outs_batsman']/year_bat['Sum of balls_batsman']
year_bat['powerplay/ball'] = year_bat['Sum of powerplay']/year_bat['Sum of balls_batsman']
year_bat['middle/ball'] = year_bat['Sum of middle']/year_bat['Sum of balls_batsman']
year_bat['setup/ball'] = year_bat['Sum of setup']/year_bat['Sum of balls_batsman']
year_bat['death/ball'] = year_bat['Sum of death']/year_bat['Sum of balls_batsman']


year_bowl = pd.pivot_table(file0,values=['balls_bowler','runs_off_bat','extras','dots','ones','twos','threes','fours','sixes','outs_bowler','balls_bowler_powerplay','balls_bowler_middle','balls_bowler_setup','balls_bowler_death'],index=['season'],aggfunc=np.sum)
year_bowl['runs_off_bowl'] = year_bowl['runs_off_bat'] + year_bowl['extras']
year_bowl = year_bowl.reset_index()
year_bowl.rename(columns = {'season':'Season', 'balls_bowler':'Sum of balls_bowler', 'runs_off_bat':'Sum of runs_off_bat', 'outs_bowler':'Sum of outs_bowler', 'dots':'Sum of 0s', 'ones':'Sum of 1s', 
                           'twos':'Sum of 2s', 'threes':'Sum of 3s', 'fours':'Sum of 4s', 'sixes':'Sum of 6s', 'balls_bowler_powerplay':'Sum of powerplay', 'balls_bowler_middle':'Sum of middle',
                           'balls_bowler_setup':'Sum of setup', 'balls_bowler_death':'Sum of death', 'extras':'Sum of extras'}, inplace = True)
year_bowl = year_bowl[["Season","Sum of balls_bowler","Sum of runs_off_bat","Sum of 0s","Sum of 1s","Sum of 2s","Sum of 3s","Sum of 4s","Sum of 6s","Sum of extras","Sum of outs_bowler","Sum of powerplay","Sum of middle","Sum of setup","Sum of death"]]
year_bowl['runs/ball'] = year_bowl['Sum of runs_off_bat']/year_bowl['Sum of balls_bowler']
year_bowl['0s/ball'] = year_bowl['Sum of 0s']/year_bowl['Sum of balls_bowler']
year_bowl['1s/ball'] = year_bowl['Sum of 1s']/year_bowl['Sum of balls_bowler']
year_bowl['2s/ball'] = year_bowl['Sum of 2s']/year_bowl['Sum of balls_bowler']
year_bowl['3s/ball'] = year_bowl['Sum of 3s']/year_bowl['Sum of balls_bowler']
year_bowl['4s/ball'] = year_bowl['Sum of 4s']/year_bowl['Sum of balls_bowler']
year_bowl['6s/ball'] = year_bowl['Sum of 6s']/year_bowl['Sum of balls_bowler']
year_bowl['extras/ball'] = year_bowl['Sum of extras']/year_bowl['Sum of balls_bowler']
year_bowl['wickets/ball'] = year_bowl['Sum of outs_bowler']/year_bowl['Sum of balls_bowler']
year_bowl['powerplay/ball'] = year_bowl['Sum of powerplay']/year_bowl['Sum of balls_bowler']
year_bowl['middle/ball'] = year_bowl['Sum of middle']/year_bowl['Sum of balls_bowler']
year_bowl['setup/ball'] = year_bowl['Sum of setup']/year_bowl['Sum of balls_bowler']
year_bowl['death/ball'] = year_bowl['Sum of death']/year_bowl['Sum of balls_bowler']

year_bat_phase = pd.pivot_table(file0,values=['balls_batsman_powerplay','runs_off_bat_powerplay','outs_batsman_powerplay','balls_batsman_middle','runs_off_bat_middle','outs_batsman_middle','balls_batsman_setup','runs_off_bat_setup','outs_batsman_setup','balls_batsman_death','runs_off_bat_death','outs_batsman_death'],index=['season'],aggfunc=np.sum)
year_bat_phase = year_bat_phase.reset_index()
year_bat_phase.rename(columns = {'season':'Season', 'balls_batsman_powerplay':'Sum of powerplay', 'runs_off_bat_powerplay':'Sum of pp_runs_batsman', 'outs_batsman_powerplay':'Sum of pp_wickets_batsman',
                                 'balls_batsman_middle':'Sum of middle', 'runs_off_bat_middle':'Sum of mid_runs_batsman', 'outs_batsman_middle':'Sum of mid_wickets_batsman',
                                 'balls_batsman_setup':'Sum of setup', 'runs_off_bat_setup':'Sum of setup_runs_batsman', 'outs_batsman_setup':'Sum of setup_wickets_batsman',
                                 'balls_batsman_death':'Sum of death', 'runs_off_bat_death':'Sum of death_runs_batsman', 'outs_batsman_death':'Sum of death_wickets_batsman',}, inplace = True)
year_bat_phase = year_bat_phase[["Season","Sum of powerplay","Sum of pp_runs_batsman","Sum of pp_wickets_batsman","Sum of middle","Sum of mid_runs_batsman","Sum of mid_wickets_batsman","Sum of setup","Sum of setup_runs_batsman","Sum of setup_wickets_batsman","Sum of death","Sum of death_runs_batsman","Sum of death_wickets_batsman"]]
year_bat_phase['pp AVG'] = year_bat_phase['Sum of powerplay']/year_bat_phase['Sum of pp_wickets_batsman']
year_bat_phase['mid AVG'] = year_bat_phase['Sum of middle']/year_bat_phase['Sum of mid_wickets_batsman']
year_bat_phase['setup AVG'] = year_bat_phase['Sum of setup']/year_bat_phase['Sum of setup_wickets_batsman']
year_bat_phase['death AVG'] = year_bat_phase['Sum of death']/year_bat_phase['Sum of death_wickets_batsman']
year_bat_phase['pp SR'] = 100*year_bat_phase['Sum of pp_runs_batsman']/year_bat_phase['Sum of powerplay']
year_bat_phase['mid SR'] = 100*year_bat_phase['Sum of mid_runs_batsman']/year_bat_phase['Sum of middle']
year_bat_phase['setup SR'] = 100*year_bat_phase['Sum of setup_runs_batsman']/year_bat_phase['Sum of setup']
year_bat_phase['death SR'] = 100*year_bat_phase['Sum of death_runs_batsman']/year_bat_phase['Sum of death']

year_bowl_phase = pd.pivot_table(file0,values=['balls_bowler_powerplay','runs_bowl_powerplay','outs_bowler_powerplay','balls_bowler_middle','runs_bowl_middle','outs_bowler_middle','balls_bowler_setup','runs_bowl_setup','outs_bowler_setup','balls_bowler_death','runs_bowl_death','outs_bowler_death'],index=['season'],aggfunc=np.sum)
year_bowl_phase = year_bowl_phase.reset_index()
year_bowl_phase.rename(columns = {'season':'Season', 'balls_bowler_powerplay':'Sum of powerplay', 'runs_bowl_powerplay':'Sum of pp_runs_bowler', 'outs_bowler_powerplay':'Sum of pp_wickets_bowler',
                                 'balls_bowler_middle':'Sum of middle', 'runs_bowl_middle':'Sum of mid_runs_bowler', 'outs_bowler_middle':'Sum of mid_wickets_bowler',
                                 'balls_bowler_setup':'Sum of setup', 'runs_bowl_setup':'Sum of setup_runs_bowler', 'outs_bowler_setup':'Sum of setup_wickets_bowler',
                                 'balls_bowler_death':'Sum of death', 'runs_bowl_death':'Sum of death_runs_bowler', 'outs_bowler_death':'Sum of death_wickets_bowler',}, inplace = True)
year_bowl_phase = year_bowl_phase[["Season","Sum of powerplay","Sum of pp_runs_bowler","Sum of pp_wickets_bowler","Sum of middle","Sum of mid_runs_bowler","Sum of mid_wickets_bowler","Sum of setup","Sum of setup_runs_bowler","Sum of setup_wickets_bowler","Sum of death","Sum of death_runs_bowler","Sum of death_wickets_bowler"]]
year_bowl_phase['pp ECON'] = 6*year_bowl_phase['Sum of pp_runs_bowler']/year_bowl_phase['Sum of powerplay']
year_bowl_phase['mid ECON'] = 6*year_bowl_phase['Sum of mid_runs_bowler']/year_bowl_phase['Sum of middle']
year_bowl_phase['setup ECON'] = 6*year_bowl_phase['Sum of setup_runs_bowler']/year_bowl_phase['Sum of setup']
year_bowl_phase['death ECON'] = 6*year_bowl_phase['Sum of death_runs_bowler']/year_bowl_phase['Sum of death']
year_bowl_phase['pp SR'] = year_bowl_phase['Sum of powerplay']/year_bowl_phase['Sum of pp_wickets_bowler']
year_bowl_phase['mid SR'] = year_bowl_phase['Sum of middle']/year_bowl_phase['Sum of mid_wickets_bowler']
year_bowl_phase['setup SR'] = year_bowl_phase['Sum of setup']/year_bowl_phase['Sum of setup_wickets_bowler']
year_bowl_phase['death SR'] = year_bowl_phase['Sum of death']/year_bowl_phase['Sum of death_wickets_bowler']


print("league average and phases data dumped")
now = datetime.datetime.now()
print(now.time())

#venues_season = file0[['venue','season']]
#venues_season = venues_season.drop_duplicates()
file0 = file0.merge(venues, left_on='venue', right_on='venue')

venue_bat_phase = [["Venue","Season","Sum of powerplay","Sum of pp_runs_batsman","Sum of pp_wickets_batsman","Sum of middle","Sum of mid_runs_batsman","Sum of mid_wickets_batsman","Sum of setup","Sum of setup_runs_batsman","Sum of setup_wickets_batsman","Sum of death","Sum of death_runs_batsman","Sum of death_wickets_batsman","pp AVG","mid AVG","setup AVG","death AVG","pp SR","mid SR","setup SR","death SR"]]
venue_bowl_phase = [["Venue","Season","Sum of powerplay","Sum of pp_runs_bowler","Sum of pp_wickets_bowler","Sum of middle","Sum of mid_runs_bowler","Sum of mid_wickets_bowler","Sum of setup","Sum of setup_runs_bowler","Sum of setup_wickets_bowler","Sum of death","Sum of death_runs_bowler","Sum of death_wickets_bowler","pp ECON","mid ECON","setup ECON","death ECON","pp SR","mid SR","setup SR","death SR"]]

venue_bat_phase = pd.pivot_table(file0,values=['balls_batsman_powerplay','runs_off_bat_powerplay','outs_batsman_powerplay','balls_batsman_middle','runs_off_bat_middle','outs_batsman_middle','balls_batsman_setup','runs_off_bat_setup','outs_batsman_setup','balls_batsman_death','runs_off_bat_death','outs_batsman_death'],index=['short','season'],aggfunc=np.sum)
venue_bat_phase = venue_bat_phase.reset_index()
venue_bat_phase.rename(columns = {'short':'Venue','season':'Season', 'balls_batsman_powerplay':'Sum of powerplay', 'runs_off_bat_powerplay':'Sum of pp_runs_batsman', 'outs_batsman_powerplay':'Sum of pp_wickets_batsman',
                                 'balls_batsman_middle':'Sum of middle', 'runs_off_bat_middle':'Sum of mid_runs_batsman', 'outs_batsman_middle':'Sum of mid_wickets_batsman',
                                 'balls_batsman_setup':'Sum of setup', 'runs_off_bat_setup':'Sum of setup_runs_batsman', 'outs_batsman_setup':'Sum of setup_wickets_batsman',
                                 'balls_batsman_death':'Sum of death', 'runs_off_bat_death':'Sum of death_runs_batsman', 'outs_batsman_death':'Sum of death_wickets_batsman',}, inplace = True)
venue_bat_phase = venue_bat_phase[["Venue","Season","Sum of powerplay","Sum of pp_runs_batsman","Sum of pp_wickets_batsman","Sum of middle","Sum of mid_runs_batsman","Sum of mid_wickets_batsman","Sum of setup","Sum of setup_runs_batsman","Sum of setup_wickets_batsman","Sum of death","Sum of death_runs_batsman","Sum of death_wickets_batsman"]]
venue_bat_phase['pp AVG'] = venue_bat_phase['Sum of powerplay']/venue_bat_phase['Sum of pp_wickets_batsman']
venue_bat_phase['mid AVG'] = venue_bat_phase['Sum of middle']/venue_bat_phase['Sum of mid_wickets_batsman']
venue_bat_phase['setup AVG'] = venue_bat_phase['Sum of setup']/venue_bat_phase['Sum of setup_wickets_batsman']
venue_bat_phase['death AVG'] = venue_bat_phase['Sum of death']/venue_bat_phase['Sum of death_wickets_batsman']
venue_bat_phase['pp SR'] = 100*venue_bat_phase['Sum of pp_runs_batsman']/venue_bat_phase['Sum of powerplay']
venue_bat_phase['mid SR'] = 100*venue_bat_phase['Sum of mid_runs_batsman']/venue_bat_phase['Sum of middle']
venue_bat_phase['setup SR'] = 100*venue_bat_phase['Sum of setup_runs_batsman']/venue_bat_phase['Sum of setup']
venue_bat_phase['death SR'] = 100*venue_bat_phase['Sum of death_runs_batsman']/venue_bat_phase['Sum of death']

venue_bowl_phase = pd.pivot_table(file0,values=['balls_bowler_powerplay','runs_bowl_powerplay','outs_bowler_powerplay','balls_bowler_middle','runs_bowl_middle','outs_bowler_middle','balls_bowler_setup','runs_bowl_setup','outs_bowler_setup','balls_bowler_death','runs_bowl_death','outs_bowler_death'],index=['short','season'],aggfunc=np.sum)
venue_bowl_phase = venue_bowl_phase.reset_index()
venue_bowl_phase.rename(columns = {'short':'Venue','season':'Season', 'balls_bowler_powerplay':'Sum of powerplay', 'runs_bowl_powerplay':'Sum of pp_runs_bowler', 'outs_bowler_powerplay':'Sum of pp_wickets_bowler',
                                 'balls_bowler_middle':'Sum of middle', 'runs_bowl_middle':'Sum of mid_runs_bowler', 'outs_bowler_middle':'Sum of mid_wickets_bowler',
                                 'balls_bowler_setup':'Sum of setup', 'runs_bowl_setup':'Sum of setup_runs_bowler', 'outs_bowler_setup':'Sum of setup_wickets_bowler',
                                 'balls_bowler_death':'Sum of death', 'runs_bowl_death':'Sum of death_runs_bowler', 'outs_bowler_death':'Sum of death_wickets_bowler',}, inplace = True)
venue_bowl_phase = venue_bowl_phase[["Venue","Season","Sum of powerplay","Sum of pp_runs_bowler","Sum of pp_wickets_bowler","Sum of middle","Sum of mid_runs_bowler","Sum of mid_wickets_bowler","Sum of setup","Sum of setup_runs_bowler","Sum of setup_wickets_bowler","Sum of death","Sum of death_runs_bowler","Sum of death_wickets_bowler"]]
venue_bowl_phase['pp ECON'] = 6*venue_bowl_phase['Sum of pp_runs_bowler']/venue_bowl_phase['Sum of powerplay']
venue_bowl_phase['mid ECON'] = 6*venue_bowl_phase['Sum of mid_runs_bowler']/venue_bowl_phase['Sum of middle']
venue_bowl_phase['setup ECON'] = 6*venue_bowl_phase['Sum of setup_runs_bowler']/venue_bowl_phase['Sum of setup']
venue_bowl_phase['death ECON'] = 6*venue_bowl_phase['Sum of death_runs_bowler']/venue_bowl_phase['Sum of death']
venue_bowl_phase['pp SR'] = venue_bowl_phase['Sum of powerplay']/venue_bowl_phase['Sum of pp_wickets_bowler']
venue_bowl_phase['mid SR'] = venue_bowl_phase['Sum of middle']/venue_bowl_phase['Sum of mid_wickets_bowler']
venue_bowl_phase['setup SR'] = venue_bowl_phase['Sum of setup']/venue_bowl_phase['Sum of setup_wickets_bowler']
venue_bowl_phase['death SR'] = venue_bowl_phase['Sum of death']/venue_bowl_phase['Sum of death_wickets_bowler']

print("venue average and phases data dumped")
now = datetime.datetime.now()
print(now.time())

handedness = pd.read_excel(people,'people')
handedness_bat = handedness[['unique_name','batType']]
handedness_bowl = handedness[['unique_name','bowlType']]

file0 = file0.merge(handedness_bat, left_on='striker', right_on='unique_name')
file0 = file0.merge(handedness_bowl, left_on='bowler', right_on='unique_name')
file0 = file0.drop(columns=['unique_name_x', 'unique_name_y'])
file0 = file0.drop_duplicates()
file0['bowlType_main'] = np.where((file0['bowlType']=='Right-arm offbreak')|(file0['bowlType']=='Legbreak googly')|(file0['bowlType']=='Legbreak')|(file0['bowlType']=='Left-arm wrist-spin')|(file0['bowlType']=='Slow left-arm orthodox'),'spin', 'pace')

matchups = pd.pivot_table(file0,values=['balls_batsman','runs_off_bat','outs_batsman'],index=['bowlType_main','short','season'],aggfunc=np.sum)
matchups = matchups.reset_index()
matchups.rename(columns = {'bowlType_main':'bowl_type', 'short':'venue', 'balls_batsman':'balls', 'outs_batsman':'wickets', 'runs_off_bat':'runs'}, inplace = True)
matchups['AVG'] = matchups['balls']/matchups['wickets']
matchups['SR'] = 100*matchups['runs']/matchups['balls']
matchups = matchups[['bowl_type','venue','season','balls','runs','wickets','AVG','SR']]
matchups = matchups.dropna()

print("venue pace/spin data dumped")
now = datetime.datetime.now()
print(now.time())

player_bat = pd.pivot_table(file0,values=['balls_batsman','runs_off_bat','dots','ones', 'twos', 'threes', 'fours', 'sixes','outs_batsman', 'balls_batsman_powerplay', 'balls_batsman_middle', 'balls_batsman_setup', 'balls_batsman_death',],index=['striker','season','batting_team'],aggfunc=np.sum)
player_bat = player_bat.reset_index()
player_bat.rename(columns = {'striker':'batsman','dots':'0s', 'ones':'1s', 'twos':'2s', 'threes':'3s', 'fours':'4s', 'sixes':'6s',
                             'balls_batsman_powerplay':'powerplay', 'balls_batsman_middle':'middle', 'balls_batsman_setup':'setup', 'balls_batsman_death':'death'}, inplace = True)
player_bat['runs/ball'] = player_bat['runs_off_bat']/player_bat['balls_batsman']
player_bat['0s/ball'] = player_bat['0s']/player_bat['balls_batsman']
player_bat['1s/ball'] = player_bat['1s']/player_bat['balls_batsman']
player_bat['2s/ball'] = player_bat['2s']/player_bat['balls_batsman']
player_bat['3s/ball'] = player_bat['3s']/player_bat['balls_batsman']
player_bat['4s/ball'] = player_bat['4s']/player_bat['balls_batsman']
player_bat['6s/ball'] = player_bat['6s']/player_bat['balls_batsman']
player_bat['wickets/ball'] = player_bat['outs_batsman']/player_bat['balls_batsman']
player_bat['PP usage'] = player_bat['powerplay']/player_bat['balls_batsman']
player_bat['mid usage'] = player_bat['middle']/player_bat['balls_batsman']
player_bat['setup usage'] = player_bat['setup']/player_bat['balls_batsman']
player_bat['death usage'] = player_bat['death']/player_bat['balls_batsman']
player_bat['AVG'] = player_bat['balls_batsman']/player_bat['outs_batsman']
player_bat.loc[player_bat['AVG']>player_bat['balls_batsman'],'AVG']=player_bat['balls_batsman']
player_bat['SR'] = 100*player_bat['runs_off_bat']/player_bat['balls_batsman']
player_bat = player_bat.merge(games_played, left_on=['batsman','season'], right_on=['player','season'])
player_bat['bf_GP'] = player_bat['balls_batsman']/player_bat['GP']
player_bat['usage'] = player_bat['balls_batsman']/(player_bat['GP']*120*factor)
player_bat = pd.merge(player_bat,year_bat_phase[['Season','pp AVG', 'mid AVG', 'setup AVG','death AVG', 'pp SR', 'mid SR', 'setup SR', 'death SR']],left_on='season', right_on='Season')
player_bat['xAVG'] = player_bat['PP usage']*player_bat['pp AVG'] + player_bat['mid usage']*player_bat['mid AVG'] + player_bat['setup usage']*player_bat['setup AVG'] + player_bat['death usage']*player_bat['death AVG']
player_bat['xSR'] = player_bat['PP usage']*player_bat['pp SR'] + player_bat['mid usage']*player_bat['mid SR'] + player_bat['setup usage']*player_bat['setup SR'] + player_bat['death usage']*player_bat['death SR']
player_bat['xruns'] = player_bat['xSR'] * player_bat['balls_batsman']/100
player_bat['xwickets'] = player_bat['balls_batsman']/player_bat['xAVG']
player_bat['RSAA'] = 1.2*(player_bat['SR']-player_bat['xSR'])*player_bat['usage']*factor
player_bat = player_bat[["batsman","season","batting_team","RSAA","usage","balls_batsman","runs_off_bat","0s","1s","2s","3s","4s","6s","outs_batsman","powerplay","middle","setup","death","runs/ball","0s/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","wickets/ball","PP usage","mid usage","setup usage","death usage","AVG","SR","xAVG","xSR","xruns","xwickets","bf_GP"]]
player_bat = player_bat.dropna()


player_bowl = pd.pivot_table(file0,values=['balls_bowler','runs_off_bat','dots','ones', 'twos', 'threes', 'fours', 'sixes','extras','outs_bowler', 'balls_bowler_powerplay', 'balls_bowler_middle', 'balls_bowler_setup', 'balls_bowler_death',],index=['bowler','season','bowling_team'],aggfunc=np.sum)
player_bowl = player_bowl.reset_index()
player_bowl.rename(columns = {'dots':'0s', 'ones':'1s', 'twos':'2s', 'threes':'3s', 'fours':'4s', 'sixes':'6s',
                             'balls_bowler_powerplay':'powerplay', 'balls_bowler_middle':'middle', 'balls_bowler_setup':'setup', 'balls_bowler_death':'death'}, inplace = True)
player_bowl['runs/ball'] = (player_bowl['runs_off_bat'] + player_bowl['extras'])/player_bowl['balls_bowler']
player_bowl['0s/ball'] = player_bowl['0s']/player_bowl['balls_bowler']
player_bowl['1s/ball'] = player_bowl['1s']/player_bowl['balls_bowler']
player_bowl['2s/ball'] = player_bowl['2s']/player_bowl['balls_bowler']
player_bowl['3s/ball'] = player_bowl['3s']/player_bowl['balls_bowler']
player_bowl['4s/ball'] = player_bowl['4s']/player_bowl['balls_bowler']
player_bowl['6s/ball'] = player_bowl['6s']/player_bowl['balls_bowler']
player_bowl['extras/ball'] = player_bowl['extras']/player_bowl['balls_bowler']
player_bowl['wickets/ball'] = player_bowl['outs_bowler']/player_bowl['balls_bowler']
player_bowl['PP usage'] = player_bowl['powerplay']/player_bowl['balls_bowler']
player_bowl['mid usage'] = player_bowl['middle']/player_bowl['balls_bowler']
player_bowl['setup usage'] = player_bowl['setup']/player_bowl['balls_bowler']
player_bowl['death usage'] = player_bowl['death']/player_bowl['balls_bowler']
player_bowl['SR'] = player_bowl['balls_bowler']/player_bowl['outs_bowler']
player_bowl.loc[player_bowl['SR']>player_bowl['balls_bowler'],'SR']=player_bowl['balls_bowler']
player_bowl['ECON'] = 6*player_bowl['runs/ball']
player_bowl = player_bowl.merge(games_played, left_on=['bowler','season'], right_on=['player','season'])
player_bowl['bb_GP'] = player_bowl['balls_bowler']/player_bowl['GP']
player_bowl['usage'] = player_bowl['balls_bowler']/(player_bowl['GP']*120*factor)
player_bowl = pd.merge(player_bowl,year_bowl_phase[['Season','pp ECON','mid ECON', 'setup ECON', 'death ECON', 'pp SR', 'mid SR', 'setup SR','death SR']],left_on='season', right_on='Season')
player_bowl['xECON'] = player_bowl['PP usage']*player_bowl['pp ECON'] + player_bowl['mid usage']*player_bowl['mid ECON'] + player_bowl['setup usage']*player_bowl['setup ECON'] + player_bowl['death usage']*player_bowl['death ECON']
player_bowl['xSR'] = player_bowl['PP usage']*player_bowl['pp SR'] + player_bowl['mid usage']*player_bowl['mid SR'] + player_bowl['setup usage']*player_bowl['setup SR'] + player_bowl['death usage']*player_bowl['death SR']
player_bowl['xruns'] = player_bowl['xECON'] * player_bowl['balls_bowler']/6
player_bowl['xwickets'] = player_bowl['balls_bowler']/player_bowl['xSR']
player_bowl['WTAA'] = factor*120*((1/player_bowl['SR'])-(1/player_bowl['xSR']))*player_bowl['usage']
player_bowl['RCAA'] = 20*(player_bowl['ECON']-player_bowl['xECON'])*player_bowl['usage']*factor - 6*player_bowl['WTAA']*factor
player_bowl = player_bowl[["bowler","season","bowling_team","RCAA","usage","balls_bowler","runs_off_bat","0s","1s","2s","3s","4s","6s","extras","outs_bowler","powerplay","middle","setup","death","runs/ball","0s/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","wickets/ball","ECON","SR","PP usage","mid usage","setup usage","death usage","xECON","xSR","xruns","xwickets","bb_GP"]]
player_bowl = player_bowl.dropna()

print("individual season data dumped")
now = datetime.datetime.now()
print(now.time())

#scale xruns and xwickets
s_player_bat = pd.pivot_table(player_bat,values=['runs_off_bat','outs_batsman','xruns','xwickets'],index=['season'],aggfunc=np.sum)
s_player_bat['r_scale'] = s_player_bat['runs_off_bat']/s_player_bat['xruns']
s_player_bat['w_scale'] = s_player_bat['outs_batsman']/s_player_bat['xwickets']
s_player_bat = s_player_bat.reset_index()
player_bat = player_bat.merge(s_player_bat[['season','r_scale','w_scale']], left_on='season', right_on='season')
player_bat['xruns'] = player_bat['xruns']*player_bat['r_scale']
player_bat['xwickets'] = player_bat['xwickets']*player_bat['w_scale']
player_bat['xSR'] = player_bat['xSR']*player_bat['r_scale']
player_bat['RSAA'] = 1.2*(player_bat['SR']-player_bat['xSR'])*player_bat['usage']*factor

s_player_bowl = pd.pivot_table(player_bowl,values=['runs_off_bat','extras','outs_bowler','xruns','xwickets'],index=['season'],aggfunc=np.sum)
s_player_bowl['r_scale'] = (s_player_bowl['runs_off_bat']+s_player_bowl['extras'])/s_player_bowl['xruns']
s_player_bowl['w_scale'] = s_player_bowl['outs_bowler']/s_player_bowl['xwickets']
s_player_bowl = s_player_bowl.reset_index()
player_bowl = player_bowl.merge(s_player_bowl[['season','r_scale','w_scale']], left_on='season', right_on='season')
player_bowl['xruns'] = player_bowl['xruns']*player_bowl['r_scale']
player_bowl['xwickets'] = player_bowl['xwickets']*player_bowl['w_scale']
player_bowl['xSR'] = player_bowl['xSR']/player_bowl['w_scale']
player_bowl['xECON'] = player_bowl['xECON']/player_bowl['r_scale']
player_bowl['WTAA'] = factor*120*((1/player_bowl['SR'])-(1/player_bowl['xSR']))*player_bowl['usage']
player_bowl['RCAA'] = 20*(player_bowl['ECON']-player_bowl['xECON'])*player_bowl['usage']*factor - 6*player_bowl['WTAA']*factor

player_bat = player_bat.drop(columns=['r_scale', 'w_scale'])
player_bowl = player_bowl.drop(columns=['r_scale', 'w_scale', 'WTAA'])

print("individual season xruns/wickets rescaled")
now = datetime.datetime.now()
print(now.time())

with pd.ExcelWriter(output_file) as writer:
    matchups.to_excel(writer, sheet_name="venue pace_spin", index=False)
    venue_bat_phase.to_excel(writer, sheet_name="venue batting", index=False)
    venue_bowl_phase.to_excel(writer, sheet_name="venue bowling", index=False)
    player_bat.to_excel(writer, sheet_name="batting seasons", index=False)
    player_bowl.to_excel(writer, sheet_name="bowling seasons", index=False)
    year_bat_phase.to_excel(writer, sheet_name="batting phases", index=False)
    year_bowl_phase.to_excel(writer, sheet_name="bowling phases", index=False)
    year_bat.to_excel(writer, sheet_name="batting year", index=False)
    year_bowl.to_excel(writer, sheet_name="bowling year", index=False)
  
print("all data dumped to the desired excel file, run aggregate (if you want to) then run projections")
