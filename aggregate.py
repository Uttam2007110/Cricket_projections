# -*- coding: utf-8 -*-
"""
Created on Mon Aug 7 16:56:36 2023
convert stats from one league to another and create an aggregate file
@author: Subramanya.Ganti
"""

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

base_comp = 'hundredw'
compm = ['bbl','ipl','lpl','sa20','hundred','bpl','blast','mlc','psl']   #blast and smat need to be adjusted
compw = ['wbbl','wpl','hundredw','t20iw']

if(base_comp in compw): comp = compw
else: comp = compm

path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'
input_file = f'{path}/summary/{base_comp}_summary.xlsx'
output_file = f"{path}/summary/{base_comp}_aggregate.xlsx"
i=0

if(base_comp=='hundred' or base_comp=='hundredw'):
    factor = (5/6); #hundred
elif(base_comp=='odi' or base_comp=='odiw' or base_comp=='odiq' or base_comp=='rlc'):
    factor = 2.5;   #odi
elif(base_comp=='tests'):
    factor = 11.25; #test
else:
    factor = 1;     #assume its a t20 by default
    
bowl = pd.read_excel(input_file,'bowling seasons')
bat = pd.read_excel(input_file,'batting seasons')
team_bat = bat.loc[:,'batsman':'batting_team']
team_bat.rename(columns = {'batsman':'player','batting_team':'team'}, inplace = True)
team_bowl = bowl.loc[:,'bowler':'bowling_team']
team_bowl.rename(columns = {'bowler':'player','bowling_team':'team'}, inplace = True)
team = pd.concat([team_bat, team_bowl], ignore_index=True, sort=False)
bat['bf_GP'] = bat['balls_batsman']/(bat['bf_GP']+0.00000001)
bowl['bb_GP'] = bowl['balls_bowler']/(bowl['bb_GP']+0.00000001)
bat_all = [bat]
bowl_all = [bowl]

