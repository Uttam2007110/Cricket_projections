# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:46:51 2023
Generating fantasy xPts for dream 11 based on projections
@author: Subramanya.Ganti
"""

import pandas as pd
import numpy as np
from scipy.stats import poisson
from usage import *
import datetime as dt

input_file = "C:/Users/Subramanya.Ganti/Downloads/cricket/blast_projections.xlsx"
input_file1 = "C:/Users/Subramanya.Ganti/Downloads/cricket/blast_summary.xlsx"
output_dump = "C:/Users/Subramanya.Ganti/Downloads/game.xlsx"

def fixtures_file(now):    
    fixtures = "C:/Users/Subramanya.Ganti/Downloads/cricket/blast_schedule.xlsx"
    fixtures = pd.read_excel(fixtures,'schedule')
    temp = dt.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = now - temp
    now = float(delta.days)
    
    home = []
    opps = []

    for x in fixtures.values:
        if(x[1] == now):
            home.append(x[3])
            opps.append(x[4])
            
    return (home,opps)

now = dt.datetime.now()
#now = dt.datetime(2023,6,18)
(home,opps) = fixtures_file(now)

#home = ["Essex"]
#opps = ["Glamorgan"]
f = 1

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
    bowl_game.loc[bowl_game['team'] == t1, 'wickets/ball'] = bowl_game['wickets/ball']*(w2-0.35)/w_avg
    bowl_game.loc[bowl_game['team'] == t2, 'wickets/ball'] = bowl_game['wickets/ball']*(w1-0.35)/w_avg

    #bat_game['usage'] = np.minimum(bat_game['usage'],(1.65*np.exp(-1.0*np.minimum(bat_game['death usage'],0.7))-0.45)*bat_game['balls/wkt']/120)
    bat_game['xPts'] = 120*bat_game['usage']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])
    #bat_game['full xPts'] = (1.65*np.exp(-1.0*np.minimum(bat_game['death usage'],0.8))-0.45)*bat_game['balls/wkt']*bat_game['xPts']/(120*bat_game['usage'])
    bat_game['full xPts'] = bat_game['balls/wkt']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])
    bat_game['xPts'] = bat_game['xPts'] - 2*bat_game['wickets/ball']
    bat_game['full xPts'] = bat_game['full xPts'] - 2*bat_game['wickets/ball']

    bat_game = bat_game.drop(['pp usage'],axis=1)
    bat_game = bat_game.drop(['mid usage'],axis=1)
    bat_game = bat_game.drop(['setup usage'],axis=1)
    bat_game = bat_game.drop(['death usage'],axis=1)

    for x in bat_game.values:
        lol = x[6]*x[3]*120; lol2 = x[6]*x[4]
        
        x[14] = x[14] + 4*(poisson.cdf(k=50,mu=lol)-poisson.cdf(k=30,mu=lol))
        x[14] = x[14] + 8*(poisson.cdf(k=100,mu=lol)-poisson.cdf(k=50,mu=lol))
        x[14] = x[14] + 16*(1-poisson.cdf(k=100,mu=lol))
        x[14] = x[14] + 6*(1-poisson.cdf(k=170,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[14] = x[14] + 4*(poisson.cdf(k=170,mu=x[5])-poisson.cdf(k=150,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[14] = x[14] + 2*(poisson.cdf(k=150,mu=x[5])-poisson.cdf(k=130,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[14] = x[14] - 2*(poisson.cdf(k=70,mu=x[5])-poisson.cdf(k=60,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[14] = x[14] - 4*(poisson.cdf(k=60,mu=x[5])-poisson.cdf(k=50,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[14] = x[14] - 6*poisson.cdf(k=50,mu=x[5])*(1-poisson.cdf(k=10,mu=120*x[3]))
        
        x[15] = x[15] + 4*(poisson.cdf(k=50,mu=lol2)-poisson.cdf(k=30,mu=lol2))
        x[15] = x[15] + 8*(poisson.cdf(k=100,mu=lol2)-poisson.cdf(k=50,mu=lol2))
        x[15] = x[15] + 16*(1-poisson.cdf(k=100,mu=lol2))
        x[15] = x[15] + 6*(1-poisson.cdf(k=170,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[15] = x[15] + 4*(poisson.cdf(k=170,mu=x[5])-poisson.cdf(k=150,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[15] = x[15] + 2*(poisson.cdf(k=150,mu=x[5])-poisson.cdf(k=130,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[15] = x[15] - 2*(poisson.cdf(k=70,mu=x[5])-poisson.cdf(k=60,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[15] = x[15] - 4*(poisson.cdf(k=60,mu=x[5])-poisson.cdf(k=50,mu=x[5]))*(1-poisson.cdf(k=10,mu=120*x[3]))
        x[15] = x[15] - 6*poisson.cdf(k=50,mu=x[5])*(1-poisson.cdf(k=10,mu=120*x[3]))

    bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
    bowl_game['usage'] = bowl_game['usage']+(2-bowl_game['usage'].sum())/bowl_game['usage'].shape[0]
    bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
    bowl_game['xPts'] = 120*bowl_game['usage']*bowl_game['wickets/ball']*28
    bowl_game['full xPts'] = 0.2*bowl_game['xPts']/bowl_game['usage']

    bowl_game = bowl_game.drop(['pp usage'],axis=1)
    bowl_game = bowl_game.drop(['mid usage'],axis=1)
    bowl_game = bowl_game.drop(['setup usage'],axis=1)
    bowl_game = bowl_game.drop(['death usage'],axis=1)

    for x in bowl_game.values:
        #pmf equal to a value, cdf less than a value
        x[15] = x[15] + 4*poisson.pmf(k=3,mu=x[6]*x[3]*120)
        x[15] = x[15] + 8*poisson.pmf(k=4,mu=x[6]*x[3]*120)
        x[15] = x[15] + 16*poisson.pmf(k=5,mu=x[6]*x[3]*120)
        x[15] = x[15] + 12*np.power(x[8],6)*20*x[3]
        x[15] = x[15] - 6*(1-poisson.cdf(k=12,mu=x[4]))
        x[15] = x[15] - 4*(poisson.cdf(k=12,mu=x[4])-poisson.cdf(k=11,mu=x[4]))
        x[15] = x[15] - 2*(poisson.cdf(k=11,mu=x[4])-poisson.cdf(k=10,mu=x[4]))
        x[15] = x[15] + 2*(poisson.cdf(k=7,mu=x[4])-poisson.cdf(k=6,mu=x[4]))
        x[15] = x[15] + 4*(poisson.cdf(k=6,mu=x[4])-poisson.cdf(k=5,mu=x[4]))
        x[15] = x[15] + 6*poisson.cdf(k=5,mu=x[4])
        #print(x[0],np.power(x[8],6)*6*x[3])
        x[16] = x[16] + 4*poisson.pmf(k=3,mu=x[6]*0.2*120)
        x[16] = x[16] + 8*poisson.pmf(k=4,mu=x[6]*0.2*120)
        x[16] = x[16] + 16*poisson.pmf(k=5,mu=x[6]*0.2*120)
        x[16] = x[16] + 12*np.power(x[8],6)*20*0.2
        x[16] = x[16] - 6*(1-poisson.cdf(k=12,mu=x[4]))
        x[16] = x[16] - 4*(poisson.cdf(k=12,mu=x[4])-poisson.cdf(k=11,mu=x[4]))
        x[16] = x[16] - 2*(poisson.cdf(k=11,mu=x[4])-poisson.cdf(k=10,mu=x[4]))
        x[16] = x[16] + 2*(poisson.cdf(k=7,mu=x[4])-poisson.cdf(k=6,mu=x[4]))
        x[16] = x[16] + 4*(poisson.cdf(k=6,mu=x[4])-poisson.cdf(k=5,mu=x[4]))
        x[16] = x[16] + 6*poisson.cdf(k=5,mu=x[4])

    print("bowling usage",bowl_game['usage'].sum())
    print("batting usage",bat_game['usage'].sum())
    print(t1,s1*c2*league_avg)
    print(t2,s2*c1*league_avg)
    print(" ")
    return (bat_game,bowl_game,summary)

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

names = np.unique(np.concatenate([bat_game['batsman'].values,bowl_game['bowler'].values]))
final = [["player","team","bat","bowl","total","bat usage","bowl usage"]]

for x in names:
    try : p_bat = bat_game.loc[(bat_game['batsman']==x),'team'].values[0]  
    except IndexError: p_bat = "Free Agent"
    try : p_bowl = bowl_game.loc[(bowl_game['bowler']==x),'team'].values[0]
    except IndexError: p_bowl = "Free Agent"
    if(p_bat == "Free Agent"): p_team = p_bowl
    else : p_team = p_bat
    
    bat_game = bat_game.groupby(['batsman','season','team'], as_index=False).sum()
    bowl_game = bowl_game.groupby(['bowler','season','team'], as_index=False).sum()
    
    final.append([x,p_team,bat_game.loc[(bat_game['batsman']==x),'xPts'].mean(),bowl_game.loc[(bowl_game['bowler']==x),'xPts'].mean(),0,bat_game.loc[(bat_game['batsman']==x),'usage'].mean(),bowl_game.loc[(bowl_game['bowler']==x),'usage'].mean()])
    
final = pd.DataFrame(final)
final.columns = final.iloc[0];final = final.drop(0)
final = final.fillna(0)
final['total'] = final['bat'] + final['bowl'] + 4
#final['max'] = final['bat max'] + final['bowl max'] + 4

with pd.ExcelWriter(output_dump) as writer:        
    final.to_excel(writer, sheet_name="Points", index=False)   