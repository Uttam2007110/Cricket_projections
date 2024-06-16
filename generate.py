# -*- coding: utf-8 -*-
"""
Created on Fri Nov 25 18:35:44 2022
@author: uttam ganti
converting cricsheet data into league summary tables
"""
import pandas as pd
from sys import getsizeof
import datetime
pd.options.mode.chained_assignment = None  # default='warn'

comp = 'blast'
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'

if(comp=='hundred' or comp=='hundredw'):
    p1 = 6; p2 = 12; p3 = 17; factor = (5/6);  #hundred
elif(comp=='odi' or comp=='odiw' or comp=='odiq' or comp=='rlc' or comp=='cwc'):
    p1 = 10; p2 = 26; p3 = 40; factor = 2.5;   #odi
elif(comp=='tests' or comp == 'cc' or comp == 'shield' or comp == 'testsw'):
    p1 = 30; p2 = 55; p3 = 80; factor = 11.25; #test
else:
    p1 = 6; p2 = 12; p3 = 17; factor = 1;      #assume its a t20 by default

input_file = f'{path}/raw/{comp}.csv'
input_file2 = f'{path}/raw/{comp}_GP.csv'
input_file3 = f'{path}/venues.xlsx'
output_file = f"{path}/summary/{comp}_summary.xlsx"

def unique(list1):
    # initialize a null list
    unique_list = []
    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)
    # print list
    return unique_list

file0 = pd.read_csv(input_file,sep=',',low_memory=False)
file00 = pd.read_csv(input_file2,sep=',',low_memory=False)
file000 = pd.read_excel(input_file3,'Sheet1')
file0 = file0.fillna(0)
now = datetime.datetime.now()
print(now.time())
start_size = getsizeof(file0)/(1024.0**2)
print('Dataframe size: %2.2f MB'%start_size)
#print(file0.columns.values)

c = 0
player_season = []
venues_season = []
balls_bowler = []
balls_batsman = []
dots = []
ones = []
twos = []
threes = []
fours = []
sixes = []
outs_batsman = []
outs_ns = []
outs_bowler = []
batting_team_season = []
bowling_team_season = []

for x in file0['bowler'].values:
    if(True):
        player_season.append(file0['bowler'][c] +";"+ str(file0['season'][c]))
        player_season.append(file0['striker'][c] +";"+ str(file0['season'][c]))
        venues_season.append(file0['venue'][c] +";"+ str(file0['season'][c]))
        batting_team_season.append(file0['batting_team'][c] +";"+ str(file0['season'][c]))
        bowling_team_season.append(file0['bowling_team'][c] +";"+ str(file0['season'][c]))
    
        if(file0['wides'][c] > 0): balls_batsman.append(0)
        else : balls_batsman.append(1)
    
        if(file0['wides'][c] > 0 or file0['noballs'][c] > 0): balls_bowler.append(0)
        else : balls_bowler.append(1)
    
        if(file0['runs_off_bat'][c] == 0 and file0['noballs'][c] ==0 and file0['wides'][c] == 0): dots.append(1)
        else : dots.append(0)
    
        if(file0['runs_off_bat'][c] == 1): ones.append(1)
        else : ones.append(0)
    
        if(file0['runs_off_bat'][c] == 2): twos.append(1)
        else : twos.append(0)
    
        if(file0['runs_off_bat'][c] == 3): threes.append(1)
        else : threes.append(0)
    
        if(file0['runs_off_bat'][c] == 4): fours.append(1)
        else : fours.append(0)
    
        if(file0['runs_off_bat'][c] == 6): sixes.append(1)
        else : sixes.append(0)
    
        if(file0['striker'][c] == file0['player_dismissed'][c]): outs_batsman.append(1)
        else : outs_batsman.append(0)
    
        if(file0['non_striker'][c] == file0['player_dismissed'][c]): outs_ns.append(1)
        else : outs_ns.append(0)
    
        if(file0['striker'][c] == file0['player_dismissed'][c]):
            if(file0['wicket_type'][c] == "run out" or file0['wicket_type'][c] == "retired hurt" or file0['wicket_type'][c] == "retired out" or file0['wicket_type'][c] == "obstructing the field"): 
                outs_bowler.append(0)
            else:
                outs_bowler.append(1)
        else : outs_bowler.append(0)
    
    c = c + 1
    