while i<len(comp):
    if(comp[i]!=base_comp):
        comp_file = f'{path}/summary/{comp[i]}_summary.xlsx'
        comp_bowl = pd.read_excel(comp_file,'bowling seasons')
        comp_bat = pd.read_excel(comp_file,'batting seasons')
        print(base_comp,comp[i])
        #print("SR",bat['xruns'].sum()/bat['balls_batsman'].sum(),"balls/wkt",bat['balls_batsman'].sum()/bat['outs_batsman'].sum())
        #print("SR",comp_bat['xruns'].sum()/comp_bat['balls_batsman'].sum(),"balls/wkt",comp_bat['balls_batsman'].sum()/comp_bat['outs_batsman'].sum())
        runs_f = (bat['xruns'].sum()/bat['balls_batsman'].sum())/(comp_bat['xruns'].sum()/comp_bat['balls_batsman'].sum())
        outs_f = (bat['balls_batsman'].sum()/bat['outs_batsman'].sum())/(comp_bat['balls_batsman'].sum()/comp_bat['outs_batsman'].sum())
        print("batting",runs_f,outs_f)
        comp_bat['runs_off_bat'] = comp_bat['runs_off_bat'] * runs_f
        comp_bat['xruns'] = comp_bat['xruns'] * runs_f
        comp_bat['runs/ball'] = comp_bat['runs/ball'] * runs_f
        comp_bat['SR'] = comp_bat['SR'] * runs_f
        comp_bat['xSR'] = comp_bat['xSR'] * runs_f
        comp_bat['outs_batsman'] = comp_bat['outs_batsman'] * (1/outs_f)
        comp_bat['xwickets'] = comp_bat['xwickets'] * (1/outs_f)
        comp_bat['AVG'] = comp_bat['AVG'] * outs_f
        comp_bat['xAVG'] = comp_bat['xAVG'] * outs_f
        comp_bat['wickets/ball'] = comp_bat['wickets/ball'] * (1/outs_f)
        comp_bat['1s'] = comp_bat['1s'] * runs_f
        comp_bat['2s'] = comp_bat['2s'] * runs_f
        comp_bat['3s'] = comp_bat['3s'] * runs_f
        comp_bat['4s'] = comp_bat['4s'] * runs_f
        comp_bat['6s'] = comp_bat['6s'] * runs_f
        comp_bat['balls_batsman'] = comp_bat['runs_off_bat']/(comp_bat['runs/ball']+0.0000001)
        comp_bat['bf_GP'] = comp_bat['balls_batsman']/comp_bat['bf_GP']
        comp_bat['0s'] = comp_bat['balls_batsman'] - (comp_bat['1s']+comp_bat['2s']+comp_bat['3s']+comp_bat['4s']+comp_bat['6s']+comp_bat['outs_batsman'])
        comp_bat.loc[comp_bat['0s']<0,'0s']=0
        if(comp[i]=='hundred' or comp[i]=='hundredw'): comp_bat['bf_GP'] = comp_bat['bf_GP'] *(5/6)
        elif(base_comp=='hundred' or base_comp=='hundredw'): comp_bat['bf_GP'] = comp_bat['bf_GP'] / (5/6)
        bat_all.append(comp_bat)
        
        rc_f = (bowl['xruns'].sum()/bowl['balls_bowler'].sum())/(comp_bowl['xruns'].sum()/comp_bowl['balls_bowler'].sum())
        wickets_f = (bowl['balls_bowler'].sum()/bowl['outs_bowler'].sum())/(comp_bowl['balls_bowler'].sum()/comp_bowl['outs_bowler'].sum())
        print("bowling",rc_f,wickets_f)
        comp_bowl['runs_off_bat'] = comp_bowl['runs_off_bat'] * rc_f
        comp_bowl['xruns'] = comp_bowl['xruns'] * rc_f
        comp_bowl['runs/ball'] = comp_bowl['runs/ball'] * rc_f
        comp_bowl['ECON'] = comp_bowl['ECON'] * rc_f
        comp_bowl['xECON'] = comp_bowl['xECON'] * rc_f
        comp_bowl['outs_bowler'] = comp_bowl['outs_bowler'] * (1/wickets_f)
        comp_bowl['xwickets'] = comp_bowl['xwickets'] * (1/wickets_f)
        comp_bowl['SR'] = comp_bowl['SR'] * wickets_f
        comp_bowl['xSR'] = comp_bowl['xSR'] * wickets_f
        comp_bowl['wickets/ball'] = comp_bowl['wickets/ball'] * (1/wickets_f)        
        comp_bowl['1s'] = comp_bowl['1s'] * rc_f
        comp_bowl['2s'] = comp_bowl['2s'] * rc_f
        comp_bowl['3s'] = comp_bowl['3s'] * rc_f
        comp_bowl['4s'] = comp_bowl['4s'] * rc_f
        comp_bowl['6s'] = comp_bowl['6s'] * rc_f
        comp_bowl['extras'] = comp_bowl['extras'] * rc_f
        comp_bowl['balls_bowler'] = comp_bowl['runs_off_bat']/(comp_bowl['runs/ball']+0.0000001)
        comp_bowl['bb_GP'] = comp_bowl['balls_bowler']/comp_bowl['bb_GP']
        comp_bowl['0s'] = comp_bowl['balls_bowler'] - (comp_bowl['1s']+comp_bowl['2s']+comp_bowl['3s']+comp_bowl['4s']+comp_bowl['6s']+comp_bowl['outs_bowler'])
        comp_bowl.loc[comp_bowl['0s']<0,'0s']=0
        if(comp[i]=='hundred' or comp[i]=='hundredw'): comp_bowl['bb_GP'] = comp_bowl['bb_GP'] *(5/6)
        elif(base_comp=='hundred' or base_comp=='hundredw'): comp_bowl['bb_GP'] = comp_bowl['bb_GP'] / (5/6)
        bowl_all.append(comp_bowl)
        
    i+=1

bat_all = pd.concat(bat_all)
bowl_all = pd.concat(bowl_all)

