# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 19:25:55 2022
author: uttam ganti
projecting ipl performances based on past seasons
"""
import numpy as np
import pandas as pd
import math
import datetime
from usage import *
pd.options.mode.chained_assignment = None  # default='warn'

comp = 'odi'
proj_year = 2024
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'

if(comp=='hundred' or comp=='hundredw'):
    factor = (5/6); #hundred
elif(comp=='odi' or comp=='odiw' or comp=='odiq' or comp=='rlc'):
    factor = 2.5;   #odi
elif(comp=='tests'):
    factor = 11.25; #test
else:
    factor = 1;     #assume its a t20 by default

input_file = f'{path}/{comp}_summary.xlsx' # the output of generate.py
dumps_file = f"{path}/{comp}_comps.xlsx"
output_file = f"{path}/{comp}_projections.xlsx"

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

#file0 = pd.read_excel(input_file,'Sheet1')
file = pd.read_excel(input_file,'bowling seasons')
file2 = pd.read_excel(input_file,'bowling year')
file3 = pd.read_excel(input_file,'batting seasons')
file4 = pd.read_excel(input_file,'batting year')
proxy_bowl = []; proxy_bat = []

for (x,y) in zip(file['bowler'].values,file['season'].values):
    proxy_bowl.append(18+math.sqrt(file.loc[(file['bowler']==x)&(file['season']<y),'balls_bowler'].sum())/5)
    
for (x,y) in zip(file3['batsman'].values,file3['season'].values):
    proxy_bat.append(18+math.sqrt(file3.loc[(file3['batsman']==x)&(file3['season']<y),'balls_batsman'].sum())/5)

file['age_proxy'] = proxy_bowl
file3['age_proxy'] = proxy_bat
name0 = file['bowler'].values
unique_names = unique(name0)
name00 = file3['batsman'].values
unique_names2 = unique(name00)

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
        p_xSR = w_balls/p_xSR
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

def proj_dump():
    lolcow = [["bowler","season","team","RCAA","WTAA","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage","runs/ball","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","xECON","xSR","bb_GP"]]
    lolcow2 = [["bowler","season","team","RCAA","WTAA","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage","runs/ball","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","xECON","xSR","bb_GP"]]
    lolcow4 = [["batsman","season","team","RSAA","OAA","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR","bf_GP"]]
    lolcow5 = [["batsman","season","team","RSAA","OAA","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xballs/wkt","xSR","bf_GP"]]
    lolcow3 = [["bowler","season","team","RCAA","WTAA","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage"]]
    
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
    lol0 = pd.DataFrame(lolcow)
    lol0.columns = lol0.iloc[0];lol0 = lol0.drop(0)
    
    for x in lol0['bowler']:
        now = datetime.datetime.now()
        print(x,proj_year,now.time())
        p_dummy = bowling_projection_comps(file,file2,x,proj_year,0)
        #print(x,p_dummy)
        if(p_dummy[3] > 0):
            a = 20*(p_dummy[4]-p_dummy[19])*p_dummy[3] #100*(p_dummy[19]/p_dummy[4])
            b = 120*((1/p_dummy[5])-(1/p_dummy[20]))*p_dummy[3]#100*(p_dummy[20]/p_dummy[5])
            p_dummy.insert(3,a)
            p_dummy.insert(4,b)
            lolcow2.append(p_dummy)           
                     
    print("bowling projections dumped")
    now = datetime.datetime.now()
    print(now.time())
    
    for x in unique_names2:
        p_dummy = batting_projection(file3,file4,x,proj_year)
        if(p_dummy[3] > 0):
            a = factor*1.2*(p_dummy[5]-p_dummy[19])*p_dummy[3] #100*(p_dummy[4]/p_dummy[18])
            b = factor*120*((1/p_dummy[4])-(1/p_dummy[18]))*p_dummy[3] #100*(p_dummy[5]/p_dummy[19])
            p_dummy.insert(3,a)
            p_dummy.insert(4,b)
            lolcow4.append(p_dummy)  
            
    lol3 = pd.DataFrame(lolcow4)
    lol3 = pd.DataFrame(lolcow4)
    lol3.columns = lol3.iloc[0];lol3 = lol3.drop(0)
     
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
    
    lol = pd.DataFrame(lolcow)
    lol.columns = lol.iloc[0];lol = lol.drop(0)
    lol2 = pd.DataFrame(lolcow2)
    lol2.columns = lol2.iloc[0];lol2 = lol2.drop(0)
    lol4 = pd.DataFrame(lolcow4)
    lol4.columns = lol4.iloc[0];lol4 = lol4.drop(0)
    lol5 = pd.DataFrame(lolcow5)
    lol5.columns = lol5.iloc[0];lol5 = lol5.drop(0)
    
    concat = [];
    for (x,y) in zip(file['bowling_team'].values,file['season'].values):
        concat.append(x+";"+str(y))
    concat = np.unique(concat)
        
    lol = bowls(file,lol,concat,factor)     #for usage adjustment
    #print(lol)
    lol4 = bats(file3,lol4,concat,factor)   #for usage adjustment
    (lol4,lol) = balance(lol4,lol,0,factor)
    print("Marcel based table")
    marcel_table = calc_agg(lol4,lol,factor)
    
    lol2 = bowls(file,lol2,concat,factor)     #for usage adjustment
    lol5 = bats(file3,lol5,concat,factor)   #for usage adjustment
    (lol5,lol2) = balance(lol5,lol2,0,factor)
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
                
        final.append([x,p_team,p_team])
        
    final = pd.DataFrame(final)
    final.columns = final.iloc[0];final = final.drop(0)
    final = final.fillna(0) 
    
    with pd.ExcelWriter(output_file) as writer:        
        mdist_table.to_excel(writer, sheet_name="MDist Table", index=False)
        lol2.to_excel(writer, sheet_name="MDist bowl", index=False)
        lol5.to_excel(writer, sheet_name="MDist bat", index=False)
        final.to_excel(writer, sheet_name="Team", index=False)
        marcel_table.to_excel(writer, sheet_name="Marcel Table", index=False)
        lol.to_excel(writer, sheet_name="Marcel bowl", index=False)       
        lol4.to_excel(writer, sheet_name="Marcel bat", index=False)        
            
    print("batting projections dumped")
    now = datetime.datetime.now()
    print(now.time())

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
        
def bowling_projection_comps(file,file2,player,year,logs):
    base_proj = bowling_projection(file,file2,player,year)
    comps = mdist(file,base_proj,player)
    projection = similarity_calc(comps, player, year, base_proj[2])    
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
    #print(bowling_projection(file,file2,x,y))
    #print(batting_projection(file3,file4,x,y))
    bowling_projection_comps(file,file2,x,y,1)
    #batting_projection_comps(file3,file4,x,y,1)
    #comps_dump(x,y)
    #comps_dump_bat(x,y)
    #mdist(file,bowling_projection(file,file2,x,y),unique_names)
    #mdist_bat(file3,batting_projection(file3,file4,x,y),unique_names2)
    print("logs dumped")

#logs("C Green",2024)
proj_dump()
