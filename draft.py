# -*- coding: utf-8 -*-
"""
Created on Tue May 16 01:54:48 2023
Generating fantasy xPts for the cricket draft based on projections
@author: Subramanya.Ganti
"""

import pandas as pd
import numpy as np
from scipy.stats import poisson
from usage import *
pd.options.mode.chained_assignment = None  # default='warn'

comp = 'blast'
year = '23'
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'
gw = 8

input_file = f"{path}/{comp}_projections.xlsx"
input_file1 = f"{path}/{comp}_summary.xlsx"
output_dump = f'{path}/{comp}_gw{gw}.xlsx'
fixtures = f"{path}/schedule.xlsx"
fixtures = pd.read_excel(fixtures,f'{comp} {year}')

home = []
opps = []
f = 1

for x in fixtures.values:
    if(x[2] == gw):
        home.append(x[3])
        opps.append(x[4])

   
def adj(x,f,bat):
    if(bat == 1):
        #print(x)
        x[6] = x[6]*f
        x[5] = x[5]*f
    else:
        x[4] = x[4]*f
        x[11] = x[11]*f
        
    x[14] = x[14]*f
    x[15] = x[15]*f
    x[16] = x[16]*f
    x[17] = x[17]*f
    x[13] = x[13]*f
    x[12] = 1 - (x[14]+x[15]+x[16]+x[17]+x[13])
    return x