bat_all = bat_all.groupby(['batsman','season'], as_index=False).sum()
bat_all.insert(loc=2, column='batting_team', value='Free Agent')
for x in bat_all.values:
    try:
        bat_all.loc[(bat_all['batsman']==x[0])&(bat_all['season']==x[1]),'batting_team'] = team.loc[(team['player']==x[0])&(team['season']==x[1]),'team'].values[0]
    except IndexError:
        bat_all.loc[(bat_all['batsman']==x[0])&(bat_all['season']==x[1]),'batting_team'] = "Free Agent"
    
bowl_all = bowl_all.groupby(['bowler','season'], as_index=False).sum()
bowl_all.insert(loc=2, column='bowling_team', value='Free Agent')
for x in bowl_all.values:
    try:
        bowl_all.loc[(bowl_all['bowler']==x[0])&(bowl_all['season']==x[1]),'bowling_team'] = team.loc[(team['player']==x[0])&(team['season']==x[1]),'team'].values[0]
    except IndexError:
        bowl_all.loc[(bowl_all['bowler']==x[0])&(bowl_all['season']==x[1]),'bowling_team'] = "Free Agent"

bat_all['runs/ball'] = bat_all['runs_off_bat']/(bat_all['balls_batsman']+0.000001)
bat_all['0s/ball'] = bat_all['0s']/(bat_all['balls_batsman']+0.000001)
bat_all['1s/ball'] = bat_all['1s']/(bat_all['balls_batsman']+0.000001)
bat_all['2s/ball'] = bat_all['2s']/(bat_all['balls_batsman']+0.000001)
bat_all['3s/ball'] = bat_all['3s']/(bat_all['balls_batsman']+0.000001)
bat_all['4s/ball'] = bat_all['4s']/(bat_all['balls_batsman']+0.000001)
bat_all['6s/ball'] = bat_all['6s']/(bat_all['balls_batsman']+0.000001)
bat_all['wickets/ball'] = bat_all['outs_batsman']/(bat_all['balls_batsman']+0.000001)
bat_all.loc[bat_all['wickets/ball']>1,'wickets/ball']=1
bat_all['PP usage'] = bat_all['powerplay']/(bat_all['balls_batsman']+0.000001)
bat_all['mid usage'] = bat_all['middle']/(bat_all['balls_batsman']+0.000001)
bat_all['setup usage'] = bat_all['setup']/(bat_all['balls_batsman']+0.000001)
bat_all['death usage'] = bat_all['death']/(bat_all['balls_batsman']+0.000001)
bat_all['PP usage'] = bat_all['PP usage']/(bat_all['PP usage']+bat_all['mid usage']+bat_all['setup usage']+bat_all['death usage'])
bat_all['mid usage'] = bat_all['mid usage']/(bat_all['PP usage']+bat_all['mid usage']+bat_all['setup usage']+bat_all['death usage'])
bat_all['setup usage'] = bat_all['setup usage']/(bat_all['PP usage']+bat_all['mid usage']+bat_all['setup usage']+bat_all['death usage'])
bat_all['death usage'] = bat_all['death usage']/(bat_all['PP usage']+bat_all['mid usage']+bat_all['setup usage']+bat_all['death usage'])
bat_all['bf_GP'] = bat_all['balls_batsman']/(bat_all['bf_GP']+0.00000001)
bat_all['AVG'] = 1/bat_all['wickets/ball']
bat_all['SR'] = 100*bat_all['runs/ball']
bat_all['xAVG'] = bat_all['balls_batsman']/bat_all['xwickets']
bat_all['xSR'] = 100*bat_all['xruns']/(bat_all['balls_batsman']+0.000001)
bat_all.loc[bat_all['AVG']>bat_all['runs_off_bat'],'AVG']=bat_all['runs_off_bat']
bat_all.loc[bat_all['xSR']>600,'xSR']=600
bat_all['usage'] =bat_all['bf_GP']/(120*factor)
bat_all['RSAA'] = 1.2*(bat_all['SR']-bat_all['xSR'])*bat_all['usage']*factor