file0['balls_batsman'] = balls_batsman
file0['balls_bowler'] = balls_bowler
file0['dots'] = dots
file0['ones'] = ones
file0['twos'] = twos
file0['threes'] = threes
file0['fours'] = fours
file0['sixes'] = sixes
file0['outs_batsman'] = outs_batsman
file0['outs_ns'] = outs_ns
file0['outs_bowler'] = outs_bowler

venues_season = unique(venues_season)
unique_seasons = unique(file0['season'].values)
player_season = unique(player_season)
batting_team_season = unique(batting_team_season)
bowling_team_season = unique(bowling_team_season)

print(unique_seasons)
now = datetime.datetime.now()
print(now.time())
venue = unique(file0['venue'].values)

c = 0
year_bat = [["Season","Sum of balls_batsman","Sum of runs_off_bat","Sum of 0s","Sum of 1s","Sum of 2s","Sum of 3s","Sum of 4s","Sum of 6s","Sum of outs_batsman","Sum of powerplay","Sum of middle","Sum of setup","Sum of death","runs/ball","0s/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","wickets/ball","powerplay/ball","middle/ball","setup/ball","death/ball"]]
year_bowl = [["Season","Sum of balls_bowler","Sum of runs_off_bat","Sum of 0s","Sum of 1s","Sum of 2s","Sum of 3s","Sum of 4s","Sum of 6s","Sum of extras","Sum of outs_bowler","Sum of powerplay","Sum of middle","Sum of setup","Sum of death","runs/ball","0s/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","wickets/ball","powerplay/ball","middle/ball","setup/ball","death/ball"]]
year_bat_phase = [["Season","Sum of powerplay","Sum of pp_runs_batsman","Sum of pp_wickets_batsman","Sum of middle","Sum of mid_runs_batsman","Sum of mid_wickets_batsman","Sum of setup","Sum of setup_runs_batsman","Sum of setup_wickets_batsman","Sum of death","Sum of death_runs_batsman","Sum of death_wickets_batsman","pp AVG","mid AVG","setup AVG","death AVG","pp SR","mid SR","setup SR","death SR"]]
year_bowl_phase = [["Season","Sum of powerplay","Sum of pp_runs_bowler","Sum of pp_wickets_bowler","Sum of middle","Sum of mid_runs_bowler","Sum of mid_wickets_bowler","Sum of setup","Sum of setup_runs_bowler","Sum of setup_wickets_bowler","Sum of death","Sum of death_runs_bowler","Sum of death_wickets_bowler","pp ECON","mid ECON","setup ECON","death ECON","pp SR","mid SR","setup SR","death SR"]]
batting_team_balls_season = []; bowling_team_balls_season = []
venue_bat_phase = [["Venue","Season","Sum of powerplay","Sum of pp_runs_batsman","Sum of pp_wickets_batsman","Sum of middle","Sum of mid_runs_batsman","Sum of mid_wickets_batsman","Sum of setup","Sum of setup_runs_batsman","Sum of setup_wickets_batsman","Sum of death","Sum of death_runs_batsman","Sum of death_wickets_batsman","pp AVG","mid AVG","setup AVG","death AVG","pp SR","mid SR","setup SR","death SR"]]
venue_bowl_phase = [["Venue","Season","Sum of powerplay","Sum of pp_runs_bowler","Sum of pp_wickets_bowler","Sum of middle","Sum of mid_runs_bowler","Sum of mid_wickets_bowler","Sum of setup","Sum of setup_runs_bowler","Sum of setup_wickets_bowler","Sum of death","Sum of death_runs_bowler","Sum of death_wickets_bowler","pp ECON","mid ECON","setup ECON","death ECON","pp SR","mid SR","setup SR","death SR"]]


for r in batting_team_season:
    c7 = 0; vals1 = 0; vals2 = 0
    #vals1 = file0['balls_batsman'].sum()
    a = r.split(";")[0]
    b = int(r.split(";")[1])
    vals1 = file0.loc[(file0['batting_team']==a)&(file0['season']==b),'balls_batsman'].sum()
    vals2 = file0.loc[(file0['bowling_team']==a)&(file0['season']==b),'balls_bowler'].sum()
    batting_team_balls_season.append([a,b,vals1])
    bowling_team_balls_season.append([a,b,vals2])
    now = datetime.datetime.now()
    #print(a,b,now.time())

print("team balls faced dumped")
now = datetime.datetime.now()
print(now.time())