print("")
def gw_projection(a,b,input_file1,input_file,factor):
    t1 = a
    t2 = b
    print(t1,"vs",t2)
    (summary,bat,bowl) = h2h_alt(input_file1,input_file,1,factor)
    #summary = pd.read_excel(input_file,'MDist Table')
    summary = summary.apply(pd.to_numeric, errors='ignore')
    league_avg = (summary.loc[(summary['Team']!="Free Agent"),'runs bat'].mean() + summary.loc[(summary['Team']!="Free Agent"),'runs bowl'].mean())/2

    s1 = summary.loc[(summary['Team']==t2),'runs bowl'].mean()/league_avg
    c1 = summary.loc[(summary['Team']==t2),'runs bat'].mean()/league_avg
    s2 = summary.loc[(summary['Team']==t1),'runs bowl'].mean()/league_avg
    c2 = summary.loc[(summary['Team']==t1),'runs bat'].mean()/league_avg
    w1 = 0; w2 = 0;
    w1_bowl = 0; w2_bowl = 0;

    #bat = pd.read_excel(input_file,'MDist bat')
    bat = bat.drop(['RSAA'],axis=1)
    bat = bat.drop(['OAA'],axis=1)
    bat = bat.drop(['xballs/wkt'],axis=1)
    bat = bat.drop(['xSR'],axis=1)
    #bowl = pd.read_excel(input_file,'MDist bowl')
    bowl = bowl.drop(['RCAA'],axis=1)
    bowl = bowl.drop(['WTAA'],axis=1)
    bowl = bowl.drop(['xECON'],axis=1)
    bowl = bowl.drop(['xSR'],axis=1)
    bat_game = [["batsman","season","team","usage","balls/wkt","SR","runs/ball","wickets/ball","pp usage","mid usage","setup usage","death usage","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","xPts","full xPts"]]
    bowl_game = [["bowler","season","team","usage","ECON","SR","wickets/ball","pp usage","mid usage","setup usage","death usage","runs/ball","dots/ball","1s/ball","2s/ball","3s/ball","4s/ball","6s/ball","extras/ball","xPts","full xPts"]]

    w_avg_bat = bat.loc[(bat['team']!="Free Agent"),'usage']*bat.loc[(bat['team']!="Free Agent"),'wickets/ball']
    w_avg_bowl = bowl.loc[(bowl['team']!="Free Agent"),'usage']*bowl.loc[(bowl['team']!="Free Agent"),'wickets/ball']
    w_avg_bat = w_avg_bat.sum()*120/(summary.shape[0]-1)
    w_avg_bowl = w_avg_bowl.sum()*120/(summary.shape[0]-1)
    w_avg = (w_avg_bat + w_avg_bowl)/2

    for x in bat.values:
        if(x[2] == t1):
            x = adj(x,s1,1)
            bat_game.append(x.tolist())
            w1 = w1 + x[3]*x[7]*120
        if(x[2] == t2):
            x = adj(x,s2,1)
            bat_game.append(x.tolist())
            w2 = w2 + x[3]*x[7]*120

    for x in bowl.values:
        if(x[2] == t1):
            x = adj(x,c1,0)
            bowl_game.append(x.tolist())
            w1_bowl = w1_bowl + x[3]*x[6]*120
        if(x[2] == t2):
            x = adj(x,c2,0)
            bowl_game.append(x.tolist())
            w2_bowl = w2_bowl + x[3]*x[6]*120

    bat_game = pd.DataFrame(bat_game)
    bat_game.columns = bat_game.iloc[0];bat_game = bat_game.drop(0)
    bowl_game = pd.DataFrame(bowl_game)
    bowl_game.columns = bowl_game.iloc[0];bowl_game = bowl_game.drop(0)
    bat_game = bat_game.apply(pd.to_numeric, errors='ignore')
    bowl_game = bowl_game.apply(pd.to_numeric, errors='ignore')

    bat_game.loc[bat_game['team'] == t1, 'wickets/ball'] = bat_game['wickets/ball']*(w2_bowl+0.35)/w_avg
    bat_game.loc[bat_game['team'] == t2, 'wickets/ball'] = bat_game['wickets/ball']*(w1_bowl+0.35)/w_avg
    bat_game['balls/wkt'] = 1/bat_game['wickets/ball']
    bowl_game.loc[bowl_game['team'] == t1, 'wickets/ball'] = bowl_game['wickets/ball']*(w2-0.35)/(w_avg-0.35)
    bowl_game.loc[bowl_game['team'] == t2, 'wickets/ball'] = bowl_game['wickets/ball']*(w1-0.35)/(w_avg-0.35)
    
    bat_game['xPts'] = 120*bat_game['usage']*(bat_game['runs/ball']+3*bat_game['6s/ball'])
    bat_game['full xPts'] = bat_game['balls/wkt']*(bat_game['runs/ball']+3*bat_game['6s/ball'])

    bat_game = bat_game.drop(['pp usage'],axis=1)
    bat_game = bat_game.drop(['mid usage'],axis=1)
    bat_game = bat_game.drop(['setup usage'],axis=1)
    bat_game = bat_game.drop(['death usage'],axis=1)

    for x in bat_game.values:
        lol = x[6]*x[3]*120; lol2 = x[6]*x[4]
        x[14] = x[14] + 25*(poisson.cdf(k=100,mu=lol)-poisson.cdf(k=50,mu=lol))
        x[14] = x[14] + 50*(1-poisson.cdf(k=100,mu=lol))
        x[14] = x[14] + 2.5*120*x[3]*x[6]*(1-poisson.cdf(k=230,mu=x[5]))
        x[14] = x[14] + 2*120*x[3]*x[6]*(poisson.cdf(k=230,mu=x[5])-poisson.cdf(k=200,mu=x[5]))
        x[14] = x[14] + 1.5*120*x[3]*x[6]*(poisson.cdf(k=200,mu=x[5])-poisson.cdf(k=175,mu=x[5]))
        x[14] = x[14] + 120*x[3]*x[6]*(poisson.cdf(k=175,mu=x[5])-poisson.cdf(k=155,mu=x[5]))
        x[14] = x[14] + 0.5*120*x[3]*x[6]*(poisson.cdf(k=155,mu=x[5])-poisson.cdf(k=140,mu=x[5]))
        x[14] = x[14] - 5*(poisson.cdf(k=110,mu=x[5])-poisson.cdf(k=95,mu=x[5]))
        x[14] = x[14] - 10*(poisson.cdf(k=95,mu=x[5])-poisson.cdf(k=75,mu=x[5]))
        x[14] = x[14] - 15*(poisson.cdf(k=75,mu=x[5])-poisson.cdf(k=50,mu=x[5]))
        x[14] = x[14] - 20*poisson.cdf(k=50,mu=x[5])
        x[14] = x[14] - 25*poisson.pmf(k=0,mu=120*x[3]*x[6])
    
        x[15] = x[15] + 25*(poisson.cdf(k=100,mu=lol2)-poisson.cdf(k=50,mu=lol2))
        x[15] = x[15] + 50*(1-poisson.cdf(k=100,mu=lol2))
        x[15] = x[15] + 2.5*x[4]*(1-poisson.cdf(k=230,mu=x[5]))
        x[15] = x[15] + 2*x[4]*(poisson.cdf(k=230,mu=x[5])-poisson.cdf(k=200,mu=x[5]))
        x[15] = x[15] + 1.5*x[4]*(poisson.cdf(k=200,mu=x[5])-poisson.cdf(k=175,mu=x[5]))
        x[15] = x[15] + x[4]*(poisson.cdf(k=175,mu=x[5])-poisson.cdf(k=155,mu=x[5]))
        x[15] = x[15] + 0.5*x[4]*(poisson.cdf(k=155,mu=x[5])-poisson.cdf(k=140,mu=x[5]))
        x[15] = x[15] - 5*(poisson.cdf(k=110,mu=x[5])-poisson.cdf(k=95,mu=x[5]))
        x[15] = x[15] - 10*(poisson.cdf(k=95,mu=x[5])-poisson.cdf(k=75,mu=x[5]))
        x[15] = x[15] - 15*(poisson.cdf(k=75,mu=x[5])-poisson.cdf(k=50,mu=x[5]))
        x[15] = x[15] - 20*poisson.cdf(k=50,mu=x[5])
        x[15] = x[15] - 25*poisson.pmf(k=0,mu=120*x[3]*x[6])

    bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
    bowl_game['usage'] = bowl_game['usage']+(2-bowl_game['usage'].sum())/bowl_game['usage'].shape[0]
    bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
    bowl_game['xPts'] = 120*bowl_game['usage']*bowl_game['wickets/ball']*30
    bowl_game['full xPts'] = 0.2*bowl_game['xPts']/bowl_game['usage']

    bowl_game = bowl_game.drop(['pp usage'],axis=1)
    bowl_game = bowl_game.drop(['mid usage'],axis=1)
    bowl_game = bowl_game.drop(['setup usage'],axis=1)
    bowl_game = bowl_game.drop(['death usage'],axis=1)

    for x in bowl_game.values:
        #pmf equal to a value, cdf less than a value
        x[15] = x[15] + 25*poisson.pmf(k=3,mu=x[6]*x[3]*120)
        x[15] = x[15] + 35*poisson.pmf(k=4,mu=x[6]*x[3]*120)
        x[15] = x[15] + 50*poisson.pmf(k=5,mu=x[6]*x[3]*120)
        x[15] = x[15] + 15*np.power(x[8],6)*20*x[3]
        x[15] = x[15] - 20*(1-poisson.cdf(k=14,mu=x[4]))
        x[15] = x[15] - 15*(poisson.cdf(k=14,mu=x[4])-poisson.cdf(k=12,mu=x[4]))
        x[15] = x[15] - 10*(poisson.cdf(k=12,mu=x[4])-poisson.cdf(k=10.5,mu=x[4]))
        x[15] = x[15] - 5*(poisson.cdf(k=10.5,mu=x[4])-poisson.cdf(k=9.5,mu=x[4]))
        x[15] = x[15] + 10*(poisson.cdf(k=7.5,mu=x[4])-poisson.cdf(k=6.5,mu=x[4]))
        x[15] = x[15] + 25*(poisson.cdf(k=6.5,mu=x[4])-poisson.cdf(k=5.5,mu=x[4]))
        x[15] = x[15] + 45*(poisson.cdf(k=5.5,mu=x[4])-poisson.cdf(k=4.5,mu=x[4]))
        x[15] = x[15] + 70*(poisson.cdf(k=4.5,mu=x[4])-poisson.cdf(k=3.5,mu=x[4]))
        x[15] = x[15] + 100*poisson.cdf(k=3.5,mu=x[4])
        #print(x[0],np.power(x[8],6)*6*x[3])
        x[16] = x[16] + 25*poisson.pmf(k=3,mu=x[6]*0.2*120)
        x[16] = x[16] + 35*poisson.pmf(k=4,mu=x[6]*0.2*120)
        x[16] = x[16] + 50*poisson.pmf(k=5,mu=x[6]*0.2*120)
        x[16] = x[16] + 15*np.power(x[8],6)*20*0.2
        x[16] = x[16] - 20*(1-poisson.cdf(k=14,mu=x[4]))
        x[16] = x[16] - 15*(poisson.cdf(k=14,mu=x[4])-poisson.cdf(k=12,mu=x[4]))
        x[16] = x[16] - 10*(poisson.cdf(k=12,mu=x[4])-poisson.cdf(k=10.5,mu=x[4]))
        x[16] = x[16] - 5*(poisson.cdf(k=10.5,mu=x[4])-poisson.cdf(k=9.5,mu=x[4]))
        x[16] = x[16] + 10*(poisson.cdf(k=7.5,mu=x[4])-poisson.cdf(k=6.5,mu=x[4]))
        x[16] = x[16] + 25*(poisson.cdf(k=6.5,mu=x[4])-poisson.cdf(k=5.5,mu=x[4]))
        x[16] = x[16] + 45*(poisson.cdf(k=5.5,mu=x[4])-poisson.cdf(k=4.5,mu=x[4]))
        x[16] = x[16] + 70*(poisson.cdf(k=4.5,mu=x[4])-poisson.cdf(k=3.5,mu=x[4]))
        x[16] = x[16] + 100*poisson.cdf(k=3.5,mu=x[4])

    print("bowling usage",bowl_game['usage'].sum())
    print("batting usage",bat_game['usage'].sum())
    print(t1,s1*c2*league_avg)
    print(t2,s2*c1*league_avg)
    print(" ")
    return (bat_game,bowl_game,summary)