bowl_all['runs/ball'] = bowl_all['runs_off_bat']/(bowl_all['balls_bowler']+0.000001)
bowl_all['0s/ball'] = bowl_all['0s']/(bowl_all['balls_bowler']+0.000001)
bowl_all['1s/ball'] = bowl_all['1s']/(bowl_all['balls_bowler']+0.000001)
bowl_all['2s/ball'] = bowl_all['2s']/(bowl_all['balls_bowler']+0.000001)
bowl_all['3s/ball'] = bowl_all['3s']/(bowl_all['balls_bowler']+0.000001)
bowl_all['4s/ball'] = bowl_all['4s']/(bowl_all['balls_bowler']+0.000001)
bowl_all['6s/ball'] = bowl_all['6s']/(bowl_all['balls_bowler']+0.000001)
bowl_all['extras/ball'] = bowl_all['extras']/(bowl_all['balls_bowler']+0.000001)
bowl_all['wickets/ball'] = bowl_all['outs_bowler']/(bowl_all['balls_bowler']+0.000001)
bowl_all.loc[bowl_all['wickets/ball']>1,'wickets/ball']=1
bowl_all['PP usage'] = bowl_all['powerplay']/(bowl_all['balls_bowler']+0.000001)
bowl_all['mid usage'] = bowl_all['middle']/(bowl_all['balls_bowler']+0.000001)
bowl_all['setup usage'] = bowl_all['setup']/(bowl_all['balls_bowler']+0.000001)
bowl_all['death usage'] = bowl_all['death']/(bowl_all['balls_bowler']+0.000001)
bowl_all['PP usage'] = bowl_all['PP usage']/(bowl_all['PP usage']+bowl_all['mid usage']+bowl_all['setup usage']+bowl_all['death usage'])
bowl_all['mid usage'] = bowl_all['mid usage']/(bowl_all['PP usage']+bowl_all['mid usage']+bowl_all['setup usage']+bowl_all['death usage'])
bowl_all['setup usage'] = bowl_all['setup usage']/(bowl_all['PP usage']+bowl_all['mid usage']+bowl_all['setup usage']+bowl_all['death usage'])
bowl_all['death usage'] = bowl_all['death usage']/(bowl_all['PP usage']+bowl_all['mid usage']+bowl_all['setup usage']+bowl_all['death usage'])
bowl_all['bb_GP'] = bowl_all['balls_bowler']/(bowl_all['bb_GP']+0.00000001)
bowl_all['ECON'] = 6*bowl_all['runs/ball']
bowl_all['SR'] = bowl_all['balls_bowler']/bowl_all['outs_bowler']
bowl_all['xECON'] = 6*bowl_all['xruns']/bowl_all['balls_bowler']
bowl_all['xSR'] = bowl_all['balls_bowler']/bowl_all['xwickets']
bowl_all.loc[bowl_all['SR']>600,'SR']=600
bowl_all['usage'] =bowl_all['bb_GP']/(120*factor)
bowl_all['RCAA'] = 20*(bowl_all['ECON']-bowl_all['xECON'])*bowl_all['usage']*factor
bowl_all = bowl_all[bowl_all.balls_bowler != 0]

def dumps():
    lol = pd.read_excel(input_file,'bowling year')
    lol2 = pd.read_excel(input_file,'batting year')
    lol3 = pd.read_excel(input_file,'bowling phases')
    lol4 = pd.read_excel(input_file,'batting phases')
    lol5 = bowl_all
    lol6 = bat_all
    lol7 = pd.read_excel(input_file,'venue bowling')
    lol8 = pd.read_excel(input_file,'venue batting')
    with pd.ExcelWriter(output_file) as writer:
        lol8.to_excel(writer, sheet_name="venue batting", index=False)
        lol7.to_excel(writer, sheet_name="venue bowling", index=False)
        lol6.to_excel(writer, sheet_name="batting seasons", index=False)
        lol5.to_excel(writer, sheet_name="bowling seasons", index=False)
        lol4.to_excel(writer, sheet_name="batting phases", index=False)
        lol3.to_excel(writer, sheet_name="bowling phases", index=False)
        lol2.to_excel(writer, sheet_name="batting year", index=False)
        lol.to_excel(writer, sheet_name="bowling year", index=False)
    print()
    print("aggregate summary dumped, run projections")
        
dumps()