for x in unique_seasons:
    
    year_balls_bowl = file0.loc[(file0['season']==x),'balls_bowler'].sum()
    year_runs_bowl = file0.loc[(file0['season']==x),'runs_off_bat'].sum() + file0.loc[(file0['season']==x),'extras'].sum()
    year_zeros_bowl = file0.loc[(file0['season']==x),'dots'].sum()
    year_ones_bowl = file0.loc[(file0['season']==x),'ones'].sum()
    year_twos_bowl = file0.loc[(file0['season']==x),'twos'].sum()
    year_threes_bowl = file0.loc[(file0['season']==x),'threes'].sum()
    year_fours_bowl = file0.loc[(file0['season']==x),'fours'].sum()
    year_sixes_bowl = file0.loc[(file0['season']==x),'sixes'].sum()
    year_extras_bowl = file0.loc[(file0['season']==x),'extras'].sum()
    year_wickets_bowl = file0.loc[(file0['season']==x),'outs_bowler'].sum()
    
    year_pp_bowl = file0.loc[(file0['season']==x)&(file0['ball']<p1),'balls_bowler'].sum()
    year_ppr_bowl = file0.loc[(file0['season']==x)&(file0['ball']<p1),'runs_off_bat'].sum() + file0.loc[(file0['season']==x)&(file0['ball']<p1),'extras'].sum()
    year_ppw_bowl = file0.loc[(file0['season']==x)&(file0['ball']<p1),'outs_bowler'].sum()   
    year_mid_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'balls_bowler'].sum()
    year_midr_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'runs_off_bat'].sum() + file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'extras'].sum()
    year_midw_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'outs_bowler'].sum()   
    year_setup_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'balls_bowler'].sum()
    year_setupr_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'runs_off_bat'].sum() + file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'extras'].sum()
    year_setupw_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'outs_bowler'].sum()    
    year_death_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p3),'balls_bowler'].sum()
    year_deathr_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p3),'runs_off_bat'].sum() + file0.loc[(file0['season']==x)&(file0['ball']>p3),'extras'].sum()
    year_deathw_bowl = file0.loc[(file0['season']==x)&(file0['ball']>p3),'outs_bowler'].sum()
    
    year_balls_bat = file0.loc[(file0['season']==x),'balls_batsman'].sum()
    year_runs_bat = file0.loc[(file0['season']==x),'runs_off_bat'].sum()
    year_zeros_bat = file0.loc[(file0['season']==x),'dots'].sum()
    year_ones_bat = file0.loc[(file0['season']==x),'ones'].sum()
    year_twos_bat = file0.loc[(file0['season']==x),'twos'].sum()
    year_threes_bat = file0.loc[(file0['season']==x),'threes'].sum()
    year_fours_bat = file0.loc[(file0['season']==x),'fours'].sum()
    year_sixes_bat = file0.loc[(file0['season']==x),'sixes'].sum()
    year_extras_bat = file0.loc[(file0['season']==x),'extras'].sum()
    year_wickets_bat = file0.loc[(file0['season']==x),'outs_batsman'].sum() + file0.loc[(file0['season']==x),'outs_ns'].sum()
    
    year_pp_bat = file0.loc[(file0['season']==x)&(file0['ball']<p1),'balls_batsman'].sum()
    year_ppr_bat = file0.loc[(file0['season']==x)&(file0['ball']<p1),'runs_off_bat'].sum()
    year_ppw_bat = file0.loc[(file0['season']==x)&(file0['ball']<p1),'outs_batsman'].sum() + file0.loc[(file0['season']==x)&(file0['ball']<p1),'outs_ns'].sum()  
    year_mid_bat = file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'balls_batsman'].sum()
    year_midr_bat = file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'runs_off_bat'].sum()
    year_midw_bat = file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'outs_batsman'].sum() + file0.loc[(file0['season']==x)&(file0['ball']>p1)&(file0['ball']<p2),'outs_ns'].sum()   
    year_setup_bat = file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'balls_batsman'].sum()
    year_setupr_bat = file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'runs_off_bat'].sum()
    year_setupw_bat = file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'outs_batsman'].sum() + file0.loc[(file0['season']==x)&(file0['ball']>p2)&(file0['ball']<p3),'outs_ns'].sum()   
    year_death_bat = file0.loc[(file0['season']==x)&(file0['ball']>p3),'balls_batsman'].sum()
    year_deathr_bat = file0.loc[(file0['season']==x)&(file0['ball']>p3),'runs_off_bat'].sum()
    year_deathw_bat = file0.loc[(file0['season']==x)&(file0['ball']>p3),'outs_batsman'].sum() + file0.loc[(file0['season']==x)&(file0['ball']>p3),'outs_ns'].sum()
   
    year_bowl.append([x,year_balls_bowl,year_runs_bowl,year_zeros_bowl,year_ones_bowl,year_twos_bowl,year_threes_bowl,year_fours_bowl,year_sixes_bowl,year_extras_bowl,year_wickets_bowl,year_pp_bowl,year_mid_bowl,year_setup_bowl,year_death_bowl,year_runs_bowl/year_balls_bowl,year_zeros_bowl/year_balls_bowl,year_ones_bowl/year_balls_bowl,year_twos_bowl/year_balls_bowl,year_threes_bowl/year_balls_bowl,year_fours_bowl/year_balls_bowl,year_sixes_bowl/year_balls_bowl,year_extras_bowl/year_balls_bowl,year_wickets_bowl/year_balls_bowl,year_pp_bowl/year_balls_bowl,year_mid_bowl/year_balls_bowl,year_setup_bowl/year_balls_bowl,year_death_bowl/year_balls_bowl])
    year_bat.append([x,year_balls_bat,year_runs_bat,year_zeros_bat,year_ones_bat,year_twos_bat,year_threes_bat,year_fours_bat,year_sixes_bat,year_wickets_bat,year_pp_bat,year_mid_bat,year_setup_bat,year_death_bat,year_runs_bat/year_balls_bat,year_zeros_bat/year_balls_bat,year_ones_bat/year_balls_bat,year_twos_bat/year_balls_bat,year_threes_bat/year_balls_bat,year_fours_bat/year_balls_bat,year_sixes_bat/year_balls_bat,year_wickets_bat/year_balls_bat,year_pp_bat/year_balls_bat,year_mid_bat/year_balls_bat,year_setup_bat/year_balls_bat,year_death_bat/year_balls_bat])
    year_bat_phase.append([x,year_pp_bat,year_ppr_bat,year_ppw_bat,year_mid_bat,year_midr_bat,year_midw_bat,year_setup_bat,year_setupr_bat,year_setupw_bat,year_death_bat,year_deathr_bat,year_deathw_bat,year_pp_bat/year_ppw_bat,year_mid_bat/year_midw_bat,year_setup_bat/year_setupw_bat,year_death_bat/year_deathw_bat,100*year_ppr_bat/year_pp_bat,100*year_midr_bat/year_mid_bat,100*year_setupr_bat/year_setup_bat,100*year_deathr_bat/year_death_bat])
    year_bowl_phase.append([x,year_pp_bowl,year_ppr_bowl,year_ppw_bowl,year_mid_bowl,year_midr_bowl,year_midw_bowl,year_setup_bowl,year_setupr_bowl,year_setupw_bowl,year_death_bowl,year_deathr_bowl,year_deathw_bowl,6*year_ppr_bowl/year_pp_bowl,6*year_midr_bowl/year_mid_bowl,6*year_setupr_bowl/year_setup_bowl,6*year_deathr_bowl/year_death_bowl,year_pp_bowl/year_ppw_bowl,year_mid_bowl/year_midw_bowl,year_setup_bowl/year_setupw_bowl,year_death_bowl/year_deathw_bowl])