""""""""""""""""""""""""""""""""""""""""""""""""""""""
c = 0;
for x in home:
    a = home[c]
    b = opps[c]
    if (c==0): 
        (bat_game,bowl_game,table) = gw_projection(a,b,input_file1,input_file,f)
    else : 
        (bat,bowl,table) = gw_projection(a,b,input_file1,input_file,f)
        bat_game = pd.concat([bat_game,bat])
        bowl_game = pd.concat([bowl_game,bowl])
    c = c + 1

""""""""""""""""""""""""""""""""""""""""""""""""""""""

names = np.unique(np.concatenate([bat_game['batsman'].values,bowl_game['bowler'].values]))
final = [["player","team","total","bat","bowl","bat usage","bowl usage"]]

for x in names:
    try : p_bat = bat_game.loc[(bat_game['batsman']==x),'team'].values[0]  
    except IndexError: p_bat = "Free Agent"
    try : p_bowl = bowl_game.loc[(bowl_game['bowler']==x),'team'].values[0]
    except IndexError: p_bowl = "Free Agent"
    if(p_bat == "Free Agent"): p_team = p_bowl
    else : p_team = p_bat
    
    bat_game = bat_game.groupby(['batsman','season','team'], as_index=False).sum()
    bowl_game = bowl_game.groupby(['bowler','season','team'], as_index=False).sum()
    
    final.append([x,p_team,0,bat_game.loc[(bat_game['batsman']==x),'xPts'].mean(),bowl_game.loc[(bowl_game['bowler']==x),'xPts'].mean(),bat_game.loc[(bat_game['batsman']==x),'usage'].mean(),bowl_game.loc[(bowl_game['bowler']==x),'usage'].mean()])
    
final = pd.DataFrame(final)
final.columns = final.iloc[0];final = final.drop(0)
final = final.fillna(0)
final['total'] = final['bat'] + final['bowl']
#final['max'] = final['bat max'] + final['bowl max']
final = final.sort_values(['total'], ascending=[False])

with pd.ExcelWriter(output_dump) as writer:        
    final.to_excel(writer, sheet_name="Points", index=False)
