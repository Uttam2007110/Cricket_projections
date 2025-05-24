# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 19:25:55 2022
author: uttam ganti
projecting league performances based on past seasons
"""
import numpy as np
import pandas as pd
import math
from datetime import datetime
from itertools import product
from usage import *
pd.options.mode.chained_assignment = None  # default='warn'
np.seterr(divide='ignore', invalid='ignore')
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

comp = 'blast'
proj_year = 2026   #year+1 of the season you want projections for
aggregate = 0
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'

if(comp=='hundred' or comp=='hundredw'):
    factor = (5/6); aggregate = 1 #hundred
elif(comp=='odi' or comp=='odiq' or comp=='odiw' or comp=='rlc' or comp=='rhf'):
    factor = 2.5; aggregate = 1  #odi
elif(comp=='tests' or comp == 'cc' or comp == 'shield' or comp == 'pks' or comp == 'testsw'):
    factor = 11.25; aggregate = 1 #test
elif(comp=='t20iq'):
    factor = 1; aggregate = 0 #international t20 qualifiers
elif(comp=='cwc'):
    factor = 2.5; aggregate = 0 #old ODIs
else:
    factor = 1; aggregate = 1 #assume its a t20 league by default
  
if(aggregate == 1): input_file = f'{path}/summary/{comp}_aggregate.xlsx' # aggregated summary
else: input_file = f'{path}/summary/{comp}_summary.xlsx' # the output of generate.py
dumps_file = f"{path}/projections/{comp}_comps.xlsx"
output_file = f"{path}/projections/{comp}_projections.xlsx"

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

#now = datetime.datetime.now()
#print(now.time())
print(f"{comp} projections started")

#file0 = pd.read_excel(input_file,'Sheet1')
file = pd.read_excel(input_file,'bowling seasons')
file2 = pd.read_excel(input_file,'bowling year')
file3 = pd.read_excel(input_file,'batting seasons')
file4 = pd.read_excel(input_file,'batting year')
proxy_bowl = []; proxy_bat = []

for (x,y) in zip(file['bowler'].values,file['season'].values): proxy_bowl.append(18+math.sqrt(file.loc[(file['bowler']==x)&(file['season']<y),'balls_bowler'].sum())/5)
for (x,y) in zip(file3['batsman'].values,file3['season'].values): proxy_bat.append(18+math.sqrt(file3.loc[(file3['batsman']==x)&(file3['season']<y),'balls_batsman'].sum())/5)

file['age_proxy'] = proxy_bowl
file3['age_proxy'] = proxy_bat
name0 = file['bowler'].values
unique_names = unique(name0)
name00 = file3['batsman'].values
unique_names2 = unique(name00)

def player_aging(batting,bowling,proj_year):
    missing = []
    #reference = pd.read_csv(f'{path}/excel/people.csv',sep=',',low_memory=False,encoding='latin-1')
    reference = pd.read_excel(f'{path}/excel/people.xlsx','people')
    print("Player DOBs collected")
    for y0 in batting.values:
        try: 
            p_dob = reference.loc[reference['unique_name']==y0[0],'dob'].sum()
            p_age = int((datetime(y0[1],4,1) - p_dob).days/365)
        except TypeError: 
            p_age = 28; missing.append(y0[0])
        batting.loc[(batting['batsman']==y0[0])&(batting['season']==y0[1]),'dots/ball'] += 0.000966*p_age + 0.058436*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) - 0.02771
        batting.loc[(batting['batsman']==y0[0])&(batting['season']==y0[1]),'1s/ball'] += -0.00072866*p_age - 0.038869*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) + 0.023522
        batting.loc[(batting['batsman']==y0[0])&(batting['season']==y0[1]),'2s/ball'] += -0.00012862*p_age + 0.009251*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) + 0.017422
        batting.loc[(batting['batsman']==y0[0])&(batting['season']==y0[1]),'4s/ball'] += 0.000071548*p_age - 0.026967*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) - 0.001723
        batting.loc[(batting['batsman']==y0[0])&(batting['season']==y0[1]),'6s/ball'] += -0.000094568*p_age + 0.005449*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) - 0.001363
        batting.loc[(batting['batsman']==y0[0])&(batting['season']==y0[1]),'wickets/ball'] += 0.000277347*p_age + 0.010306*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) - 0.007334
        
    for y00 in bowling.values:        
        try:
            p_dob = reference.loc[reference['unique_name']==y00[0],'dob'].sum()
            p_age = int((datetime(y00[1],4,1) - p_dob).days/365)
        except TypeError: 
            p_age = 28; missing.append(y00[0])
        bowling.loc[(bowling['bowler']==y00[0])&(bowling['season']==y00[1]),'dots/ball'] += -0.00007606*p_age + 0.172822*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) - 0.01640
        bowling.loc[(bowling['bowler']==y00[0])&(bowling['season']==y00[1]),'1s/ball'] += 0.000013308*p_age - 0.0720761*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) + 0.005167
        bowling.loc[(bowling['bowler']==y00[0])&(bowling['season']==y00[1]),'2s/ball'] += 0.000051438*p_age - 0.0774087*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) + 0.003987
        bowling.loc[(bowling['bowler']==y00[0])&(bowling['season']==y00[1]),'4s/ball'] += 0.000010719*p_age - 0.0235676*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) + 0.003424
        bowling.loc[(bowling['bowler']==y00[0])&(bowling['season']==y00[1]),'6s/ball'] += 0.000003777*p_age + 0.0060524*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) + 0.003439
        bowling.loc[(bowling['bowler']==y00[0])&(bowling['season']==y00[1]),'wickets/ball'] += 0.000112113*p_age + 0.0158677*(math.exp(-0.5*pow((p_age-28)/2,2)))/(5*math.sqrt(2*3.14)) - 0.005956
        
    batting['runs/ball'] = batting['1s/ball']+2*batting['2s/ball']+3*batting['3s/ball']+4*batting['4s/ball']+6*batting['6s/ball']
    batting['SR'] = 100*batting['runs/ball']
    batting['balls/wkt'] = 1/batting['wickets/ball']
    
    bowling['runs/ball'] = bowling['1s/ball']+2*bowling['2s/ball']+3*bowling['3s/ball']+4*bowling['4s/ball']+6*bowling['6s/ball']+bowling['extras/ball']
    bowling['ECON'] = 6*bowling['runs/ball']
    bowling['SR'] = 1/bowling['wickets/ball']
    missing = set(missing)
    missing = list(missing)
    return (batting,bowling,missing)

def mdist(df,v,p):
    proxy1 = 18+math.sqrt(df.loc[(df['bowler']==v[0])&(df['season']<v[1]),'balls_bowler'].sum())/5
    v_adj = v[4:6]+v[7:11]+v[3:4]+[proxy1]
    #print(v_adj)
    names = df['bowler'].values
    year = df['season'].values
    team = df['bowling_team'].values
    wickets = df['wickets/ball'].values
    #balls = df['balls_bowler'].values
    runs = df['runs/ball'].values
    dots = df['0s/ball'].values
    ones = df['1s/ball'].values
    twos = df['2s/ball'].values
    threes = df['3s/ball'].values
    fours = df['4s/ball'].values
    sixes = df['6s/ball'].values
    extras = df['extras/ball'].values
    ECON = df['ECON'].values
    SR = df['SR'].values
    xECON = df['xECON'].values
    xSR = df['xSR'].values
    PP_usage = df['PP usage'].values
    mid_usage = df['mid usage'].values
    setup_usage = df['setup usage'].values
    death_usage = df['death usage'].values
    usage = df['usage'].values
    proxy0 = df['age_proxy'].values
    
    data = np.array([ECON,SR,PP_usage,mid_usage,setup_usage,death_usage,usage,proxy0])    
    cov_matrix = np.cov(data,bias=True)
    inv_cov_matrix = np.linalg.inv(cov_matrix)
    c = 0; distance = 0;
    comps = [["bowler","season","team","Similarity","usage","ECON","SR","wickets","pp usage","mid usage","setup usage","death usage","runs","dots","ones","twos","threes","fours","sixes","extras","xECON","xSR"]]
    for x in ECON:
        proxy2 = df.loc[(df['bowler']==names[c])&(df['season']==year[c]),'age_proxy'].sum()
        v2 = np.array([ECON[c],SR[c],PP_usage[c],mid_usage[c],setup_usage[c],death_usage[c],usage[c],proxy2])
        vdiff = v2-v_adj
        distance = (np.sqrt(abs(np.matmul(np.matmul(vdiff,inv_cov_matrix),vdiff.transpose()))))
        score = 1/(1+distance)
        if(p != names[c] and year[c] > year.min()):
            comps.append([names[c],year[c],team[c],score,usage[c],ECON[c],SR[c],wickets[c],PP_usage[c],mid_usage[c],setup_usage[c],death_usage[c],runs[c],dots[c],ones[c],twos[c],threes[c],fours[c],sixes[c],extras[c],xECON[c],xSR[c]])
        c = c + 1
    return comps

def mdist_bat(df,v,p):
    proxy1 = 18+math.sqrt(df.loc[(df['batsman']==v[0])&(df['season']<v[1]),'balls_batsman'].sum())/5
    v_adj = v[4:6]+v[8:12]+v[3:4]+[proxy1]
    names = df['batsman'].values
    year = df['season'].values
    team = df['batting_team'].values
    usage = df['usage'].values
    wickets = df['wickets/ball'].values
    PP_usage = df['PP usage'].values
    mid_usage = df['mid usage'].values
    setup_usage = df['setup usage'].values
    death_usage = df['death usage'].values
    #balls = df['balls_batsman'].values
    runs = df['runs/ball'].values
    dots = df['0s/ball'].values
    ones = df['1s/ball'].values
    twos = df['2s/ball'].values
    threes = df['3s/ball'].values
    fours = df['4s/ball'].values
    sixes = df['6s/ball'].values
    #extras = df['extras/ball'].values
    xAVG = df['xAVG'].values
    xSR = df['xSR'].values
    AVG = df['AVG'].values
    SR = df['SR'].values
    proxy0 = df['age_proxy'].values
    
    data = np.array([AVG,SR,PP_usage,mid_usage,setup_usage,death_usage,usage,proxy0])    
    cov_matrix = np.cov(data,bias=True)
    inv_cov_matrix = np.linalg.inv(cov_matrix)
    c = 0; distance = 0;
    comps = [["batsman","season","team","similarity","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR"]]
    for x in AVG:
        proxy2 = df.loc[(df['batsman']==names[c])&(df['season']==year[c]),'age_proxy'].sum()
        v2 = np.array([AVG[c],SR[c],PP_usage[c],mid_usage[c],setup_usage[c],death_usage[c],usage[c],proxy2])
        vdiff = v2-v_adj
        distance = (np.sqrt(abs(np.matmul(np.matmul(vdiff,inv_cov_matrix),vdiff.transpose()))))
        score = 1/(1+distance)
        if(p != names[c] and year[c] > year.min()):
            comps.append([names[c],year[c],team[c],score,usage[c],AVG[c],SR[c],runs[c],wickets[c],PP_usage[c],mid_usage[c],setup_usage[c],death_usage[c],dots[c],ones[c],twos[c],threes[c],fours[c],sixes[c],xAVG[c],xSR[c]])
        c = c + 1
    return comps

def bowling_projection(df,df2,player,year):
    names = df['bowler'].values
    season = df['season'].values
    team = df['bowling_team'].values
    usage = df['usage'].values
    wickets = df['outs_bowler'].values
    PP_usage = df['powerplay'].values
    mid_usage = df['middle'].values
    setup_usage = df['setup'].values
    death_usage = df['death'].values
    balls = df['balls_bowler'].values
    runs = df['runs_off_bat'].values
    dots = df['0s'].values
    ones = df['1s'].values
    twos = df['2s'].values
    threes = df['3s'].values
    fours = df['4s'].values
    sixes = df['6s'].values
    extras = df['extras'].values
    xRuns = df['xruns'].values
    xWickets = df['xwickets'].values
    bb_GP = df['bb_GP'].values
    avg_season = df2['Season'].values
    avg_runs = df2['runs/ball'].values
    avg_wickets = df2['wickets/ball'].values
    avg_dots = df2['0s/ball'].values
    avg_ones = df2['1s/ball'].values
    avg_twos = df2['2s/ball'].values
    avg_threes = df2['3s/ball'].values
    avg_fours = df2['4s/ball'].values
    avg_sixes = df2['6s/ball'].values
    avg_extras = df2['extras/ball'].values
    #print(avg_season)
    c = 0; c2 = 0; curr_team = "Free Agent"; ECON = 0; SR = 0
    y1_usage = 0.000001; y1_wickets = 0.000001; y1_PP_usage = 0.000001; y1_mid_usage = 0.000001; y1_setup_usage = 0.000001; y1_death_usage = 0.000001; y1_balls = 0.000001;    y1_runs = 0.000001; y1_dots = 0.000001; y1_ones = 0.000001; y1_twos = 0.000001; y1_threes = 0.000001; y1_fours = 0.000001; y1_sixes = 0.000001; y1_extras = 0.000001;
    y2_usage = 0.000001; y2_wickets = 0.000001; y2_PP_usage = 0.000001; y2_mid_usage = 0.000001; y2_setup_usage = 0.000001; y2_death_usage = 0.000001; y2_balls = 0.000001;    y2_runs = 0.000001; y2_dots = 0.000001; y2_ones = 0.000001; y2_twos = 0.000001; y2_threes = 0.000001; y2_fours = 0.000001; y2_sixes = 0.000001; y2_extras = 0.000001;
    y3_usage = 0.000001; y3_wickets = 0.000001; y3_PP_usage = 0.000001; y3_mid_usage = 0.000001; y3_setup_usage = 0.000001; y3_death_usage = 0.000001; y3_balls = 0.000001;    y3_runs = 0.000001; y3_dots = 0.000001; y3_ones = 0.000001; y3_twos = 0.000001; y3_threes = 0.000001; y3_fours = 0.000001; y3_sixes = 0.000001; y3_extras = 0.000001;
    y4_usage = 0.000001; y4_wickets = 0.000001; y4_PP_usage = 0.000001; y4_mid_usage = 0.000001; y4_setup_usage = 0.000001; y4_death_usage = 0.000001; y4_balls = 0.000001;    y4_runs = 0.000001; y4_dots = 0.000001; y4_ones = 0.000001; y4_twos = 0.000001; y4_threes = 0.000001; y4_fours = 0.000001; y4_sixes = 0.000001; y4_extras = 0.000001;
    y5_usage = 0.000001; y5_wickets = 0.000001; y5_PP_usage = 0.000001; y5_mid_usage = 0.000001; y5_setup_usage = 0.000001; y5_death_usage = 0.000001; y5_balls = 0.000001;    y5_runs = 0.000001; y5_dots = 0.000001; y5_ones = 0.000001; y5_twos = 0.000001; y5_threes = 0.000001; y5_fours = 0.000001; y5_sixes = 0.000001; y5_extras = 0.000001; 
    y6_usage = 0.000001; y6_wickets = 0.000001; y6_PP_usage = 0.000001; y6_mid_usage = 0.000001; y6_setup_usage = 0.000001; y6_death_usage = 0.000001; y6_balls = 0.000001;    y6_runs = 0.000001; y6_dots = 0.000001; y6_ones = 0.000001; y6_twos = 0.000001; y6_threes = 0.000001; y6_fours = 0.000001; y6_sixes = 0.000001; y6_extras = 0.000001; 
    p_xECON = 0; p_xSR = 0; y1_xRuns = 0; y2_xRuns = 0;y3_xRuns = 0;y4_xRuns = 0;y5_xRuns = 0;y6_xRuns = 0
    y1_xWickets = 0; y2_xWickets = 0;y3_xWickets = 0;y4_xWickets = 0;y5_xWickets = 0;y6_xWickets = 0
    y1_bb_gp =0; y2_bb_gp =0; y3_bb_gp =0; y4_bb_gp =0; y5_bb_gp =0; y6_bb_gp =0;
    y1_avg_runs = 0; y1_avg_wickets = 0; y1_avg_dots = 0; y1_avg_ones = 0; y1_avg_twos = 0; y1_avg_threes = 0; y1_avg_fours = 0; y1_avg_sixes = 0
    y2_avg_runs = 0; y2_avg_wickets = 0; y2_avg_dots = 0; y2_avg_ones = 0; y2_avg_twos = 0; y2_avg_threes = 0; y2_avg_fours = 0; y2_avg_sixes = 0
    y3_avg_runs = 0; y3_avg_wickets = 0; y3_avg_dots = 0; y3_avg_ones = 0; y3_avg_twos = 0; y3_avg_threes = 0; y3_avg_fours = 0; y3_avg_sixes = 0
    y4_avg_runs = 0; y4_avg_wickets = 0; y4_avg_dots = 0; y4_avg_ones = 0; y4_avg_twos = 0; y4_avg_threes = 0; y4_avg_fours = 0; y4_avg_sixes = 0
    y5_avg_runs = 0; y5_avg_wickets = 0; y5_avg_dots = 0; y5_avg_ones = 0; y5_avg_twos = 0; y5_avg_threes = 0; y5_avg_fours = 0; y5_avg_sixes = 0
    y6_avg_runs = 0; y6_avg_wickets = 0; y6_avg_dots = 0; y6_avg_ones = 0; y6_avg_twos = 0; y6_avg_threes = 0; y6_avg_fours = 0; y6_avg_sixes = 0
    y1_avg_extras = 0; y2_avg_extras = 0; y3_avg_extras = 0; y4_avg_extras = 0; y5_avg_extras = 0; y6_avg_extras = 0
    
    for x in names:
        if(names[c]==player and season[c]==year-1):
            y1_usage = usage[c]
            y1_wickets = wickets[c]
            y1_PP_usage = PP_usage[c]
            y1_mid_usage = mid_usage[c]
            y1_setup_usage = setup_usage[c]
            y1_death_usage = death_usage[c]
            y1_balls = balls[c]
            y1_runs = runs[c]
            y1_dots = dots[c]
            y1_ones = ones[c]
            y1_twos = twos[c]
            y1_threes = threes[c]
            y1_fours = fours[c]
            y1_sixes = sixes[c]
            y1_extras = extras[c]
            y1_xWickets = xWickets[c]
            y1_xRuns = xRuns[c]
            y1_bb_gp = bb_GP[c]
            curr_team = team[c]
        if(names[c]==player and season[c]==year-2):
            y2_usage = usage[c]
            y2_wickets = wickets[c]
            y2_PP_usage = PP_usage[c]
            y2_mid_usage = mid_usage[c]
            y2_setup_usage = setup_usage[c]
            y2_death_usage = death_usage[c]
            y2_balls = balls[c]
            y2_runs = runs[c]
            y2_dots = dots[c]
            y2_ones = ones[c]
            y2_twos = twos[c]
            y2_threes = threes[c]
            y2_fours = fours[c]
            y2_sixes = sixes[c]
            y2_extras = extras[c]
            y2_xWickets = xWickets[c]
            y2_bb_gp = bb_GP[c]
            y2_xRuns = xRuns[c]
        if(names[c]==player and season[c]==year-3):
            y3_usage = usage[c]
            y3_wickets = wickets[c]
            y3_PP_usage = PP_usage[c]
            y3_mid_usage = mid_usage[c]
            y3_setup_usage = setup_usage[c]
            y3_death_usage = death_usage[c]
            y3_balls = balls[c]
            y3_runs = runs[c]
            y3_dots = dots[c]
            y3_ones = ones[c]
            y3_twos = twos[c]
            y3_threes = threes[c]
            y3_fours = fours[c]
            y3_sixes = sixes[c]
            y3_extras = extras[c]
            y3_xWickets = xWickets[c]
            y3_bb_gp = bb_GP[c]
            y3_xRuns = xRuns[c]
        if(names[c]==player and season[c]==year-4):
            y4_usage = usage[c]
            y4_wickets = wickets[c]
            y4_PP_usage = PP_usage[c]
            y4_mid_usage = mid_usage[c]
            y4_setup_usage = setup_usage[c]
            y4_death_usage = death_usage[c]
            y4_balls = balls[c]
            y4_runs = runs[c]
            y4_dots = dots[c]
            y4_ones = ones[c]
            y4_twos = twos[c]
            y4_threes = threes[c]
            y4_fours = fours[c]
            y4_sixes = sixes[c]
            y4_xWickets = xWickets[c]
            y4_xRuns = xRuns[c]
            y4_bb_gp = bb_GP[c]
            y4_extras = extras[c]
        if(names[c]==player and season[c]==year-5):
            y5_usage = usage[c]
            y5_wickets = wickets[c]
            y5_PP_usage = PP_usage[c]
            y5_mid_usage = mid_usage[c]
            y5_setup_usage = setup_usage[c]
            y5_death_usage = death_usage[c]
            y5_balls = balls[c]
            y5_runs = runs[c]
            y5_dots = dots[c]
            y5_ones = ones[c]
            y5_twos = twos[c]
            y5_threes = threes[c]
            y5_fours = fours[c]
            y5_sixes = sixes[c]
            y5_xWickets = xWickets[c]
            y5_xRuns = xRuns[c]
            y5_bb_gp = bb_GP[c]
            y5_extras = extras[c]
        if(names[c]==player and season[c]==year-6):
            y6_usage = usage[c]
            y6_wickets = wickets[c]
            y6_PP_usage = PP_usage[c]
            y6_mid_usage = mid_usage[c]
            y6_setup_usage = setup_usage[c]
            y6_death_usage = death_usage[c]
            y6_balls = balls[c]
            y6_runs = runs[c]
            y6_dots = dots[c]
            y6_ones = ones[c]
            y6_twos = twos[c]
            y6_threes = threes[c]
            y6_fours = fours[c]
            y6_sixes = sixes[c]
            y6_xWickets = xWickets[c]
            y6_xRuns = xRuns[c]
            y6_bb_gp = bb_GP[c]
            y6_extras = extras[c]
        c = c + 1
    
    for y in avg_season:
        if(avg_season[c2]==year-1):
            y1_avg_runs = avg_runs[c2]
            y1_avg_wickets = avg_wickets[c2]
            y1_avg_dots = avg_dots[c2]
            y1_avg_ones = avg_ones[c2]
            y1_avg_twos = avg_twos[c2]
            y1_avg_threes = avg_threes[c2]
            y1_avg_fours = avg_fours[c2]
            y1_avg_sixes = avg_sixes[c2]
            y1_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-2):
            y2_avg_runs = avg_runs[c2]
            y2_avg_wickets = avg_wickets[c2]
            y2_avg_dots = avg_dots[c2]
            y2_avg_ones = avg_ones[c2]
            y2_avg_twos = avg_twos[c2]
            y2_avg_threes = avg_threes[c2]
            y2_avg_fours = avg_fours[c2]
            y2_avg_sixes = avg_sixes[c2]
            y2_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-3):
            y3_avg_runs = avg_runs[c2]
            y3_avg_wickets = avg_wickets[c2]
            y3_avg_dots = avg_dots[c2]
            y3_avg_ones = avg_ones[c2]
            y3_avg_twos = avg_twos[c2]
            y3_avg_threes = avg_threes[c2]
            y3_avg_fours = avg_fours[c2]
            y3_avg_sixes = avg_sixes[c2]
            y3_avg_extras = avg_extras[c2]    
        if(avg_season[c2]==year-4):
            y4_avg_runs = avg_runs[c2]
            y4_avg_wickets = avg_wickets[c2]
            y4_avg_dots = avg_dots[c2]
            y4_avg_ones = avg_ones[c2]
            y4_avg_twos = avg_twos[c2]
            y4_avg_threes = avg_threes[c2]
            y4_avg_fours = avg_fours[c2]
            y4_avg_sixes = avg_sixes[c2]
            y4_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-5):
            y5_avg_runs = avg_runs[c2]
            y5_avg_wickets = avg_wickets[c2]
            y5_avg_dots = avg_dots[c2]
            y5_avg_ones = avg_ones[c2]
            y5_avg_twos = avg_twos[c2]
            y5_avg_threes = avg_threes[c2]
            y5_avg_fours = avg_fours[c2]
            y5_avg_sixes = avg_sixes[c2]
            y5_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-6):
            y6_avg_runs = avg_runs[c2]
            y6_avg_wickets = avg_wickets[c2]
            y6_avg_dots = avg_dots[c2]
            y6_avg_ones = avg_ones[c2]
            y6_avg_twos = avg_twos[c2]
            y6_avg_threes = avg_threes[c2]
            y6_avg_fours = avg_fours[c2]
            y6_avg_sixes = avg_sixes[c2]
            y6_avg_extras = avg_extras[c2]
        c2 = c2 + 1
      
    #print(y1_avg_runs,y2_avg_runs,y3_avg_runs,y4_avg_runs,y5_avg_runs,y6_avg_runs)
    if(y1_avg_runs==0):
        y1_avg_runs = y2_avg_runs
        y1_avg_wickets = y2_avg_wickets
        y1_avg_dots = y2_avg_dots
        y1_avg_ones = y2_avg_ones
        y1_avg_twos = y2_avg_twos
        y1_avg_threes = y2_avg_threes
        y1_avg_fours = y2_avg_fours
        y1_avg_sixes = y2_avg_sixes
        y1_avg_extras = y2_avg_extras
    if(y2_avg_runs==0):
        y2_avg_runs = y1_avg_runs
        y2_avg_wickets = y1_avg_wickets
        y2_avg_dots = y1_avg_dots
        y2_avg_ones = y1_avg_ones
        y2_avg_twos = y1_avg_twos
        y2_avg_threes = y1_avg_threes
        y2_avg_fours = y1_avg_fours
        y2_avg_sixes = y1_avg_sixes
        y2_avg_extras = y1_avg_extras
    if(y3_avg_runs==0):
        y3_avg_runs = y2_avg_runs
        y3_avg_wickets = y2_avg_wickets
        y3_avg_dots = y2_avg_dots
        y3_avg_ones = y2_avg_ones
        y3_avg_twos = y2_avg_twos
        y3_avg_threes = y2_avg_threes
        y3_avg_fours = y2_avg_fours
        y3_avg_sixes = y2_avg_sixes
        y3_avg_extras = y2_avg_extras
    if(y4_avg_runs==0):
        y4_avg_runs = y3_avg_runs
        y4_avg_wickets = y3_avg_wickets
        y4_avg_dots = y3_avg_dots
        y4_avg_ones = y3_avg_ones
        y4_avg_twos = y3_avg_twos
        y4_avg_threes = y3_avg_threes
        y4_avg_fours = y3_avg_fours
        y4_avg_sixes = y3_avg_sixes
        y4_avg_extras = y3_avg_extras
    if(y5_avg_runs==0):
        y5_avg_runs = y4_avg_runs
        y5_avg_wickets = y4_avg_wickets
        y5_avg_dots = y4_avg_dots
        y5_avg_ones = y4_avg_ones
        y5_avg_twos = y4_avg_twos
        y5_avg_threes = y4_avg_threes
        y5_avg_fours = y4_avg_fours
        y5_avg_sixes = y4_avg_sixes
        y5_avg_extras = y4_avg_extras
    if(y6_avg_runs==0):
        y6_avg_runs = y5_avg_runs
        y6_avg_wickets = y5_avg_wickets
        y6_avg_dots = y5_avg_dots
        y6_avg_ones = y5_avg_ones
        y6_avg_twos = y5_avg_twos
        y6_avg_threes = y5_avg_threes
        y6_avg_fours = y5_avg_fours
        y6_avg_sixes = y5_avg_sixes
        y6_avg_extras = y5_avg_extras
    #print(y1_avg_runs,y2_avg_runs,y3_avg_runs,y4_avg_runs,y5_avg_runs,y6_avg_runs)
    
    w_balls = 8*y1_balls + 5*y2_balls + 4*y3_balls + 3*y4_balls + 2*y5_balls + y6_balls
    w_runs = 8*y1_runs + 5*y2_runs + 4*y3_runs +3*y4_runs + 2*y5_runs + y6_runs
    w_dots = 8*y1_dots + 5*y2_dots + 4*y3_dots +3*y4_dots + 2*y5_dots + y6_dots
    w_ones = 8*y1_ones + 5*y2_ones + 4*y3_ones +3*y4_ones + 2*y5_ones + y6_ones
    w_twos = 8*y1_twos + 5*y2_twos + 4*y3_twos +3*y4_twos + 2*y5_twos + y6_twos
    w_threes = 8*y1_threes + 5*y2_threes + 4*y3_threes +3*y4_threes + 2*y5_threes + y6_threes
    w_fours = 8*y1_fours + 5*y2_fours + 4*y3_fours +3*y4_fours + 2*y5_fours + y6_fours
    w_sixes = 8*y1_sixes + 5*y2_sixes + 4*y3_sixes +3*y4_sixes + 2*y5_sixes + y6_sixes
    w_wickets = 8*y1_wickets + 5*y2_wickets + 4*y3_wickets +3*y4_wickets + 2*y5_wickets + y6_wickets
    w_extras = 8*y1_extras + 5*y2_extras + 4*y3_extras +3*y4_extras + 2*y5_extras + y6_extras
    w_PP_usage = 8*y1_PP_usage + 5*y2_PP_usage + 4*y3_PP_usage +3*y4_PP_usage + 2*y5_PP_usage + y6_PP_usage
    w_mid_usage = 8*y1_mid_usage + 5*y2_mid_usage + 4*y3_mid_usage +3*y4_mid_usage + 2*y5_mid_usage + y6_mid_usage
    w_setup_usage = 8*y1_setup_usage + 5*y2_setup_usage + 4*y3_setup_usage +3*y4_setup_usage + 2*y5_setup_usage + y6_setup_usage
    w_death_usage = 8*y1_death_usage + 5*y2_death_usage + 4*y3_death_usage +3*y4_death_usage + 2*y5_death_usage + y6_death_usage
    w_usage = 8*y1_usage + 5*y2_usage + 4*y3_usage +3*y4_usage + 2*y5_usage + y6_usage
    p_xECON = 8*y1_xRuns + 5*y2_xRuns + 4*y3_xRuns +3*y4_xRuns + 2*y5_xRuns + y6_xRuns
    p_xSR = 8*y1_xWickets + 5*y2_xWickets + 4*y3_xWickets +3*y4_xWickets + 2*y5_xWickets + y6_xWickets
    #print(w_wickets)
    mr_runs = (800/w_balls)*(8*y1_balls*y1_avg_runs + 5*y2_balls*y2_avg_runs + 4*y3_balls*y3_avg_runs + 3*y4_balls*y4_avg_runs + 2*y5_balls*y5_avg_runs + y6_balls*y6_avg_runs)    
    mr_dots = (800/w_balls)*(8*y1_balls*y1_avg_dots + 5*y2_balls*y2_avg_dots + 4*y3_balls*y3_avg_dots + 3*y4_balls*y4_avg_dots + 2*y5_balls*y5_avg_dots + y6_balls*y6_avg_dots)
    mr_ones = (800/w_balls)*(8*y1_balls*y1_avg_ones + 5*y2_balls*y2_avg_ones + 4*y3_balls*y3_avg_ones + 3*y4_balls*y4_avg_ones + 2*y5_balls*y5_avg_ones + y6_balls*y6_avg_ones)
    mr_twos = (800/w_balls)*(8*y1_balls*y1_avg_twos + 5*y2_balls*y2_avg_twos + 4*y3_balls*y3_avg_twos + 3*y4_balls*y4_avg_twos + 2*y5_balls*y5_avg_twos + y6_balls*y6_avg_twos)
    mr_threes = (800/w_balls)*(8*y1_balls*y1_avg_threes + 5*y2_balls*y2_avg_threes + 4*y3_balls*y3_avg_threes + 3*y4_balls*y4_avg_threes + 2*y5_balls*y5_avg_threes + y6_balls*y6_avg_threes)
    mr_fours = (800/w_balls)*(8*y1_balls*y1_avg_fours + 5*y2_balls*y2_avg_fours + 4*y3_balls*y3_avg_fours + 3*y4_balls*y4_avg_fours + 2*y5_balls*y5_avg_fours + y6_balls*y6_avg_fours)
    mr_sixes = (800/w_balls)*(8*y1_balls*y1_avg_sixes + 5*y2_balls*y2_avg_sixes + 4*y3_balls*y3_avg_sixes + 3*y4_balls*y4_avg_sixes + 2*y5_balls*y5_avg_sixes + y6_balls*y6_avg_sixes)
    mr_wickets = (800/w_balls)*(8*y1_balls*y1_avg_wickets + 5*y2_balls*y2_avg_wickets + 4*y3_balls*y3_avg_wickets + 3*y4_balls*y4_avg_wickets + 2*y5_balls*y5_avg_wickets + y6_balls*y6_avg_wickets)
    mr_extras = (800/w_balls)*(8*y1_balls*y1_avg_extras + 5*y2_balls*y2_avg_extras + 4*y3_balls*y3_avg_extras + 3*y4_balls*y4_avg_extras + 2*y5_balls*y5_avg_extras + y6_balls*y6_avg_extras)
    w_bb_gp = (8*y1_bb_gp + 5*y2_bb_gp + 4*y3_bb_gp + 3*y4_bb_gp + 2*y5_bb_gp + y6_bb_gp)
    #print(mr_wickets)
    if(y1_usage==0.000001): y1_usage = 0
    if(y2_usage==0.000001): y2_usage = 0
    if(y3_usage==0.000001): y3_usage = 0
    if(y4_usage==0.000001): y4_usage = 0
    if(y5_usage==0.000001): y5_usage = 0
    if(y6_usage==0.000001): y6_usage = 0
    #print(p_xECON,p_xSR,w_balls)
    if(y1_usage==0 and y2_usage==0 and y3_usage==0 and y4_usage==0 and y5_usage==0 and y6_usage==0):
        p_usage = 0; p_xECON = 999; p_xSR = 999; p_bb_gp = 0
    else:
        p_usage = w_usage/(8*math.ceil(y1_usage) + 5*math.ceil(y2_usage) + 4*math.ceil(y3_usage) + 3*math.ceil(y4_usage) + 2*math.ceil(y5_usage) + math.ceil(y6_usage))
        p_xECON = 6*p_xECON/w_balls
        p_xSR = w_balls/(p_xSR+0.000000001)
        p_bb_gp = w_bb_gp/(8*math.ceil(y1_usage) + 5*math.ceil(y2_usage) + 4*math.ceil(y3_usage) + 3*math.ceil(y4_usage) + 2*math.ceil(y5_usage) + math.ceil(y6_usage))
    
    #p_balls = 120*14*p_usage
    p_runs = (w_runs+mr_runs)/(800+w_balls)
    p_dots = (w_dots+mr_dots)/(800+w_balls)
    p_ones = (w_ones+mr_ones)/(800+w_balls)
    p_twos = (w_twos+mr_twos)/(800+w_balls)
    p_threes = (w_threes+mr_threes)/(800+w_balls)
    p_fours = (w_fours+mr_fours)/(800+w_balls)
    p_sixes = (w_sixes+mr_sixes)/(800+w_balls)
    p_extras = (w_extras+mr_extras)/(800+w_balls)
    p_wickets = (w_wickets+mr_wickets)/(800+w_balls)
    dummy = (w_PP_usage + w_setup_usage + w_mid_usage + w_death_usage)/w_balls
    p_PP_usage = w_PP_usage/(w_balls*dummy)
    p_setup_usage = w_setup_usage/(w_balls*dummy)
    p_mid_usage = w_mid_usage/(w_balls*dummy)
    p_death_usage = w_death_usage/(w_balls*dummy)
    if(p_usage == 0):
        ECON = 999
        SR = 999
    elif(p_wickets == 0):
        SR = 999
    else:
        ECON = 6*p_runs
        SR = 1.0/p_wickets
    projection = [player,year,curr_team,p_usage,ECON,SR,p_wickets,p_PP_usage,p_mid_usage,p_setup_usage,p_death_usage,p_runs,p_dots,p_ones,p_twos,p_threes,p_fours,p_sixes,p_extras,p_xECON,p_xSR,p_bb_gp]
    #print(p_wickets)
    return projection 

def venue_projections():
    venue_bat = pd.read_excel(input_file,'venue batting')
    bat_avg = pd.read_excel(input_file,'batting phases')
    teams = list(dict.fromkeys(venue_bat['Venue'].tolist()))
    
    proj_year_bat = pd.DataFrame(columns=venue_bat.columns)
    proj_year_bat['Venue'] = teams
    proj_year_bat['Season'] = proj_year
    proj_year_bat['Weight'] = 0
    
    for p in teams:
        for q in venue_bat.columns:      
            if(q != 'Venue' and q != 'Season'):
                #print(p,q,venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==2023),q].sum())
                proj_year_bat.loc[proj_year_bat['Venue']==p,q] = 8*venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-1),q].sum()+5*venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-2),q].sum()+4*venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-3),q].sum()+3*venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-4),q].sum()+2*venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-5),q].sum()+venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-6),q].sum()           
        
        if(venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-1),'Sum of powerplay'].sum()!=0): proj_year_bat.loc[proj_year_bat['Venue']==p,'Weight'] += 8
        if(venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-2),'Sum of powerplay'].sum()!=0): proj_year_bat.loc[proj_year_bat['Venue']==p,'Weight'] += 5
        if(venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-3),'Sum of powerplay'].sum()!=0): proj_year_bat.loc[proj_year_bat['Venue']==p,'Weight'] += 4
        if(venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-4),'Sum of powerplay'].sum()!=0): proj_year_bat.loc[proj_year_bat['Venue']==p,'Weight'] += 3
        if(venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-5),'Sum of powerplay'].sum()!=0): proj_year_bat.loc[proj_year_bat['Venue']==p,'Weight'] += 2
        if(venue_bat.loc[(venue_bat['Venue']==p)&(venue_bat['Season']==proj_year-6),'Sum of powerplay'].sum()!=0): proj_year_bat.loc[proj_year_bat['Venue']==p,'Weight'] += 1
    
    lg_balls = bat_avg['Sum of powerplay'].sum()+bat_avg['Sum of middle'].sum()+bat_avg['Sum of setup'].sum()+bat_avg['Sum of death'].sum()
    lg_runs = bat_avg['Sum of pp_runs_batsman'].sum()+bat_avg['Sum of mid_runs_batsman'].sum()+bat_avg['Sum of setup_runs_batsman'].sum()+bat_avg['Sum of death_runs_batsman'].sum()
    lg_wickets = bat_avg['Sum of pp_wickets_batsman'].sum()+bat_avg['Sum of mid_wickets_batsman'].sum()+bat_avg['Sum of setup_wickets_batsman'].sum()+bat_avg['Sum of death_wickets_batsman'].sum()
    lg_runs = lg_runs*20000/lg_balls
    lg_wickets = lg_wickets*20000/lg_balls
    lg_balls = 20000
    
    final = pd.DataFrame(columns=['Venue','Season','runs','wkts'])
    final['Venue'] = teams
    final['Season'] = proj_year
    
    for p in teams:
        final.loc[final['Venue']==p,'runs']
        team_balls = proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of powerplay']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of middle']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of setup']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of death']
        team_runs = proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of pp_runs_batsman']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of mid_runs_batsman']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of setup_runs_batsman']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of death_runs_batsman']
        team_wickets = proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of pp_wickets_batsman']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of mid_wickets_batsman']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of setup_wickets_batsman']+proj_year_bat.loc[proj_year_bat['Venue']==p,'Sum of death_wickets_batsman']
        final.loc[final['Venue']==p,'runs'] = ((team_runs+lg_runs)/(team_balls+lg_balls))/(lg_runs/lg_balls)
        final.loc[final['Venue']==p,'wkts'] = ((team_wickets+lg_wickets)/(team_balls+lg_balls))/(lg_wickets/lg_balls)
    
    final = final.apply(pd.to_numeric, errors='ignore')
    return final

def venue_projections_new():
    venue_pace_spin = pd.read_excel(input_file,'venue pace_spin')
    matchups = list(product(['spin','pace'],venue_pace_spin['venue'].unique()))
    matchups = pd.DataFrame(matchups, columns =['bowl_type','venue'])
    matchups['season'] = proj_year
    #matchups['weight'] = 0
    matchups['bias'] = 0.5

    spin_la_balls = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='spin','balls'].sum()
    spin_la_runs = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='spin','runs'].sum()
    spin_la_wickets = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='spin','wickets'].sum()
    pace_la_balls = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='pace','balls'].sum()
    pace_la_runs = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='pace','runs'].sum()
    pace_la_wickets = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='pace','wickets'].sum()

    for x in matchups.values:
        #print(x)
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'] = 8*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
            5*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
            4*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
            3*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
            2*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
            venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()
            
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'runs'] = 8*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
            5*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
            4*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
            3*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
            2*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
            venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum()
            
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'wickets'] = 8*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
            5*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
            4*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
            3*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
            2*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
            venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum()
        
        #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 8
        #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 5
        #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 4
        #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 3
        #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 2
        #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 1

        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'] += 20000
        if(x[0] == 'spin'):
            matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'runs'] += 20000*(spin_la_runs/spin_la_balls)
            matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'wickets'] += 20000*(spin_la_wickets/spin_la_balls)
        else:
            matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'runs'] += 20000*(pace_la_runs/pace_la_balls)
            matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'wickets'] += 20000*(pace_la_wickets/pace_la_balls)
            
    matchups['AVG'] = matchups['balls']/matchups['wickets']
    matchups['SR'] = 100*matchups['runs']/matchups['balls']

    matchups.loc[matchups['bowl_type']=='pace','rf'] = (matchups['runs']/matchups['balls'])/(pace_la_runs/pace_la_balls)
    matchups.loc[matchups['bowl_type']=='spin','rf'] = (matchups['runs']/matchups['balls'])/(spin_la_runs/spin_la_balls)
    matchups.loc[matchups['bowl_type']=='pace','wf'] = (matchups['wickets']/matchups['balls'])/(pace_la_wickets/pace_la_balls)
    matchups.loc[matchups['bowl_type']=='spin','wf'] = (matchups['wickets']/matchups['balls'])/(spin_la_wickets/spin_la_balls)

    for x in matchups.values:
        if(x[0] == 'spin'):
            matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'bias'] = (matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'].sum()-20000+7000)/(matchups.loc[(matchups['venue']==x[1]),'balls'].sum()-40000+20000)
        else:
            matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'bias'] = (matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'].sum()-20000+13000)/(matchups.loc[(matchups['venue']==x[1]),'balls'].sum()-40000+20000)

    matchups = matchups[['venue','season','rf','wf','bowl_type','bias']]

    m2 = pd.DataFrame(columns = matchups.columns)
    m2['venue'] = matchups['venue'].unique()
    m2['season'] = proj_year
    m2['bowl_type'] = 'all'
    m2['bias'] = 1

    for x in m2.values:
        #print(x)
        m2.loc[m2['venue']==x[0],'rf'] = (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'rf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'bias'].sum()) +\
                                         (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'rf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'bias'].sum())
                                         
        m2.loc[m2['venue']==x[0],'wf'] = (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'wf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'bias'].sum()) +\
                                         (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'wf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'bias'].sum())

    final = pd.concat([matchups, m2], axis=0)
    final = final.apply(pd.to_numeric, errors='ignore')
    final = final.sort_values('venue')
    final = final.rename(columns={'rf': 'runs', 'wf': 'wkts'})
    return final

def proj_dump():
    lolcow = [["bowler","season","team","RCAA","WTAA","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage","runs/ball","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","xECON","xSR","bb_GP"]]
    lolcow2 = [["bowler","season","team","RCAA","WTAA","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage","runs/ball","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","xECON","xSR","bb_GP"]]
    lolcow4 = [["batsman","season","team","RSAA","OAA","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR","bf_GP"]]
    lolcow5 = [["batsman","season","team","RSAA","OAA","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR","bf_GP"]]
    
    for x in unique_names:
        #now = datetime.datetime.now()
        #print(x,proj_year,now.time())
        p_dummy = bowling_projection(file,file2,x,proj_year)
        if(p_dummy[3] > 0):
            a = 20*(p_dummy[4]-p_dummy[19])*p_dummy[3] #100*(p_dummy[19]/p_dummy[4])
            b = 120*((1/p_dummy[5])-(1/p_dummy[20]))*p_dummy[3]#100*(p_dummy[20]/p_dummy[5])
            p_dummy.insert(3,a)
            p_dummy.insert(4,b)
            lolcow.append(p_dummy) 
            
    lol0 = pd.DataFrame(lolcow)
    lol0.columns = lol0.iloc[0];lol0 = lol0.drop(0)
    """
    for x in lol0['bowler']:
        now = datetime.datetime.now()
        print(x,proj_year,now.time())
        base_proj = lol0.loc[lol0['bowler']==x].values.flatten().tolist()
        del base_proj[3:5]
        p_dummy = bowling_projection_comps(file,file2,x,proj_year,0,base_proj)
        #print(x,p_dummy)
        if(p_dummy[3] > 0):
            a = 20*(p_dummy[4]-p_dummy[19])*p_dummy[3] #100*(p_dummy[19]/p_dummy[4])
            b = 120*((1/p_dummy[5])-(1/p_dummy[20]))*p_dummy[3]#100*(p_dummy[20]/p_dummy[5])
            p_dummy.insert(3,a)
            p_dummy.insert(4,b)
            lolcow2.append(p_dummy)           
    """               
    print("bowling projections dumped")
    
    for x in unique_names2:
        p_dummy = batting_projection(file3,file4,x,proj_year)
        if(p_dummy[3] > 0):
            a = factor*1.2*(p_dummy[5]-p_dummy[19])*p_dummy[3] #100*(p_dummy[4]/p_dummy[18])
            b = factor*120*((1/p_dummy[4])-(1/p_dummy[18]))*p_dummy[3] #100*(p_dummy[5]/p_dummy[19])
            p_dummy.insert(3,a)
            p_dummy.insert(4,b)
            lolcow4.append(p_dummy)  
            
    lol3 = pd.DataFrame(lolcow4)
    lol3.columns = lol3.iloc[0];lol3 = lol3.drop(0)
    """ 
    for x in lol3['batsman']:
        now = datetime.datetime.now()
        print(x,proj_year,now.time())
        p_dummy = batting_projection_comps(file3,file4,x,proj_year,0)
        #print(x,p_dummy)
        if(p_dummy[3] > 0):
            a = factor*1.2*(p_dummy[5]-p_dummy[19])*p_dummy[3] #100*(p_dummy[4]/p_dummy[18])
            b = factor*120*((1/p_dummy[4])-(1/p_dummy[18]))*p_dummy[3] #100*(p_dummy[5]/p_dummy[19])
            p_dummy.insert(3,a)
            p_dummy.insert(4,b)
            lolcow5.append(p_dummy)           
    """
    lol = pd.DataFrame(lolcow)
    lol.columns = lol.iloc[0];lol = lol.drop(0)   
    lol4 = pd.DataFrame(lolcow4)
    lol4.columns = lol4.iloc[0];lol4 = lol4.drop(0)
    print("batting projections dumped")
    
    missing = []
    if(factor <= 2.5): 
        (lol5,lol2,missing) = player_aging(lol4.copy(),lol.copy(),proj_year)
    else:
        lol2 = pd.DataFrame(lolcow) #lolcow2
        lol2.columns = lol2.iloc[0];lol2 = lol2.drop(0)
        lol5 = pd.DataFrame(lolcow4) #lolcow5
        lol5.columns = lol5.iloc[0];lol5 = lol5.drop(0)
    print("aging applied")
    
    concat = [];
    for (x,y) in zip(file['bowling_team'].values,file['season'].values):
        concat.append(x+";"+str(y))
    concat = np.unique(concat)
    
    for t in unique(lol['team'].to_list()):
        if(t != 'Free Agent'):
            team_bowl_usage = lol.loc[lol['team']==t,'usage'].sum()
            team_bat_usage = lol4.loc[lol4['team']==t,'usage'].sum()
            if(team_bowl_usage>1):
                lol.loc[lol['team']==t,'usage'] = lol.loc[lol['team']==t,'usage']/team_bowl_usage
                lol2.loc[lol2['team']==t,'usage'] = lol2.loc[lol2['team']==t,'usage']/team_bowl_usage
            if(team_bat_usage>1):
                lol4.loc[lol4['team']==t,'usage'] = lol4.loc[lol4['team']==t,'usage']/team_bat_usage
                lol5.loc[lol5['team']==t,'usage'] = lol5.loc[lol5['team']==t,'usage']/team_bat_usage
    
    try:
        (lol4,lol) = balance(lol4,lol,0,factor)
        (lol5,lol2) = balance(lol5,lol2,0,factor)
        print("Marcel based table")
        marcel_table = calc_agg(lol4,lol,factor)  
        print("MDist based table")
        mdist_table = calc_agg(lol5,lol2,factor)
    except ZeroDivisionError:
        print(proj_year-1,"rosters not avalible using",proj_year-2,"rosters")
        for x in lol['bowler'].tolist(): lol.loc[lol['bowler']==x,'team'] = file.loc[(file['bowler']==x)&(file['season']==proj_year-2),'bowling_team'].sum()
        for x in lol2['bowler'].tolist(): lol2.loc[lol2['bowler']==x,'team'] = file.loc[(file['bowler']==x)&(file['season']==proj_year-2),'bowling_team'].sum()
        for x in lol4['batsman'].tolist(): lol4.loc[lol4['batsman']==x,'team'] = file3.loc[(file3['batsman']==x)&(file3['season']==proj_year-2),'batting_team'].sum()
        for x in lol5['batsman'].tolist(): lol5.loc[lol5['batsman']==x,'team'] = file3.loc[(file3['batsman']==x)&(file3['season']==proj_year-2),'batting_team'].sum()
        lol['team'] = lol['team'].replace(0,'Free Agent')
        lol2['team'] = lol2['team'].replace(0,'Free Agent')
        lol4['team'] = lol4['team'].replace(0,'Free Agent')
        lol5['team'] = lol5['team'].replace(0,'Free Agent')
        (lol4,lol) = balance(lol4,lol,0,factor)
        (lol5,lol2) = balance(lol5,lol2,0,factor)
        print("Marcel based table")
        marcel_table = calc_agg(lol4,lol,factor)  
        print("MDist based table")
        mdist_table = calc_agg(lol5,lol2,factor)
    
    p_bat = ""; p_bowl = "";
    final = [["player","team","squad"]]
    names = np.unique(np.concatenate([lol5['batsman'].values,lol2['bowler'].values]))
    
    for x in names:
        try : p_bat = lol5.loc[(lol5['batsman']==x),'team'].values[0]  
        except IndexError: p_bat = "Free Agent"
        try : p_bowl = lol2.loc[(lol2['bowler']==x),'team'].values[0]
        except IndexError: p_bowl = "Free Agent"
        if(p_bat == "Free Agent"): p_team = p_bowl
        else : p_team = p_bat
        
        if(p_team=='Free Agent' and (comp=='t20i' or comp=='odi' or comp=='tests' or comp=='t20iw' or comp=='odiw')):
            k = 1
            while (p_team=='Free Agent' and k<5):
                try: p_bat = file3.loc[(file3['batsman']==x)&(file3['season']==proj_year-k),'batting_team'].values[0]
                except IndexError: p_bat = "Free Agent"
                try: p_bowl = file.loc[(file['bowler']==x)&(file['season']==proj_year-2),'bowling_team'].values[0]
                except IndexError: p_bowl = "Free Agent"
                if(p_bat == "Free Agent"): p_team = p_bowl
                else : p_team = p_bat
                k += 1
            final.append([x,'Free Agent',p_team])
        else:
            final.append([x,p_team,p_team])
        
    final = pd.DataFrame(final)
    final.columns = final.iloc[0];final = final.drop(0)
    final = final.fillna(0)    
    #venues = venue_projections()
    venues = venue_projections_new()
    
    with pd.ExcelWriter(output_file) as writer:        
        mdist_table.to_excel(writer, sheet_name="MDist Table", index=False)
        lol2.to_excel(writer, sheet_name="MDist bowl", index=False)
        lol5.to_excel(writer, sheet_name="MDist bat", index=False)
        final.to_excel(writer, sheet_name="Team", index=False)
        venues.to_excel(writer, sheet_name="Venue factors", index=False)
        marcel_table.to_excel(writer, sheet_name="Marcel Table", index=False)
        lol.to_excel(writer, sheet_name="Marcel bowl", index=False)       
        lol4.to_excel(writer, sheet_name="Marcel bat", index=False)        
            
    print("venue factors dumped")
    #now = datetime.datetime.now()
    #print(now.time())
    return (lol2,lol5,missing)

def comps_future(df,comps):
    names = df['bowler'].values
    year = df['season'].values
    team = df['bowling_team'].values
    wickets = df['wickets/ball'].values
    #balls = df['balls_bowler'].values
    runs = df['runs/ball'].values
    dots = df['0s/ball'].values
    ones = df['1s/ball'].values
    twos = df['2s/ball'].values
    threes = df['3s/ball'].values
    fours = df['4s/ball'].values
    sixes = df['6s/ball'].values
    extras = df['extras/ball'].values
    ECON = df['ECON'].values
    SR = df['SR'].values
    xECON = df['xECON'].values
    xSR = df['xSR'].values
    PP_usage = df['PP usage'].values
    mid_usage = df['mid usage'].values
    setup_usage = df['setup usage'].values
    death_usage = df['death usage'].values
    usage = df['usage'].values
    comps_next = [["bowler","season","team","Similarity","usage","ECON","SR","wickets","pp usage","mid usage","setup usage","death usage","runs","dots","ones","twos","threes","fours","sixes","extras","xECON","xSR"]]
    c = 0; c2 = 0
    #print(comps[0][1])
    for x in comps:
        for y in names:
            #print(comps[c][0],c,names[c2],c2,year[c2],comps[c][1])
            if(names[c2] == comps[c][0] and year[c2] == comps[c][1]+1):
                comps_next.append([names[c2],year[c2],team[c2],comps[c][3],usage[c2],ECON[c2],SR[c2],wickets[c2],PP_usage[c2],mid_usage[c2],setup_usage[c2],death_usage[c2],runs[c2],dots[c2],ones[c2],twos[c2],threes[c2],fours[c2],sixes[c2],extras[c2],xECON[c2],xSR[c2]])
            c2 = c2 + 1
        c = c + 1
        c2 = 0
    return comps_next

def comps_future_bat(df,comps):
    names = df['batsman'].values
    year = df['season'].values
    team = df['batting_team'].values
    usage = df['usage'].values
    wickets = df['outs_batsman'].values
    PP_usage = df['PP usage'].values
    mid_usage = df['mid usage'].values
    setup_usage = df['setup usage'].values
    death_usage = df['death usage'].values
    #balls = df['balls_batsman'].values
    runs = df['runs/ball'].values
    dots = df['0s/ball'].values
    ones = df['1s/ball'].values
    twos = df['2s/ball'].values
    threes = df['3s/ball'].values
    fours = df['4s/ball'].values
    sixes = df['6s/ball'].values
    #extras = df['extras/ball'].values
    xAVG = df['xAVG'].values
    xSR = df['xSR'].values
    AVG = df['AVG'].values
    SR = df['SR'].values
    comps_next = [["batsman","season","team","similarity","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR"]]
    c = 0; c2 = 0
    #print(comps[0][1])
    for x in comps:
        for y in names:
            #print(comps[c][0],c,names[c2],c2,year[c2],comps[c][1])
            if(names[c2] == comps[c][0] and year[c2] == comps[c][1]+1):
                comps_next.append([names[c2],year[c2],team[c2],comps[c][3],usage[c2],AVG[c2],SR[c2],runs[c2],wickets[c2],PP_usage[c2],mid_usage[c2],setup_usage[c2],death_usage[c2],dots[c2],ones[c2],twos[c2],threes[c2],fours[c2],sixes[c2],xAVG[c2],xSR[c2]])
            c2 = c2 + 1
        c = c + 1
        c2 = 0
    return comps_next

def comps_dump(player,year):
    comps = mdist(file,bowling_projection(file,file2,player,proj_year),player)
    current_comp = pd.DataFrame(comps)
    current_comp.columns = current_comp.iloc[0];current_comp = current_comp.drop(0)
    n_comps = comps_future(file,comps)
    next_comp = pd.DataFrame(n_comps)
    next_comp.columns = next_comp.iloc[0];next_comp = next_comp.drop(0)
    with pd.ExcelWriter(dumps_file) as writer:
        current_comp.to_excel(writer, sheet_name="current year", index=False)
        next_comp.to_excel(writer, sheet_name="next year", index=False)
        
def comps_dump_bat(player,year):
    comps = mdist_bat(file3,batting_projection(file3,file4,player,proj_year),player)
    current_comp = pd.DataFrame(comps)
    current_comp.columns = current_comp.iloc[0];current_comp = current_comp.drop(0)
    n_comps = comps_future_bat(file3,comps)
    next_comp = pd.DataFrame(n_comps)
    next_comp.columns = next_comp.iloc[0];next_comp = next_comp.drop(0)
    with pd.ExcelWriter(dumps_file) as writer:
        current_comp.to_excel(writer, sheet_name="current year", index=False)
        next_comp.to_excel(writer, sheet_name="next year", index=False)
        
def bowling_projection_comps(file,file2,player,year,logs,base_proj):
    #base_proj = bowling_projection(file,file2,player,year)
    comps = mdist(file,base_proj,player)
    #now = datetime.datetime.now()
    #print("comps done",now.time())
    projection = similarity_calc(comps, player, year, base_proj[2])
    #now = datetime.datetime.now()
    #print("similarity done",now.time())
    c = 0; delta = []; comps_expected = []
    
    for x in comps:
        if(x[1] != "season"):
            y = bowling_projection(file,file2,x[0],x[1])
            y.insert(3,x[3])
            comps_expected.append(y)
        if(x[1] == "season"): comps_expected.append(x)
    
    comps_expected_weighted = similarity_calc(comps_expected, player, year, base_proj[2])
    
    for x in projection:        
        if(c<3): delta.append(comps_expected_weighted[c])
        elif(comps_expected_weighted[c]==0): delta.append(1)
        else: delta.append(projection[c]/comps_expected_weighted[c])
        c = c + 1
        
    c = 0; projection_new = []
    for x in base_proj:
        if(c<3 or c==21): projection_new.append(base_proj[c])
        else: projection_new.append(delta[c]*base_proj[c])
        c = c + 1
        
    dummy = projection_new[7] + projection_new[8] + projection_new[9] + projection_new[10]
    projection_new[7] = projection_new[7]/dummy
    projection_new[8] = projection_new[8]/dummy
    projection_new[9] = projection_new[9]/dummy
    projection_new[10] = projection_new[10]/dummy    
           
    if (logs == 1):
        print("base projection")
        print(base_proj)
        print("comps weighted actual")
        print(projection)
        print("comps weighted projection")
        print(comps_expected_weighted)
        print("delta")
        print(delta)
        #print("comps weighted y+1 actual")
        #print(sim_y2)
        print("final projection")
        print(projection_new)
        print("RCAA,WTAA")
        print(20*(projection_new[4]-projection_new[19])*projection_new[3],120*((1/projection_new[5])-(1/projection_new[20]))*projection_new[3])
    
    #now = datetime.datetime.now()
    #print("new projection found",now.time())
    return projection_new
    
def similarity_calc(comps,player,year,team):
    #print(comps[1])
    c = 0; w_dist = 0; w_usage = 0; w_runs = 0; w_dots = 0; w_ones = 0; w_twos = 0
    w_threes = 0; w_fours = 0; w_sixes = 0; w_wickets = 0; w_extras = 0; w_PP_usage = 0
    w_mid_usage = 0; w_setup_usage = 0; w_death_usage = 0; w_ECON = 0; w_SR = 0; w_xECON = 0; w_xSR = 0
    for x in comps:
        if(c > 0 and comps[c][3]>0.25):
            w_dist = w_dist + comps[c][3]*comps[c][4]
            w_usage = w_usage + (comps[c][3]*comps[c][4]*comps[c][4])
            w_ECON = w_ECON + (comps[c][3]*comps[c][5]*comps[c][4])
            w_SR = w_SR + (comps[c][3]*comps[c][6]*comps[c][4])
            w_runs = w_runs + (comps[c][3]*comps[c][12]*comps[c][4])
            w_dots = w_dots + (comps[c][3]*comps[c][13]*comps[c][4])
            w_ones = w_ones + (comps[c][3]*comps[c][14]*comps[c][4])
            w_twos = w_twos + (comps[c][3]*comps[c][15]*comps[c][4])
            w_threes = w_threes + (comps[c][3]*comps[c][16]*comps[c][4]) 
            w_fours = w_fours + (comps[c][3]*comps[c][17]*comps[c][4])
            w_sixes = w_sixes + (comps[c][3]*comps[c][18]*comps[c][4])
            w_wickets = w_wickets + (comps[c][3]*comps[c][7]*comps[c][4]) 
            w_extras = w_extras + (comps[c][3]*comps[c][19]*comps[c][4])
            w_PP_usage = w_PP_usage + (comps[c][3]*comps[c][8]*comps[c][4])
            w_mid_usage = w_mid_usage + (comps[c][3]*comps[c][9]*comps[c][4])
            w_setup_usage = w_setup_usage + (comps[c][3]*comps[c][10]*comps[c][4])
            w_death_usage = w_death_usage + (comps[c][3]*comps[c][11]*comps[c][4])
            w_xECON = w_xECON + (comps[c][3]*comps[c][20]*comps[c][4])
            w_xSR = w_xSR + (comps[c][3]*comps[c][21]*comps[c][4])
        c = c + 1
    #print(player,year,w_dist)
    w_dist = w_dist + 0.000001
    p_usage = w_usage/w_dist
    p_ECON = w_ECON/w_dist
    p_SR = w_SR/w_dist
    p_runs = w_runs/w_dist
    p_dots = w_dots/w_dist
    p_ones = w_ones/w_dist
    p_twos = w_twos/w_dist
    p_threes = w_threes/w_dist
    p_fours = w_fours/w_dist
    p_sixes = w_sixes/w_dist
    p_wickets = w_wickets/w_dist
    p_extras = w_extras/w_dist
    p_PP_usage = w_PP_usage/w_dist
    p_mid_usage = w_mid_usage/w_dist
    p_setup_usage = w_setup_usage/w_dist
    p_death_usage = w_death_usage/w_dist
    p_xECON = w_xECON/w_dist
    p_xSR = w_xSR/w_dist
    dummy = (p_PP_usage + p_setup_usage + p_mid_usage + p_death_usage) + 0.00000001
    p_PP_usage = p_PP_usage/dummy
    p_mid_usage = p_mid_usage/dummy
    p_setup_usage = p_setup_usage/dummy
    p_death_usage = p_death_usage/dummy
    c = 0
    projection = [player,year,team,p_usage,p_ECON,p_SR,p_wickets,p_PP_usage,p_mid_usage,p_setup_usage,p_death_usage,p_runs,p_dots,p_ones,p_twos,p_threes,p_fours,p_sixes,p_extras,p_xECON,p_xSR]
    return projection

def similarity_calc_bat(comps,player,year,team):
    #print(comps[0])
    c = 0; w_dist = 0; w_usage = 0; w_runs = 0; w_dots = 0; w_ones = 0; w_twos = 0
    w_threes = 0; w_fours = 0; w_sixes = 0; w_wickets = 0; w_PP_usage = 0
    w_mid_usage = 0; w_setup_usage = 0; w_death_usage = 0; w_AVG = 0; w_SR = 0; w_xAVG = 0; w_xSR = 0
    for x in comps:
        if(c > 0 and comps[c][3]>=0.25):
            #print("we in")
            w_dist = w_dist + comps[c][3]*comps[c][4]
            w_usage = w_usage + (comps[c][3]*comps[c][4]*comps[c][4])
            w_AVG = w_AVG + (comps[c][3]*comps[c][5]*comps[c][4])
            w_SR = w_SR + (comps[c][3]*comps[c][6]*comps[c][4])
            w_runs = w_runs + (comps[c][3]*comps[c][7]*comps[c][4])
            w_dots = w_dots + (comps[c][3]*comps[c][13]*comps[c][4])
            w_ones = w_ones + (comps[c][3]*comps[c][14]*comps[c][4])
            w_twos = w_twos + (comps[c][3]*comps[c][15]*comps[c][4])
            w_threes = w_threes + (comps[c][3]*comps[c][16]*comps[c][4]) 
            w_fours = w_fours + (comps[c][3]*comps[c][17]*comps[c][4])
            w_sixes = w_sixes + (comps[c][3]*comps[c][18]*comps[c][4])
            w_wickets = w_wickets + (comps[c][3]*comps[c][8]*comps[c][4]) 
            #w_extras = w_extras + (comps[c][3]*comps[c][19])
            w_PP_usage = w_PP_usage + (comps[c][3]*comps[c][9]*comps[c][4])
            w_mid_usage = w_mid_usage + (comps[c][3]*comps[c][10]*comps[c][4])
            w_setup_usage = w_setup_usage + (comps[c][3]*comps[c][11]*comps[c][4])
            w_death_usage = w_death_usage + (comps[c][3]*comps[c][12]*comps[c][4])
            w_xAVG = w_xAVG + (comps[c][3]*comps[c][19]*comps[c][4])
            w_xSR = w_xSR + (comps[c][3]*comps[c][20]*comps[c][4])
        c = c + 1
    #print(player,year,w_dist)
    w_dist = w_dist + 0.0000001
    p_usage = w_usage/w_dist
    p_AVG = w_AVG/w_dist
    p_SR = w_SR/w_dist
    p_runs = w_runs/w_dist
    p_dots = w_dots/w_dist
    p_ones = w_ones/w_dist
    p_twos = w_twos/w_dist
    p_threes = w_threes/w_dist
    p_fours = w_fours/w_dist
    p_sixes = w_sixes/w_dist
    p_wickets = w_wickets/w_dist
    #p_extras = w_extras/w_dist
    p_PP_usage = w_PP_usage/w_dist
    p_mid_usage = w_mid_usage/w_dist
    p_setup_usage = w_setup_usage/w_dist
    p_death_usage = w_death_usage/w_dist
    p_xAVG = w_xAVG/w_dist
    p_xSR = w_xSR/w_dist
    dummy = (p_PP_usage + p_setup_usage + p_mid_usage + p_death_usage)+0.000000001
    p_PP_usage = p_PP_usage/dummy
    p_mid_usage = p_mid_usage/dummy
    p_setup_usage = p_setup_usage/dummy
    p_death_usage = p_death_usage/dummy
    c = 0
    projection = [player,year,team,p_usage,p_AVG,p_SR,p_runs,p_wickets,p_PP_usage,p_mid_usage,p_setup_usage,p_death_usage,p_dots,p_ones,p_twos,p_threes,p_fours,p_sixes,p_xAVG,p_xSR]
    return projection

def batting_projection_comps(file,file2,player,year,logs):
    base_proj = batting_projection(file,file2,player,year)
    comps = mdist_bat(file,base_proj,player)
    projection = similarity_calc_bat(comps, player, year, base_proj[2])    
    c = 0; delta = []; comps_expected = []
    
    for x in comps:
        if(x[1] != "season"):
            y = batting_projection(file,file2,x[0],x[1])
            y.insert(3,x[3])
            comps_expected.append(y)
        if(x[1] == "season"): comps_expected.append(x)
    
    comps_expected_weighted = similarity_calc_bat(comps_expected, player, year, base_proj[2])
    
    for x in projection:
        if(c<3): delta.append(comps_expected_weighted[c])
        elif(comps_expected_weighted[c]==0): delta.append(1)
        else: delta.append(projection[c]/comps_expected_weighted[c])
        c = c + 1   
    
    c = 0; projection_new = []
    for x in base_proj:
        if(c<3 or c==20): projection_new.append(base_proj[c])
        else: projection_new.append(delta[c]*base_proj[c])
        c = c + 1
    
    sum_balls = (1/projection_new[4])+projection_new[12]+projection_new[13]+projection_new[14]+projection_new[15]+projection_new[16]+projection_new[17]
    sum_runs = projection_new[13]+2*projection_new[14]+3*projection_new[15]+4*projection_new[16]+6*projection_new[17]
    sum_usage = projection_new[8]+projection_new[9]+projection_new[10]+projection_new[11]
    
    dummy = projection_new[11] + projection_new[8] + projection_new[9] + projection_new[10]
    projection_new[11] = projection_new[11]/dummy
    projection_new[8] = projection_new[8]/dummy
    projection_new[9] = projection_new[9]/dummy
    projection_new[10] = projection_new[10]/dummy
    
    if (logs == 1):
        print("base projection")
        print(base_proj)
        print("comps weighted actual")
        print(projection)
        print("comps weighted projection")
        print(comps_expected_weighted)
        print("delta")
        print(delta)
        print("final projection")
        print(projection_new)
        print("RSAA,OAA")
        print(1.2*(projection_new[5]-projection_new[19])*projection_new[3],120*((1/projection_new[4])-(1/projection_new[18]))*projection_new[3])
        
    return projection_new

def batting_projection(df,df2,player,year):
    names = df['batsman'].values
    season = df['season'].values
    team = df['batting_team'].values
    usage = df['usage'].values
    wickets = df['outs_batsman'].values
    PP_usage = df['powerplay'].values
    mid_usage = df['middle'].values
    setup_usage = df['setup'].values
    death_usage = df['death'].values
    balls = df['balls_batsman'].values
    runs = df['runs_off_bat'].values
    dots = df['0s'].values
    ones = df['1s'].values
    twos = df['2s'].values
    threes = df['3s'].values
    fours = df['4s'].values
    sixes = df['6s'].values
    xRuns = df['xruns'].values
    xWickets = df['xwickets'].values
    bf_GP = df['bf_GP'].values
    avg_season = df2['Season'].values
    avg_runs = df2['runs/ball'].values
    avg_wickets = df2['wickets/ball'].values
    avg_dots = df2['0s/ball'].values
    avg_ones = df2['1s/ball'].values
    avg_twos = df2['2s/ball'].values
    avg_threes = df2['3s/ball'].values
    avg_fours = df2['4s/ball'].values
    avg_sixes = df2['6s/ball'].values
    #avg_extras = df2['extras/ball'].values
    #print(avg_season)
    c = 0; c2 = 0; curr_team = "Free Agent"; AVG = 0; SR = 0
    y1_usage = 0.000001; y1_wickets = 0.000001; y1_PP_usage = 0.000001; y1_mid_usage = 0.000001; y1_setup_usage = 0.000001; y1_death_usage = 0.000001; y1_balls = 0.000001;    y1_runs = 0.000001; y1_dots = 0.000001; y1_ones = 0.000001; y1_twos = 0.000001; y1_threes = 0.000001; y1_fours = 0.000001; y1_sixes = 0.000001
    y2_usage = 0.000001; y2_wickets = 0.000001; y2_PP_usage = 0.000001; y2_mid_usage = 0.000001; y2_setup_usage = 0.000001; y2_death_usage = 0.000001; y2_balls = 0.000001;    y2_runs = 0.000001; y2_dots = 0.000001; y2_ones = 0.000001; y2_twos = 0.000001; y2_threes = 0.000001; y2_fours = 0.000001; y2_sixes = 0.000001
    y3_usage = 0.000001; y3_wickets = 0.000001; y3_PP_usage = 0.000001; y3_mid_usage = 0.000001; y3_setup_usage = 0.000001; y3_death_usage = 0.000001; y3_balls = 0.000001;    y3_runs = 0.000001; y3_dots = 0.000001; y3_ones = 0.000001; y3_twos = 0.000001; y3_threes = 0.000001; y3_fours = 0.000001; y3_sixes = 0.000001
    y4_usage = 0.000001; y4_wickets = 0.000001; y4_PP_usage = 0.000001; y4_mid_usage = 0.000001; y4_setup_usage = 0.000001; y4_death_usage = 0.000001; y4_balls = 0.000001;    y4_runs = 0.000001; y4_dots = 0.000001; y4_ones = 0.000001; y4_twos = 0.000001; y4_threes = 0.000001; y4_fours = 0.000001; y4_sixes = 0.000001
    y5_usage = 0.000001; y5_wickets = 0.000001; y5_PP_usage = 0.000001; y5_mid_usage = 0.000001; y5_setup_usage = 0.000001; y5_death_usage = 0.000001; y5_balls = 0.000001;    y5_runs = 0.000001; y5_dots = 0.000001; y5_ones = 0.000001; y5_twos = 0.000001; y5_threes = 0.000001; y5_fours = 0.000001; y5_sixes = 0.000001 
    y6_usage = 0.000001; y6_wickets = 0.000001; y6_PP_usage = 0.000001; y6_mid_usage = 0.000001; y6_setup_usage = 0.000001; y6_death_usage = 0.000001; y6_balls = 0.000001;    y6_runs = 0.000001; y6_dots = 0.000001; y6_ones = 0.000001; y6_twos = 0.000001; y6_threes = 0.000001; y6_fours = 0.000001; y6_sixes = 0.000001 
    p_xAVG = 0; p_xSR = 0; y1_xRuns = 0; y2_xRuns = 0;y3_xRuns = 0;y4_xRuns = 0;y5_xRuns = 0;y6_xRuns = 0
    y1_xWickets = 0; y2_xWickets = 0;y3_xWickets = 0;y4_xWickets = 0;y5_xWickets = 0;y6_xWickets = 0
    y1_bf_gp =0; y2_bf_gp =0; y3_bf_gp =0; y4_bf_gp =0; y5_bf_gp =0; y6_bf_gp =0;
    y1_avg_runs = 0; y1_avg_wickets = 0; y1_avg_dots = 0; y1_avg_ones = 0; y1_avg_twos = 0; y1_avg_threes = 0; y1_avg_fours = 0; y1_avg_sixes = 0
    y2_avg_runs = 0; y2_avg_wickets = 0; y2_avg_dots = 0; y2_avg_ones = 0; y2_avg_twos = 0; y2_avg_threes = 0; y2_avg_fours = 0; y2_avg_sixes = 0
    y3_avg_runs = 0; y3_avg_wickets = 0; y3_avg_dots = 0; y3_avg_ones = 0; y3_avg_twos = 0; y3_avg_threes = 0; y3_avg_fours = 0; y3_avg_sixes = 0
    y4_avg_runs = 0; y4_avg_wickets = 0; y4_avg_dots = 0; y4_avg_ones = 0; y4_avg_twos = 0; y4_avg_threes = 0; y4_avg_fours = 0; y4_avg_sixes = 0
    y5_avg_runs = 0; y5_avg_wickets = 0; y5_avg_dots = 0; y5_avg_ones = 0; y5_avg_twos = 0; y5_avg_threes = 0; y5_avg_fours = 0; y5_avg_sixes = 0
    y6_avg_runs = 0; y6_avg_wickets = 0; y6_avg_dots = 0; y6_avg_ones = 0; y6_avg_twos = 0; y6_avg_threes = 0; y6_avg_fours = 0; y6_avg_sixes = 0
    
    for x in names:
        if(names[c]==player and season[c]==year-1):
            y1_usage = usage[c]
            y1_wickets = wickets[c]
            y1_PP_usage = PP_usage[c]
            y1_mid_usage = mid_usage[c]
            y1_setup_usage = setup_usage[c]
            y1_death_usage = death_usage[c]
            y1_balls = balls[c]
            y1_runs = runs[c]
            y1_dots = dots[c]
            y1_ones = ones[c]
            y1_twos = twos[c]
            y1_threes = threes[c]
            y1_fours = fours[c]
            y1_sixes = sixes[c]
            #y1_extras = extras[c]
            y1_xWickets = xWickets[c]
            y1_xRuns = xRuns[c]
            y1_bf_gp = bf_GP[c]
            curr_team = team[c]
        if(names[c]==player and season[c]==year-2):
            y2_usage = usage[c]
            y2_wickets = wickets[c]
            y2_PP_usage = PP_usage[c]
            y2_mid_usage = mid_usage[c]
            y2_setup_usage = setup_usage[c]
            y2_death_usage = death_usage[c]
            y2_balls = balls[c]
            y2_runs = runs[c]
            y2_dots = dots[c]
            y2_ones = ones[c]
            y2_twos = twos[c]
            y2_threes = threes[c]
            y2_fours = fours[c]
            y2_sixes = sixes[c]
            #y2_extras = extras[c]
            y2_xWickets = xWickets[c]
            y2_bf_gp = bf_GP[c]
            y2_xRuns = xRuns[c]
        if(names[c]==player and season[c]==year-3):
            y3_usage = usage[c]
            y3_wickets = wickets[c]
            y3_PP_usage = PP_usage[c]
            y3_mid_usage = mid_usage[c]
            y3_setup_usage = setup_usage[c]
            y3_death_usage = death_usage[c]
            y3_balls = balls[c]
            y3_runs = runs[c]
            y3_dots = dots[c]
            y3_ones = ones[c]
            y3_twos = twos[c]
            y3_threes = threes[c]
            y3_fours = fours[c]
            y3_sixes = sixes[c]
            #y3_extras = extras[c]
            y3_xWickets = xWickets[c]
            y3_bf_gp = bf_GP[c]
            y3_xRuns = xRuns[c]
        if(names[c]==player and season[c]==year-4):
            y4_usage = usage[c]
            y4_wickets = wickets[c]
            y4_PP_usage = PP_usage[c]
            y4_mid_usage = mid_usage[c]
            y4_setup_usage = setup_usage[c]
            y4_death_usage = death_usage[c]
            y4_balls = balls[c]
            y4_runs = runs[c]
            y4_dots = dots[c]
            y4_ones = ones[c]
            y4_twos = twos[c]
            y4_threes = threes[c]
            y4_fours = fours[c]
            y4_sixes = sixes[c]
            y4_xWickets = xWickets[c]
            y4_bf_gp = bf_GP[c]
            y4_xRuns = xRuns[c]
            #y4_extras = extras[c]
        if(names[c]==player and season[c]==year-5):
            y5_usage = usage[c]
            y5_wickets = wickets[c]
            y5_PP_usage = PP_usage[c]
            y5_mid_usage = mid_usage[c]
            y5_setup_usage = setup_usage[c]
            y5_death_usage = death_usage[c]
            y5_balls = balls[c]
            y5_runs = runs[c]
            y5_dots = dots[c]
            y5_ones = ones[c]
            y5_twos = twos[c]
            y5_threes = threes[c]
            y5_fours = fours[c]
            y5_sixes = sixes[c]
            y5_xWickets = xWickets[c]
            y5_xRuns = xRuns[c]
            y5_bf_gp = bf_GP[c]
            #y5_extras = extras[c]
        if(names[c]==player and season[c]==year-6):
            y6_usage = usage[c]
            y6_wickets = wickets[c]
            y6_PP_usage = PP_usage[c]
            y6_mid_usage = mid_usage[c]
            y6_setup_usage = setup_usage[c]
            y6_death_usage = death_usage[c]
            y6_balls = balls[c]
            y6_runs = runs[c]
            y6_dots = dots[c]
            y6_ones = ones[c]
            y6_twos = twos[c]
            y6_threes = threes[c]
            y6_fours = fours[c]
            y6_sixes = sixes[c]
            y6_xWickets = xWickets[c]
            y6_xRuns = xRuns[c]
            y6_bf_gp = bf_GP[c]
            #y6_extras = extras[c]
        c = c + 1
    
    for y in avg_season:
        if(avg_season[c2]==year-1):
            y1_avg_runs = avg_runs[c2]
            y1_avg_wickets = avg_wickets[c2]
            y1_avg_dots = avg_dots[c2]
            y1_avg_ones = avg_ones[c2]
            y1_avg_twos = avg_twos[c2]
            y1_avg_threes = avg_threes[c2]
            y1_avg_fours = avg_fours[c2]
            y1_avg_sixes = avg_sixes[c2]
            #y1_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-2):
            y2_avg_runs = avg_runs[c2]
            y2_avg_wickets = avg_wickets[c2]
            y2_avg_dots = avg_dots[c2]
            y2_avg_ones = avg_ones[c2]
            y2_avg_twos = avg_twos[c2]
            y2_avg_threes = avg_threes[c2]
            y2_avg_fours = avg_fours[c2]
            y2_avg_sixes = avg_sixes[c2]
            #y2_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-3):
            y3_avg_runs = avg_runs[c2]
            y3_avg_wickets = avg_wickets[c2]
            y3_avg_dots = avg_dots[c2]
            y3_avg_ones = avg_ones[c2]
            y3_avg_twos = avg_twos[c2]
            y3_avg_threes = avg_threes[c2]
            y3_avg_fours = avg_fours[c2]
            y3_avg_sixes = avg_sixes[c2]
            #y3_avg_extras = avg_extras[c2]    
        if(avg_season[c2]==year-4):
            y4_avg_runs = avg_runs[c2]
            y4_avg_wickets = avg_wickets[c2]
            y4_avg_dots = avg_dots[c2]
            y4_avg_ones = avg_ones[c2]
            y4_avg_twos = avg_twos[c2]
            y4_avg_threes = avg_threes[c2]
            y4_avg_fours = avg_fours[c2]
            y4_avg_sixes = avg_sixes[c2]
            #y4_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-5):
            y5_avg_runs = avg_runs[c2]
            y5_avg_wickets = avg_wickets[c2]
            y5_avg_dots = avg_dots[c2]
            y5_avg_ones = avg_ones[c2]
            y5_avg_twos = avg_twos[c2]
            y5_avg_threes = avg_threes[c2]
            y5_avg_fours = avg_fours[c2]
            y5_avg_sixes = avg_sixes[c2]
            #y5_avg_extras = avg_extras[c2]
        if(avg_season[c2]==year-6):
            y6_avg_runs = avg_runs[c2]
            y6_avg_wickets = avg_wickets[c2]
            y6_avg_dots = avg_dots[c2]
            y6_avg_ones = avg_ones[c2]
            y6_avg_twos = avg_twos[c2]
            y6_avg_threes = avg_threes[c2]
            y6_avg_fours = avg_fours[c2]
            y6_avg_sixes = avg_sixes[c2]
            #y6_avg_extras = avg_extras[c2]
        c2 = c2 + 1
        
    #print(y1_avg_runs,y2_avg_runs,y3_avg_runs,y4_avg_runs,y5_avg_runs,y6_avg_runs)
    if(y1_avg_runs==0):
        y1_avg_runs = y2_avg_runs
        y1_avg_wickets = y2_avg_wickets
        y1_avg_dots = y2_avg_dots
        y1_avg_ones = y2_avg_ones
        y1_avg_twos = y2_avg_twos
        y1_avg_threes = y2_avg_threes
        y1_avg_fours = y2_avg_fours
        y1_avg_sixes = y2_avg_sixes
    if(y2_avg_runs==0):
        y2_avg_runs = y1_avg_runs
        y2_avg_wickets = y1_avg_wickets
        y2_avg_dots = y1_avg_dots
        y2_avg_ones = y1_avg_ones
        y2_avg_twos = y1_avg_twos
        y2_avg_threes = y1_avg_threes
        y2_avg_fours = y1_avg_fours
        y2_avg_sixes = y1_avg_sixes
    if(y3_avg_runs==0):
        y3_avg_runs = y2_avg_runs
        y3_avg_wickets = y2_avg_wickets
        y3_avg_dots = y2_avg_dots
        y3_avg_ones = y2_avg_ones
        y3_avg_twos = y2_avg_twos
        y3_avg_threes = y2_avg_threes
        y3_avg_fours = y2_avg_fours
        y3_avg_sixes = y2_avg_sixes
    if(y4_avg_runs==0):
        y4_avg_runs = y3_avg_runs
        y4_avg_wickets = y3_avg_wickets
        y4_avg_dots = y3_avg_dots
        y4_avg_ones = y3_avg_ones
        y4_avg_twos = y3_avg_twos
        y4_avg_threes = y3_avg_threes
        y4_avg_fours = y3_avg_fours
        y4_avg_sixes = y3_avg_sixes
    if(y5_avg_runs==0):
        y5_avg_runs = y4_avg_runs
        y5_avg_wickets = y4_avg_wickets
        y5_avg_dots = y4_avg_dots
        y5_avg_ones = y4_avg_ones
        y5_avg_twos = y4_avg_twos
        y5_avg_threes = y4_avg_threes
        y5_avg_fours = y4_avg_fours
        y5_avg_sixes = y4_avg_sixes
    if(y6_avg_runs==0):
        y6_avg_runs = y5_avg_runs
        y6_avg_wickets = y5_avg_wickets
        y6_avg_dots = y5_avg_dots
        y6_avg_ones = y5_avg_ones
        y6_avg_twos = y5_avg_twos
        y6_avg_threes = y5_avg_threes
        y6_avg_fours = y5_avg_fours
        y6_avg_sixes = y5_avg_sixes       
    #print(y1_avg_runs,y2_avg_runs,y3_avg_runs,y4_avg_runs,y5_avg_runs,y6_avg_runs)
    
    w_balls = 8*y1_balls + 5*y2_balls + 4*y3_balls + 3*y4_balls + 2*y5_balls + y6_balls
    w_runs = 8*y1_runs + 5*y2_runs + 4*y3_runs +3*y4_runs + 2*y5_runs + y6_runs
    w_dots = 8*y1_dots + 5*y2_dots + 4*y3_dots +3*y4_dots + 2*y5_dots + y6_dots
    w_ones = 8*y1_ones + 5*y2_ones + 4*y3_ones +3*y4_ones + 2*y5_ones + y6_ones
    w_twos = 8*y1_twos + 5*y2_twos + 4*y3_twos +3*y4_twos + 2*y5_twos + y6_twos
    w_threes = 8*y1_threes + 5*y2_threes + 4*y3_threes +3*y4_threes + 2*y5_threes + y6_threes
    w_fours = 8*y1_fours + 5*y2_fours + 4*y3_fours +3*y4_fours + 2*y5_fours + y6_fours
    w_sixes = 8*y1_sixes + 5*y2_sixes + 4*y3_sixes +3*y4_sixes + 2*y5_sixes + y6_sixes
    w_wickets = 8*y1_wickets + 5*y2_wickets + 4*y3_wickets +3*y4_wickets + 2*y5_wickets + y6_wickets
    #w_extras = 8*y1_extras + 5*y2_extras + 4*y3_extras +3*y4_extras + 2*y5_extras + y6_extras
    w_PP_usage = 8*y1_PP_usage + 5*y2_PP_usage + 4*y3_PP_usage +3*y4_PP_usage + 2*y5_PP_usage + y6_PP_usage
    w_mid_usage = 8*y1_mid_usage + 5*y2_mid_usage + 4*y3_mid_usage +3*y4_mid_usage + 2*y5_mid_usage + y6_mid_usage
    w_setup_usage = 8*y1_setup_usage + 5*y2_setup_usage + 4*y3_setup_usage +3*y4_setup_usage + 2*y5_setup_usage + y6_setup_usage
    w_death_usage = 8*y1_death_usage + 5*y2_death_usage + 4*y3_death_usage +3*y4_death_usage + 2*y5_death_usage + y6_death_usage
    w_usage = 8*y1_usage + 5*y2_usage + 4*y3_usage +3*y4_usage + 2*y5_usage + y6_usage
    w_xruns = 8*y1_xRuns + 5*y2_xRuns + 4*y3_xRuns +3*y4_xRuns +2*y5_xRuns +y6_xRuns
    w_xwickets = 8*y1_xWickets + 5*y2_xWickets + 4*y3_xWickets +3*y4_xWickets + 2*y5_xWickets +y6_xWickets
    w_bf_gp = (8*y1_bf_gp + 5*y2_bf_gp + 4*y3_bf_gp + 3*y4_bf_gp + 2*y5_bf_gp + y6_bf_gp)
    #print(w_wickets)
    mr_runs = (800/w_balls)*(8*y1_balls*y1_avg_runs + 5*y2_balls*y2_avg_runs + 4*y3_balls*y3_avg_runs + 3*y4_balls*y4_avg_runs + 2*y5_balls*y5_avg_runs + y6_balls*y6_avg_runs)
    mr_dots = (800/w_balls)*(8*y1_balls*y1_avg_dots + 5*y2_balls*y2_avg_dots + 4*y3_balls*y3_avg_dots + 3*y4_balls*y4_avg_dots + 2*y5_balls*y5_avg_dots + y6_balls*y6_avg_dots)
    mr_ones = (800/w_balls)*(8*y1_balls*y1_avg_ones + 5*y2_balls*y2_avg_ones + 4*y3_balls*y3_avg_ones + 3*y4_balls*y4_avg_ones + 2*y5_balls*y5_avg_ones + y6_balls*y6_avg_ones)
    mr_twos = (800/w_balls)*(8*y1_balls*y1_avg_twos + 5*y2_balls*y2_avg_twos + 4*y3_balls*y3_avg_twos + 3*y4_balls*y4_avg_twos + 2*y5_balls*y5_avg_twos + y6_balls*y6_avg_twos)
    mr_threes = (800/w_balls)*(8*y1_balls*y1_avg_threes + 5*y2_balls*y2_avg_threes + 4*y3_balls*y3_avg_threes + 3*y4_balls*y4_avg_threes + 2*y5_balls*y5_avg_threes + y6_balls*y6_avg_threes)
    mr_fours = (800/w_balls)*(8*y1_balls*y1_avg_fours + 5*y2_balls*y2_avg_fours + 4*y3_balls*y3_avg_fours + 3*y4_balls*y4_avg_fours + 2*y5_balls*y5_avg_fours + y6_balls*y6_avg_fours)
    mr_sixes = (800/w_balls)*(8*y1_balls*y1_avg_sixes + 5*y2_balls*y2_avg_sixes + 4*y3_balls*y3_avg_sixes + 3*y4_balls*y4_avg_sixes + 2*y5_balls*y5_avg_sixes + y6_balls*y6_avg_sixes)
    mr_wickets = (800/w_balls)*(8*y1_balls*y1_avg_wickets + 5*y2_balls*y2_avg_wickets + 4*y3_balls*y3_avg_wickets + 3*y4_balls*y4_avg_wickets + 2*y5_balls*y5_avg_wickets + y6_balls*y6_avg_wickets)
    #mr_extras = (800/w_balls)*(8*y1_balls*y1_avg_extras + 5*y2_balls*y2_avg_extras + 4*y3_balls*y3_avg_extras + 3*y4_balls*y4_avg_extras + 2*y5_balls*y5_avg_extras + y6_balls*y6_avg_extras)
    #print(mr_wickets)
    if(y1_usage==0.000001): y1_usage = 0
    if(y2_usage==0.000001): y2_usage = 0
    if(y3_usage==0.000001): y3_usage = 0
    if(y4_usage==0.000001): y4_usage = 0
    if(y5_usage==0.000001): y5_usage = 0
    if(y6_usage==0.000001): y6_usage = 0
    #print(p_xAVG,p_xSR,w_balls)
    if(y1_usage==0 and y2_usage==0 and y3_usage==0 and y4_usage==0 and y5_usage==0 and y6_usage==0):
        p_usage = 0; p_bf_gp = 0
    else:
        p_usage = w_usage/(8*math.ceil(y1_usage) + 5*math.ceil(y2_usage) + 4*math.ceil(y3_usage) + 3*math.ceil(y4_usage) + 2*math.ceil(y5_usage) + math.ceil(y6_usage))
        p_bf_gp = w_bf_gp/(8*math.ceil(y1_usage) + 5*math.ceil(y2_usage) + 4*math.ceil(y3_usage) + 3*math.ceil(y4_usage) + 2*math.ceil(y5_usage) + math.ceil(y6_usage))
    
    #p_balls = 120*14*p_usage
    p_runs = (w_runs+mr_runs)/(800+w_balls)
    p_dots = (w_dots+mr_dots)/(800+w_balls)
    p_ones = (w_ones+mr_ones)/(800+w_balls)
    p_twos = (w_twos+mr_twos)/(800+w_balls)
    p_threes = (w_threes+mr_threes)/(800+w_balls)
    p_fours = (w_fours+mr_fours)/(800+w_balls)
    p_sixes = (w_sixes+mr_sixes)/(800+w_balls)
    #p_extras = (w_extras+mr_extras)/(800+w_balls)
    p_wickets = (w_wickets+mr_wickets)/(800+w_balls)
    dummy = (w_PP_usage + w_setup_usage + w_mid_usage + w_death_usage)/w_balls
    p_PP_usage = w_PP_usage/(w_balls*dummy)
    p_setup_usage = w_setup_usage/(w_balls*dummy)
    p_mid_usage = w_mid_usage/(w_balls*dummy)
    p_death_usage = w_death_usage/(w_balls*dummy)
    p_xAVG = w_balls/(w_xwickets+0.00000001)
    p_xSR = 100*w_xruns/w_balls
    
    if(p_usage == 0):
        AVG = 0
        SR = 0
    elif(p_wickets == 0):
        AVG = 999
    else:
        AVG = 1/p_wickets
        SR = p_runs*100
    projection = [player,year,curr_team,p_usage,AVG,SR,p_runs,p_wickets,p_PP_usage,p_mid_usage,p_setup_usage,p_death_usage,p_dots,p_ones,p_twos,p_threes,p_fours,p_sixes,p_xAVG,p_xSR,p_bf_gp]
    #print(p_wickets)
    return projection

def logs(x,y):
    print(bowling_projection(file,file2,x,y))
    print(batting_projection(file3,file4,x,y))
    #bowling_projection_comps(file,file2,x,y,1)
    #batting_projection_comps(file3,file4,x,y,1)
    #comps_dump(x,y)
    #comps_dump_bat(x,y)
    #mdist(file,bowling_projection(file,file2,x,y),unique_names)
    #mdist_bat(file3,batting_projection(file3,file4,x,y),unique_names2)
    print("logs dumped")

def multi_year(x,y):
    bats = [["batsman","season","team","RSAA","OAA","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR","bf_GP"]]
    bat_player = batting_projection(file3,file4,x,y)
    if(bat_player[3] > 0):
        a = factor*1.2*(bat_player[5]-bat_player[19])*bat_player[3] #100*(p_dummy[4]/p_dummy[18])
        b = factor*120*((1/bat_player[4])-(1/bat_player[18]))*bat_player[3] #100*(p_dummy[5]/p_dummy[19])
        bat_player.insert(3,a)
        bat_player.insert(4,b)
    #bats.append(bat_player,bat_player,bat_player,bat_player,bat_player)
    bats = bats + [bat_player] + [bat_player] + [bat_player] + [bat_player] + [bat_player]
    bats = pd.DataFrame(bats)
    bats.columns = bats.iloc[0];bats = bats.drop(0)
    bats['season'] = [y,y+1,y+2,y+3,y+4]
    
    bowls = [["bowler","season","team","RCAA","WTAA","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage","runs/ball","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","xECON","xSR","bb_GP"]]
    bowl_player = bowling_projection(file,file2,x,y)
    if(bowl_player[3] > 0):        
        b = factor*120*((1/bowl_player[5])-(1/bowl_player[20]))*bowl_player[3]
        a = factor*1.2*(bowl_player[4]-bowl_player[19])*bowl_player[3] + factor*6*b
        bowl_player.insert(3,a)
        bowl_player.insert(4,b)
    bowls = bowls + [bowl_player] + [bowl_player] + [bowl_player] + [bowl_player] + [bowl_player]
    bowls = pd.DataFrame(bowls)
    bowls.columns = bowls.iloc[0];bowls = bowls.drop(0)
    bowls['season'] = [y,y+1,y+2,y+3,y+4]
    
    bats = bats.apply(pd.to_numeric, errors='ignore')
    bowls = bowls.apply(pd.to_numeric, errors='ignore')
    (bats,bowls) = player_aging(bats.copy(),bowls.copy(),y)
    bats['RSAA'] = factor*1.2*(bats['SR']-bats['xSR'])*bats['usage']
    bats['OAA'] = factor*120*((1/bats['balls/wkt'])-(1/bats['xballs/wkt']))*bats['usage']
    bowls['WTAA'] = factor*120*((1/bowls['SR'])-(1/bowls['xSR']))*bowls['usage']
    bowls['RCAA'] = factor*1.2*(bowls['ECON']-bowls['xECON'])*bowls['usage'] - factor*6*bowls['WTAA']
    return bats,bowls

#bats,bowls = multi_year("V Kohli",2024)
#logs("V Kohli",2024)
#venue_projections = venue_projections()
(aa_bowl,aa_bat,missing_dob)=proj_dump()