print("league average and phases data dumped")
now = datetime.datetime.now()
print(now.time())

for x in venues_season:
    a = x.split(";")[0]         #venue
    b = int(x.split(";")[1])    #season
    try:
        a2 = file000.loc[file000['venue']==a,'short'].values[0]
    except IndexError:
        a2 = a
    
    year_pp_bowl = file0.loc[(file0['season']==b)&(file0['ball']<p1),'balls_bowler'].sum()
    year_ppr_bowl = file0.loc[(file0['season']==b)&(file0['ball']<p1),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['ball']<p1),'extras'].sum()
    year_ppw_bowl = file0.loc[(file0['season']==b)&(file0['ball']<p1),'outs_bowler'].sum()   
    year_mid_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'balls_bowler'].sum()
    year_midr_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'extras'].sum()
    year_midw_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'outs_bowler'].sum()   
    year_setup_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'balls_bowler'].sum()
    year_setupr_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'extras'].sum()
    year_setupw_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'outs_bowler'].sum()    
    year_death_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p3),'balls_bowler'].sum()
    year_deathr_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p3),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['ball']>p3),'extras'].sum()
    year_deathw_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p3),'outs_bowler'].sum()
    
    venue_pp_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'balls_bowler'].sum()
    venue_ppr_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'extras'].sum()
    venue_ppw_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'outs_bowler'].sum()
    venue_mid_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'balls_bowler'].sum()
    venue_midr_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'extras'].sum()
    venue_midw_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'outs_bowler'].sum()
    venue_setup_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'balls_bowler'].sum()
    venue_setupr_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'extras'].sum()
    venue_setupw_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'outs_bowler'].sum()    
    venue_death_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'balls_bowler'].sum()
    venue_deathr_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'extras'].sum()
    venue_deathw_bowl = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'outs_bowler'].sum()
    
    year_pp_bat = file0.loc[(file0['season']==b)&(file0['ball']<p1),'balls_batsman'].sum()
    year_ppr_bat = file0.loc[(file0['season']==b)&(file0['ball']<p1),'runs_off_bat'].sum()
    year_ppw_bat = file0.loc[(file0['season']==b)&(file0['ball']<p1),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['ball']<p1),'outs_ns'].sum()  
    year_mid_bat = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'balls_batsman'].sum()
    year_midr_bat = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'runs_off_bat'].sum()
    year_midw_bat = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2),'outs_ns'].sum()   
    year_setup_bat = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'balls_batsman'].sum()
    year_setupr_bat = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'runs_off_bat'].sum()
    year_setupw_bat = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3),'outs_ns'].sum()   
    year_death_bat = file0.loc[(file0['season']==b)&(file0['ball']>p3),'balls_batsman'].sum()
    year_deathr_bat = file0.loc[(file0['season']==b)&(file0['ball']>p3),'runs_off_bat'].sum()
    year_deathw_bat = file0.loc[(file0['season']==b)&(file0['ball']>p3),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['ball']>p3),'outs_ns'].sum()

    venue_pp_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'balls_batsman'].sum()
    venue_ppr_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'runs_off_bat'].sum()
    venue_ppw_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']<p1),'outs_ns'].sum()    
    venue_mid_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'balls_batsman'].sum()
    venue_midr_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'runs_off_bat'].sum()
    venue_midw_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p1)&(file0['ball']<p2),'outs_ns'].sum()
    venue_setup_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'balls_batsman'].sum()
    venue_setupr_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'runs_off_bat'].sum()
    venue_setupw_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p2)&(file0['ball']<p3),'outs_ns'].sum()
    venue_death_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'balls_batsman'].sum()
    venue_deathr_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'runs_off_bat'].sum()
    venue_deathw_bat = file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['venue']==a)&(file0['ball']>p3),'outs_ns'].sum()
    
    #now = datetime.datetime.now()
    #print(a,b,now.time())
    #venue_bowl.append([a,b,venue_balls_bowl,venue_runs_bowl,venue_zeros_bowl,venue_ones_bowl,venue_twos_bowl,venue_threes_bowl,venue_fours_bowl,venue_sixes_bowl,venue_extras_bowl,venue_wickets_bowl,venue_pp_bowl,venue_mid_bowl,venue_setup_bowl,venue_death_bowl,venue_runs_bowl/venue_balls_bowl,venue_zeros_bowl/venue_balls_bowl,venue_ones_bowl/venue_balls_bowl,venue_twos_bowl/venue_balls_bowl,venue_threes_bowl/venue_balls_bowl,venue_fours_bowl/venue_balls_bowl,venue_sixes_bowl/venue_balls_bowl,venue_extras_bowl/venue_balls_bowl,venue_wickets_bowl/venue_balls_bowl,venue_pp_bowl/venue_balls_bowl,venue_mid_bowl/venue_balls_bowl,venue_setup_bowl/venue_balls_bowl,venue_death_bowl/venue_balls_bowl])
    #venue_bat.append([a,b,venue_balls_bat,venue_runs_bat,venue_zeros_bat,venue_ones_bat,venue_twos_bat,venue_threes_bat,venue_fours_bat,venue_sixes_bat,venue_wickets_bat,venue_pp_bat,venue_mid_bat,venue_setup_bat,venue_death_bat,venue_runs_bat/venue_balls_bat,venue_zeros_bat/venue_balls_bat,venue_ones_bat/venue_balls_bat,venue_twos_bat/venue_balls_bat,venue_threes_bat/venue_balls_bat,venue_fours_bat/venue_balls_bat,venue_sixes_bat/venue_balls_bat,venue_wickets_bat/venue_balls_bat,venue_pp_bat/venue_balls_bat,venue_mid_bat/venue_balls_bat,venue_setup_bat/venue_balls_bat,venue_death_bat/venue_balls_bat])
    venue_bat_phase.append([a2,b,venue_pp_bat,venue_ppr_bat,venue_ppw_bat,venue_mid_bat,venue_midr_bat,venue_midw_bat,venue_setup_bat,venue_setupr_bat,venue_setupw_bat,venue_death_bat,venue_deathr_bat,venue_deathw_bat,venue_pp_bat/venue_ppw_bat,venue_mid_bat/venue_midw_bat,venue_setup_bat/venue_setupw_bat,venue_death_bat/venue_deathw_bat,100*venue_ppr_bat/venue_pp_bat,100*venue_midr_bat/venue_mid_bat,100*venue_setupr_bat/venue_setup_bat,100*venue_deathr_bat/venue_death_bat])
    venue_bowl_phase.append([a2,b,venue_pp_bowl,venue_ppr_bowl,venue_ppw_bowl,venue_mid_bowl,venue_midr_bowl,venue_midw_bowl,venue_setup_bowl,venue_setupr_bowl,venue_setupw_bowl,venue_death_bowl,venue_deathr_bowl,venue_deathw_bowl,6*venue_ppr_bowl/venue_pp_bowl,6*venue_midr_bowl/venue_mid_bowl,6*venue_setupr_bowl/venue_setup_bowl,6*venue_deathr_bowl/venue_death_bowl,venue_pp_bowl/venue_ppw_bowl,venue_mid_bowl/venue_midw_bowl,venue_setup_bowl/venue_setupw_bowl,venue_death_bowl/venue_deathw_bowl])

