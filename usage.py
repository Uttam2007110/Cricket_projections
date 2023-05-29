# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 16:46:11 2022
estimating team strengths based on individual projections
@author: uttam ganti
"""

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from sklearn.linear_model import LinearRegression

game_sim = 0

def avg(bowler,file_name,item):
    total = []; total2 = []
    if(bowler == 1): k = 'bowling_team'
    else: k = 'batting_team'
    
    for x in item:
        a = x.split(";")[0] #team
        b = int(x.split(";")[1]) #season
        sublist = file_name[(file_name['season'] == int(b)) & (file_name[k] == a)]
        sublist = sublist.sort_values(by=['usage'],ascending=False)
        #if(bowler == 1):print(sublist)
        total.append(sublist['usage'].to_list())
        if(bowler != 1):total2.append(sublist['AVG'].to_list())
        if(bowler == 1):total2.append(sublist['wickets/ball'].to_list())
    
    bowling_usage = pd.DataFrame(total)
    bowling_usage = bowling_usage.fillna(0)
    bowling_wkts = pd.DataFrame(total2)
    bowling_wkts = bowling_wkts.fillna(0)
    return (bowling_usage,bowling_wkts)

def usage_corrected(bowler,file_name,values):
    team_names = np.unique(file_name['team'].values)
    
    for x in team_names:
        c = 0;dummy = 0;
        sublist = file_name[(file_name['team'] == x)]
        sublist = sublist.sort_values(by=['usage'],ascending=False)

        if(bowler == 1): 
            k = sublist.count()[0]
            factor = 1/sum(values[0:k])
            #print(x,k,factor)
        if(bowler == 0 and x != "Free Agent"):
            if(game_sim == 1):
                sublist = sublist.sort_values(by=5*['pp usage']+3*['mid usage']+['setup usage'],ascending=False)
                #print(sublist)
            k = sublist.count()[0]
        
        #if(bowler == 1):
            #print(sublist)
            #print(len(values))
            
        for y in sublist.index:
            if(x != "Free Agent" and bowler == 1 and k>5):
                if(c<len(values)):file_name['usage'][y] = min(values[c]*file_name['wickets/ball'][y],0.2)
                else : file_name['usage'][y] = 0
                dummy = dummy + file_name['usage'][y]
                c = c + 1
            if(x != "Free Agent" and bowler == 1 and k<=5):
                file_name['usage'][y] = 0.2
                dummy = dummy + file_name['usage'][y]
                c = c + 1
            if(x != "Free Agent" and bowler == 0):
                if(c<len(values)):file_name['usage'][y] = min((1+c/k)*values[c]*file_name['balls/wkt'][y],file_name['balls/wkt'][y]/120)
                else : file_name['usage'][y] = 0
                dummy = dummy + file_name['usage'][y]
                c = c + 1  
        
        for y in sublist.index:
            if(x != "Free Agent"): file_name['usage'][y] = file_name['usage'][y]/dummy
        #print(x,dummy,bowler)  
        
    return file_name

def analyse(u,w):
    c = 0; coeffs = []
    for k in u:
        y = np.array(u[c].tolist())
        x = np.array(w[c].tolist()).reshape((-1, 1))
        #print(y,x)
        model = LinearRegression(fit_intercept=False).fit(x,y)
        coeffs.append(model.coef_[0])
        #print(c,model.coef_[0],model.score(x,y))
        c = c + 1
    return coeffs

def bowls(file_bowl_input,file_bowl,concat):
    (usage_bowl,wkts_bowl) = avg(1,file_bowl_input,concat)
    #averages_bowl = usage_bowl.mean(axis=0)
    coeffs_bowl = analyse(usage_bowl,wkts_bowl)
    #return usage_corrected(1,file_bowl,averages_bowl)
    return usage_corrected(1,file_bowl,coeffs_bowl)    

def bats(file_bat_input,file_bat,concat):
    (usage_bat,wkts_bat) = avg(0,file_bat_input,concat)
    coeffs_bat = analyse(usage_bat,wkts_bat)
    #print(coeffs_bat)
    return usage_corrected(0,file_bat,coeffs_bat)

def calc_agg(f_bat,f_bowl):
    summary = [["Team","runs bat","runs bowl","NRR","Wins"]]
    extras= (f_bowl['usage']*f_bowl['extras/ball']*120).sum()/f_bowl['usage'].sum()
    team_names = np.unique(f_bowl['team'].values)
    
    for x in team_names:
        runs_bat = ((f_bat.loc[(f_bat['team']==x),'usage']*f_bat.loc[(f_bat['team']==x),'runs/ball']).sum()*120)/(f_bat.loc[(f_bat['team']==x),'usage'].sum()) 
        lg_runs_bat = ((f_bat.loc[(f_bat['team']==x),'usage']*f_bat.loc[(f_bat['team']==x),'xSR']).sum()*1.2)/(f_bat.loc[(f_bat['team']==x),'usage'].sum())
        runs_bowl = ((f_bowl.loc[(f_bowl['team']==x),'usage']*f_bowl.loc[(f_bowl['team']==x),'runs/ball']).sum()*120)/(f_bowl.loc[(f_bowl['team']==x),'usage'].sum())
        lg_runs_bowl = ((f_bowl.loc[(f_bowl['team']==x),'usage']*f_bowl.loc[(f_bowl['team']==x),'xECON']).sum()*20)/(f_bowl.loc[(f_bowl['team']==x),'usage'].sum())
        adj_runs = runs_bat + extras
        wins = (adj_runs**15.5)/((adj_runs**15.5)+(runs_bowl**15.5))
        summary.append([x,adj_runs,runs_bowl,(adj_runs-runs_bowl)/20,wins])
        
    summary = pd.DataFrame(summary)
    summary.columns = summary.iloc[0];summary = summary.drop(0)
    print("total league wins",summary['Wins'].sum()-summary.loc[(summary['Team']=="Free Agent"),'Wins'].sum())
    summary = summary.sort_values(by=['Wins'],ascending=False)
    return summary

def balance(file_batting,file_bowling,display,fac):
    
    file_bt = file_batting[file_batting.team != "Free Agent"]
    file_bwl = file_bowling[file_bowling.team != "Free Agent"]
    runs_bat = (file_bt['usage']*file_bt['runs/ball']).sum()/file_bt['usage'].sum()
    dots_bat = (file_bt['usage']*file_bt['dots/ball']).sum()/file_bt['usage'].sum()
    ones_bat = (file_bt['usage']*file_bt['1s/ball']).sum()/file_bt['usage'].sum()
    twos_bat = (file_bt['usage']*file_bt['2s/ball']).sum()/file_bt['usage'].sum()
    threes_bat = (file_bt['usage']*file_bt['3s/ball']).sum()/file_bt['usage'].sum()
    fours_bat = (file_bt['usage']*file_bt['4s/ball']).sum()/file_bt['usage'].sum()
    sixes_bat = (file_bt['usage']*file_bt['6s/ball']).sum()/file_bt['usage'].sum()
    wickets_bat = (file_bt['usage']*file_bt['wickets/ball']).sum()/file_bt['usage'].sum()
    lg_runs_bat = ((1/100)*file_bt['usage']*file_bt['xSR']).sum()/file_bt['usage'].sum()
    lg_wickets_bat = (file_bt['usage']*1/(file_bt['xballs/wkt'])).sum()/file_bt['usage'].sum()
    
    runs_bowl= (file_bwl['usage']*file_bwl['runs/ball']).sum()/file_bwl['usage'].sum()
    lg_runs_bowl = ((1/6)*file_bwl['usage']*file_bwl['xECON']).sum()/file_bwl['usage'].sum()
    extras= (file_bwl['usage']*file_bwl['extras/ball']).sum()/file_bwl['usage'].sum()
    dots_bowl = (file_bwl['usage']*file_bwl['dots/ball']).sum()/file_bwl['usage'].sum()
    ones_bowl = (file_bwl['usage']*file_bwl['1s/ball']).sum()/file_bwl['usage'].sum()
    twos_bowl = (file_bwl['usage']*file_bwl['2s/ball']).sum()/file_bwl['usage'].sum()
    threes_bowl = (file_bwl['usage']*file_bwl['3s/ball']).sum()/file_bwl['usage'].sum()
    fours_bowl = (file_bwl['usage']*file_bwl['4s/ball']).sum()/file_bwl['usage'].sum()
    sixes_bowl = (file_bwl['usage']*file_bwl['6s/ball']).sum()/file_bwl['usage'].sum()
    wickets_bowl = (file_bwl['usage']*file_bwl['wickets/ball']).sum()/file_bwl['usage'].sum()
    lg_wickets_bowl = (file_bwl['usage']*1/(file_bwl['xSR'])).sum()/file_bwl['usage'].sum()
    agg_runs_bat = ones_bat+2*twos_bat+3*threes_bat+4*fours_bat+6*sixes_bat
    agg_runs_bowl = ones_bowl+2*twos_bowl+3*threes_bowl+4*fours_bowl+6*sixes_bowl
    
    adj_dots = (dots_bat + dots_bowl)/2
    adj_ones = (ones_bat + ones_bowl)/2
    adj_twos = (twos_bat + twos_bowl)/2
    adj_threes = (threes_bat + threes_bowl)/2
    adj_fours = (fours_bat + fours_bowl)/2
    adj_sixes = (sixes_bat + sixes_bowl)/2
    adj_wickets = (wickets_bat + wickets_bowl)/2
    adj_runs = adj_ones + 2*adj_twos+ 3*adj_threes + 4*adj_fours + 6*adj_sixes
    
    if(display == 1):
        print("------------------------------------------------------")
        print("usage bat",file_bt['usage'].sum())
        print("runs scored",runs_bat)
        print("agg runs",agg_runs_bat)
        print("dots",dots_bat)
        print("ones",ones_bat)
        print("twos",twos_bat)
        print("threes",threes_bat)
        print("fours",fours_bat)
        print("sixes",sixes_bat)
        print("wickets",wickets_bat)
        print("xruns scored",lg_runs_bat)
        print("xwickets",lg_wickets_bat)
        print("------------------------------------------------------")
        print("usage bowl",file_bwl['usage'].sum())
        print("runs conceded",runs_bowl)
        print("agg runs conceded",agg_runs_bowl)
        print("dots",dots_bowl)
        print("ones",ones_bowl)
        print("twos",twos_bowl)
        print("threes",threes_bowl)
        print("fours",fours_bowl)
        print("sixes",sixes_bowl)
        print("wickets",wickets_bowl)
        print("xruns conceded",lg_runs_bowl)
        print("xwickets",lg_wickets_bowl)
        print("extras",extras)
        print("------------------------------------------------------")
    
    for c in file_batting.index:
        file_batting['dots/ball'][c] = file_batting['dots/ball'][c]*(adj_dots/dots_bat)
        file_batting['1s/ball'][c] = file_batting['1s/ball'][c]*(adj_ones/ones_bat)
        file_batting['2s/ball'][c] = file_batting['2s/ball'][c]*(adj_twos/twos_bat)
        file_batting['3s/ball'][c] = file_batting['3s/ball'][c]*(adj_threes/threes_bat)
        file_batting['4s/ball'][c] = file_batting['4s/ball'][c]*(adj_fours/fours_bat)
        file_batting['6s/ball'][c] = file_batting['6s/ball'][c]*(adj_sixes/sixes_bat)
        file_batting['wickets/ball'][c] = file_batting['wickets/ball'][c]*(adj_wickets/wickets_bat)
        file_batting['xSR'][c] = file_batting['xSR'][c]*adj_runs/lg_runs_bat
        file_batting['xballs/wkt'][c] = file_batting['xballs/wkt'][c]*lg_wickets_bat/adj_wickets
        file_batting['balls/wkt'][c] = 1/file_batting['wickets/ball'][c]
        file_batting['runs/ball'][c] = file_batting['1s/ball'][c] + 2*file_batting['2s/ball'][c] + 3*file_batting['3s/ball'][c] + 4*file_batting['4s/ball'][c] + 6*file_batting['6s/ball'][c]
        file_batting['SR'][c] = 100*file_batting['runs/ball'][c]
        file_batting['RSAA'][c] = fac*1.2*(file_batting['SR'][c]-file_batting['xSR'][c])*file_batting['usage'][c]
        file_batting['OAA'][c] = fac*120*(1/file_batting['balls/wkt'][c]-1/file_batting['xballs/wkt'][c])*file_batting['usage'][c]
     
    for c in file_bowling.index:
        file_bowling['dots/ball'][c] = file_bowling['dots/ball'][c]*(adj_dots/dots_bowl)
        file_bowling['1s/ball'][c] = file_bowling['1s/ball'][c]*(adj_ones/ones_bowl)
        file_bowling['2s/ball'][c] = file_bowling['2s/ball'][c]*(adj_twos/twos_bowl)
        file_bowling['3s/ball'][c] = file_bowling['3s/ball'][c]*(adj_threes/threes_bowl)
        file_bowling['4s/ball'][c] = file_bowling['4s/ball'][c]*(adj_fours/fours_bowl)
        file_bowling['6s/ball'][c] = file_bowling['6s/ball'][c]*(adj_sixes/sixes_bowl)
        file_bowling['wickets/ball'][c] = file_bowling['wickets/ball'][c]*(adj_wickets/wickets_bowl)
        file_bowling['xSR'][c] = file_bowling['xSR'][c]*lg_wickets_bowl/adj_wickets
        file_bowling['xECON'][c] = file_bowling['xECON'][c]*(adj_runs+extras)/lg_runs_bowl
        file_bowling['runs/ball'][c] = file_bowling['extras/ball'][c]+ file_bowling['1s/ball'][c] + 2*file_bowling['2s/ball'][c] + 3*file_bowling['3s/ball'][c] + 4*file_bowling['4s/ball'][c] + 6*file_bowling['6s/ball'][c]
        file_bowling['ECON'][c] = 6*file_bowling['runs/ball'][c]
        file_bowling['SR'][c] = 1/file_bowling['wickets/ball'][c]
        file_bowling['RCAA'][c] = fac*20*(file_bowling['ECON'][c]-file_bowling['xECON'][c])*file_bowling['usage'][c]
        file_bowling['WTAA'][c] = fac*120*(1/file_bowling['SR'][c]-1/file_bowling['xSR'][c])*file_bowling['usage'][c]
        
    return (file_batting,file_bowling)

def h2h_alt(i_file,i_file2,flag):
    global game_sim
    game_sim = flag
    file_bowl_input = pd.read_excel(i_file,'bowling seasons')
    file_bat_input = pd.read_excel(i_file,'batting seasons')
    f_bowl = pd.read_excel(i_file2,'MDist bowl')
    f_bat = pd.read_excel(i_file2,'MDist bat')
    
    concat = [];
    for (x,y) in zip(file_bowl_input['bowling_team'].values,file_bowl_input['season'].values):
        concat.append(x+";"+str(y))
    concat = np.unique(concat)
        
    f_bowl_adj = bowls(file_bowl_input,f_bowl,concat)
    f_bat_adj = bats(file_bat_input,f_bat,concat)
    (f_bat_adj,f_bowl_adj) = balance(f_bat_adj,f_bowl_adj,0,1)
    #print(calc_agg(f_bat_adj,f_bowl_adj))
    return (calc_agg(f_bat_adj,f_bowl_adj),f_bat_adj,f_bowl_adj)

def team_projections():
    input_file = "C:/Users/Subramanya.Ganti/Downloads/cricket/ipl_summary.xlsx"
    file_bowl_input = pd.read_excel(input_file,'bowling seasons')
    file_bat_input = pd.read_excel(input_file,'batting seasons')

    input_file2 = "C:/Users/Subramanya.Ganti/Downloads/cricket/ipl_projections.xlsx"
    f_bowl = pd.read_excel(input_file2,'MDist bowl')
    f_bat = pd.read_excel(input_file2,'MDist bat')
    
    concat = [];
    for (x,y) in zip(file_bowl_input['bowling_team'].values,file_bowl_input['season'].values):
        concat.append(x+";"+str(y))
    concat = np.unique(concat)
        
    f_bowl_adj = bowls(file_bowl_input,f_bowl,concat)
    f_bat_adj = bats(file_bat_input,f_bat,concat)
    (f_bat_adj,f_bowl_adj) = balance(f_bat_adj,f_bowl_adj,0,1)
    table = calc_agg(f_bat_adj,f_bowl_adj)
    #print(table)
    table = table.apply(pd.to_numeric, errors='ignore')
    return (f_bat_adj,f_bowl_adj,table)
    
#(bat,bowl,table) = team_projections()