print("venue average and phases data dumped")
now = datetime.datetime.now()
print(now.time())

player_bat = [["batsman","season","batting_team","RSAA","usage","balls_batsman","runs_off_bat","0s","1s","2s","3s","4s","6s","outs_batsman","powerplay","middle","setup","death","runs/ball","0s/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","wickets/ball","PP usage","mid usage","setup usage","death usage","AVG","SR","xAVG","xSR","xruns","xwickets","bf_GP"]]
player_bowl = [["bowler","season","bowling_team","RCAA","usage","balls_bowler","runs_off_bat","0s","1s","2s","3s","4s","6s","extras","outs_bowler","powerplay","middle","setup","death","runs/ball","0s/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","wickets/ball","ECON","SR","PP usage","mid usage","setup usage","death usage","xECON","xSR","xruns","xwickets","bb_GP"]]

def league_stats(sssss,pp,mid,setup,death,bowl_sr,bowl_econ,bat_sr,bat_avg):
    c8 = 0; v = 0
    for b in year_bat_phase:
        if(year_bat_phase[c8][0] == sssss and bat_sr == 1): 
            v = year_bat_phase[c8][17]*pp + year_bat_phase[c8][18]*mid + year_bat_phase[c8][19]*setup + year_bat_phase[c8][20]*death
        if(year_bat_phase[c8][0] == sssss and bat_avg == 1): 
            v = year_bat_phase[c8][13]*pp + year_bat_phase[c8][14]*mid + year_bat_phase[c8][15]*setup + year_bat_phase[c8][16]*death    
        if(year_bowl_phase[c8][0] == sssss and bowl_econ == 1): 
            v = year_bowl_phase[c8][13]*pp + year_bowl_phase[c8][14]*mid + year_bowl_phase[c8][15]*setup + year_bowl_phase[c8][16]*death
        if(year_bowl_phase[c8][0] == sssss and bowl_sr == 1): 
            v = year_bowl_phase[c8][17]*pp + year_bowl_phase[c8][18]*mid + year_bowl_phase[c8][19]*setup + year_bowl_phase[c8][20]*death
        c8 = c8 + 1
    return v

print("individual season data started")

for x in player_season:
    a = x.split(";")[0]
    b = int(x.split(";")[1])
    
    year_gp = file00.loc[(file00['season']==b)&(file00['player']==a),'GP'].sum()
    year_balls_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'balls_bowler'].sum() + 0.00000000001
    year_runs_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'runs_off_bat'].sum() + file0.loc[(file0['season']==b)&(file0['bowler']==a),'extras'].sum()
    year_zeros_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'dots'].sum()
    year_ones_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'ones'].sum()
    year_twos_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'twos'].sum()
    year_threes_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'threes'].sum()
    year_fours_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'fours'].sum()
    year_sixes_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'sixes'].sum()
    year_extras_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'extras'].sum()
    year_wickets_bowl = file0.loc[(file0['season']==b)&(file0['bowler']==a),'outs_bowler'].sum()
    
    year_pp_bowl = file0.loc[(file0['season']==b)&(file0['ball']<p1)&(file0['bowler']==a),'balls_bowler'].sum()
    year_mid_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2)&(file0['bowler']==a),'balls_bowler'].sum()
    year_setup_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3)&(file0['bowler']==a),'balls_bowler'].sum()
    year_death_bowl = file0.loc[(file0['season']==b)&(file0['ball']>p3)&(file0['bowler']==a),'balls_bowler'].sum()
    
    try : team0 = file0[(file0.season==b)&(file0.bowler==a)].iloc[0][7]
    except IndexError: team0 = "Free Agent"
    usage_bowl = year_balls_bowl/(0.0000001+file0.loc[(file0['bowling_team']==team0)&(file0['season']==b),'balls_bowler'].sum())
    usage_bowl = year_balls_bowl/(0.0000001+(file00.loc[(file00['player']==team0)&(file00['season']==b),'GP']*120*factor).sum())
    ECON = 6*year_runs_bowl/(year_balls_bowl)
    if(year_wickets_bowl >= 1):SR_bowl = year_balls_bowl/year_wickets_bowl
    else: SR_bowl = year_balls_bowl
    xECON = league_stats(b,year_pp_bowl/year_balls_bowl,year_mid_bowl/year_balls_bowl,year_setup_bowl/year_balls_bowl,year_death_bowl/year_balls_bowl,0,1,0,0)
    xSR_bowl = league_stats(b,year_pp_bowl/year_balls_bowl,year_mid_bowl/year_balls_bowl,year_setup_bowl/year_balls_bowl,year_death_bowl/year_balls_bowl,1,0,0,0)
    xruns_bowl = (xECON * year_balls_bowl)/6
    xwickets_bowl = year_balls_bowl/xSR_bowl
    RCAA = 20*(ECON-xECON)*usage_bowl*factor
    
    year_balls_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'balls_batsman'].sum() + 0.000000000001
    year_runs_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'runs_off_bat'].sum()
    year_zeros_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'dots'].sum()
    year_ones_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'ones'].sum()
    year_twos_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'twos'].sum()
    year_threes_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'threes'].sum()
    year_fours_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'fours'].sum()
    year_sixes_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'sixes'].sum()
    year_extras_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'extras'].sum()
    year_wickets_bat = file0.loc[(file0['season']==b)&(file0['striker']==a),'outs_batsman'].sum() + file0.loc[(file0['season']==b)&(file0['non_striker']==a),'outs_ns'].sum()
    
    year_pp_bat = file0.loc[(file0['season']==b)&(file0['ball']<p1)&(file0['striker']==a),'balls_batsman'].sum()
    year_mid_bat = file0.loc[(file0['season']==b)&(file0['ball']>p1)&(file0['ball']<p2)&(file0['striker']==a),'balls_batsman'].sum()
    year_setup_bat = file0.loc[(file0['season']==b)&(file0['ball']>p2)&(file0['ball']<p3)&(file0['striker']==a),'balls_batsman'].sum()
    year_death_bat = file0.loc[(file0['season']==b)&(file0['ball']>p3)&(file0['striker']==a),'balls_batsman'].sum()
   
    try : team1 = file0[(file0.season==b)&(file0.striker==a)].iloc[0][6]
    except IndexError: team1 = "Free Agent"
    usage = year_balls_bat/(0.00000001+file0.loc[(file0['batting_team']==team1)&(file0['season']==b),'balls_batsman'].sum())
    usage = year_balls_bat/(0.00000001+(file00.loc[(file00['player']==team1)&(file00['season']==b),'GP']*120*factor).sum())
    SR = 100*year_runs_bat/(year_balls_bat)
    if(year_wickets_bat >= 1): AVG = year_balls_bat/year_wickets_bat 
    else: AVG = year_balls_bat
    xAVG = league_stats(b,year_pp_bat/year_balls_bat,year_mid_bat/year_balls_bat,year_setup_bat/year_balls_bat,year_death_bat/year_balls_bat,0,0,0,1)
    xSR = league_stats(b,year_pp_bat/year_balls_bat,year_mid_bat/year_balls_bat,year_setup_bat/year_balls_bat,year_death_bat/year_balls_bat,0,0,1,0)
    xruns = year_balls_bat*xSR/100
    xwickets = year_balls_bat/xAVG
    RSAA = 1.2*(SR-xSR)*usage*factor
    
    if(year_balls_bowl >= 1): player_bowl.append([a,b,team0,RCAA,usage_bowl,year_balls_bowl,year_runs_bowl,year_zeros_bowl,year_ones_bowl,year_twos_bowl,year_threes_bowl,year_fours_bowl,year_sixes_bowl,year_extras_bowl,year_wickets_bowl,year_pp_bowl,year_mid_bowl,year_setup_bowl,year_death_bowl,year_runs_bowl/year_balls_bowl,year_zeros_bowl/year_balls_bowl,year_ones_bowl/year_balls_bowl,year_twos_bowl/year_balls_bowl,year_threes_bowl/year_balls_bowl,year_fours_bowl/year_balls_bowl,year_sixes_bowl/year_balls_bowl,year_extras_bowl/year_balls_bowl,year_wickets_bowl/year_balls_bowl,ECON,SR_bowl,year_pp_bowl/year_balls_bowl,year_mid_bowl/year_balls_bowl,year_setup_bowl/year_balls_bowl,year_death_bowl/year_balls_bowl,xECON,xSR_bowl,xruns_bowl,xwickets_bowl,year_balls_bowl/year_gp])
    if(year_balls_bat >= 1): player_bat.append([a,b,team1,RSAA,usage,year_balls_bat,year_runs_bat,year_zeros_bat,year_ones_bat,year_twos_bat,year_threes_bat,year_fours_bat,year_sixes_bat,year_wickets_bat,year_pp_bat,year_mid_bat,year_setup_bat,year_death_bat,year_runs_bat/year_balls_bat,year_zeros_bat/year_balls_bat,year_ones_bat/year_balls_bat,year_twos_bat/year_balls_bat,year_threes_bat/year_balls_bat,year_fours_bat/year_balls_bat,year_sixes_bat/year_balls_bat,year_wickets_bat/year_balls_bat,year_pp_bat/year_balls_bat,year_mid_bat/year_balls_bat,year_setup_bat/year_balls_bat,year_death_bat/year_balls_bat,AVG,SR,xAVG,xSR,xruns,xwickets,year_balls_bat/year_gp])
    now = datetime.datetime.now()
    
    print(b,a,now.time())

print("individual season data dumped")
now = datetime.datetime.now()
print(now.time())

def dumps():
    lol = pd.DataFrame(year_bowl)
    lol.columns = lol.iloc[0];lol = lol.drop(0)
    lol2 = pd.DataFrame(year_bat)
    lol2.columns = lol2.iloc[0];lol2 = lol2.drop(0)
    lol3 = pd.DataFrame(year_bowl_phase)
    lol3.columns = lol3.iloc[0];lol3 = lol3.drop(0)
    lol4 = pd.DataFrame(year_bat_phase)
    lol4.columns = lol4.iloc[0];lol4 = lol4.drop(0)
    lol5 = pd.DataFrame(player_bowl)
    lol5.columns = lol5.iloc[0];lol5 = lol5.drop(0)
    lol6 = pd.DataFrame(player_bat)
    lol6.columns = lol6.iloc[0];lol6 = lol6.drop(0)
    lol7 = pd.DataFrame(venue_bowl_phase)
    lol7.columns = lol7.iloc[0];lol7 = lol7.drop(0)
    lol8 = pd.DataFrame(venue_bat_phase)
    lol8.columns = lol8.iloc[0];lol8 = lol8.drop(0)
    with pd.ExcelWriter(output_file) as writer:
        lol8.to_excel(writer, sheet_name="venue batting", index=False)
        lol7.to_excel(writer, sheet_name="venue bowling", index=False)
        lol6.to_excel(writer, sheet_name="batting seasons", index=False)
        lol5.to_excel(writer, sheet_name="bowling seasons", index=False)
        lol4.to_excel(writer, sheet_name="batting phases", index=False)
        lol3.to_excel(writer, sheet_name="bowling phases", index=False)
        lol2.to_excel(writer, sheet_name="batting year", index=False)
        lol.to_excel(writer, sheet_name="bowling year", index=False)
        
    print("all data dumped to the desired excel file, run aggregate if you want to then run projections")
        
dumps()
