# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:46:51 2023
Generating fantasy xPts for dream 11 based on projections
@author: Subramanya.Ganti
"""
#%% choose the teams which are playing
import pandas as pd
import numpy as np
from scipy.stats import poisson,gmean
import datetime as dt
pd.options.mode.chained_assignment = None  # default='warn'

comp = 'lpl'; year = '23'; unique_combos = 11
#if another league data is used as a proxy then set 1
custom=0; home=[]; opps=[]; proxy = 0
#date based game selection if 0, else specific gameweek or entire season
gw = 0
#select teams manually
home = ["B-Love Kandy"]; opps = ["Jaffna Kings"]
#select custom date
#custom = dt.datetime(2023,8,3) #year,month,date

#%% find projections for the games in question
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'
if(proxy == 1): input_file = f"{path}/{comp}_proxy_projections.xlsx"
else: input_file = f"{path}/{comp}_projections.xlsx"
input_file1 = f"{path}/{comp}_summary.xlsx"
output_dump = f"{path}/game.xlsx"

def fixtures_file(now,comp,gw):
    fixtures = f"{path}/schedule.xlsx"
    if(comp == 'hundredw'): fixtures = pd.read_excel(fixtures,f'hundred {year}')
    else: fixtures = pd.read_excel(fixtures,f'{comp} {year}')
    temp = dt.datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
    delta = now - temp
    now = float(delta.days)
    home = []; opps = []

    for x in fixtures.values:
        if(gw == 0 and x[1] == now):
            home.append(x[3])
            opps.append(x[4])
        elif(gw == x[2]):
            home.append(x[3])
            opps.append(x[4])
            
    return (home,opps)

if(home==[] and opps==[]):
    if(custom !=0): now = custom
    else: now = dt.datetime.now()
    (home,opps) = fixtures_file(now,comp,gw)

if(comp=='hundred' or comp=='hundredw'):
    f = (5/6); #hundred
elif(comp=='odi' or comp=='odiw' or comp=='odiq' or comp=='rlc'):
    f = 2.5;   #odi
elif(comp=='tests'):
    f = 11.25; #test
else:
    f = 1;     #assume its a t20 by default

from usage import *
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
    summary = summary.apply(pd.to_numeric, errors='ignore')
    league_avg = (summary.loc[(summary['Team']!="Free Agent"),'runs bat'].mean() + summary.loc[(summary['Team']!="Free Agent"),'runs bowl'].mean())/2
    
    #old logic for balls faced
    #ut1 = (bat.loc[bat['team']==t2,'usage'].sum())/(bowl.loc[bowl['team']==t1,'usage'].sum())
    #ut2 = (bat.loc[bat['team']==t1,'usage'].sum())/(bowl.loc[bowl['team']==t2,'usage'].sum())
    #bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1
    #bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2
    
    #new logic for balls faced
    ut3 = gmean([(bat.loc[bat['team']==t2,'usage'].sum()),(bowl.loc[bowl['team']==t1,'usage'].sum())])
    ut4 = gmean([(bat.loc[bat['team']==t1,'usage'].sum()),(bowl.loc[bowl['team']==t2,'usage'].sum())])
    ut1b = ut3 / (bowl.loc[bowl['team']==t1,'usage'].sum())
    ut2b = ut4 / (bowl.loc[bowl['team']==t2,'usage'].sum())
    ut1bat = ut4 / (bat.loc[bat['team']==t1,'usage'].sum())
    ut2bat = ut3 / (bat.loc[bat['team']==t2,'usage'].sum())
    bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1b
    bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2b
    bat.loc[bat['team']==t2,'usage'] = bat.loc[bat['team']==t2,'usage'] * ut2bat
    bat.loc[bat['team']==t1,'usage'] = bat.loc[bat['team']==t1,'usage'] * ut1bat
    #print(bowl.loc[bowl['team']==t1,'usage'].sum(),bowl.loc[bowl['team']==t2,'usage'].sum(),ut3,ut4)
    
    s1 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'runs/ball']*factor*120).sum()/(league_avg*bowl.loc[bowl['team']==t2,'usage'].sum())
    c1 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'runs/ball']*factor*120).sum()/(league_avg*bat.loc[bat['team']==t2,'usage'].sum())
    s2 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'runs/ball']*factor*120).sum()/(league_avg*bowl.loc[bowl['team']==t1,'usage'].sum())
    c2 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'runs/ball']*factor*120).sum()/(league_avg*bat.loc[bat['team']==t1,'usage'].sum())
    
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
    w_avg_bat = w_avg_bat.sum()*120*factor/(summary.shape[0]-1)
    w_avg_bowl = w_avg_bowl.sum()*120*factor/(summary.shape[0]-1)
    w_avg = (w_avg_bat + w_avg_bowl)/2

    for x in bat.values:
        if(x[2] == t1):
            x = adj(x,s1,1)
            bat_game.append(x.tolist())
            w1 = w1 + x[3]*x[7]*120*factor
        if(x[2] == t2):
            x = adj(x,s2,1)
            bat_game.append(x.tolist())
            w2 = w2 + x[3]*x[7]*120*factor

    for x in bowl.values:
        if(x[2] == t1):
            x = adj(x,c1,0)
            bowl_game.append(x.tolist())
            w1_bowl = w1_bowl + x[3]*x[6]*120*factor
        if(x[2] == t2):
            x = adj(x,c2,0)
            bowl_game.append(x.tolist())
            w2_bowl = w2_bowl + x[3]*x[6]*120*factor

    bat_game = pd.DataFrame(bat_game)
    bat_game.columns = bat_game.iloc[0];bat_game = bat_game.drop(0)
    bowl_game = pd.DataFrame(bowl_game)
    bowl_game.columns = bowl_game.iloc[0];bowl_game = bowl_game.drop(0)
    bat_game = bat_game.apply(pd.to_numeric, errors='ignore')
    bowl_game = bowl_game.apply(pd.to_numeric, errors='ignore')
    
    if(factor == 11.25):
        w_avg = w_avg * (bat_game['usage'].sum()/2)
        bat_game.loc[bat_game['team'] == t1, 'wickets/ball'] = bat_game.loc[bat_game['team'] == t1, 'wickets/ball']*(w2_bowl+0.7)/w_avg
        bat_game.loc[bat_game['team'] == t2, 'wickets/ball'] = bat_game.loc[bat_game['team'] == t2, 'wickets/ball']*(w1_bowl+0.7)/w_avg
        bat_game['balls/wkt'] = 1/bat_game['wickets/ball']
        bowl_game.loc[bowl_game['team'] == t1, 'wickets/ball'] = bowl_game.loc[bowl_game['team'] == t1, 'wickets/ball']*(w2-0.7)/w_avg
        bowl_game.loc[bowl_game['team'] == t2, 'wickets/ball'] = bowl_game.loc[bowl_game['team'] == t2, 'wickets/ball']*(w1-0.7)/w_avg
    else:
        bat_game.loc[bat_game['team'] == t1, 'wickets/ball'] = bat_game.loc[bat_game['team'] == t1, 'wickets/ball']*(w2_bowl+0.35)/w_avg
        bat_game.loc[bat_game['team'] == t2, 'wickets/ball'] = bat_game.loc[bat_game['team'] == t2, 'wickets/ball']*(w1_bowl+0.35)/w_avg
        bat_game['balls/wkt'] = 1/bat_game['wickets/ball']
        bowl_game.loc[bowl_game['team'] == t1, 'wickets/ball'] = bowl_game.loc[bowl_game['team'] == t1, 'wickets/ball']*(w2-0.35)/w_avg
        bowl_game.loc[bowl_game['team'] == t2, 'wickets/ball'] = bowl_game.loc[bowl_game['team'] == t2, 'wickets/ball']*(w1-0.35)/w_avg

    bat_game['xPts'] = 120*factor*bat_game['usage']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])
    bat_game['full xPts'] = bat_game['balls/wkt']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])
    bat_game['xPts'] = bat_game['xPts'] - 2*bat_game['wickets/ball']
    bat_game['full xPts'] = bat_game['full xPts'] - 2*bat_game['wickets/ball']

    bat_game = bat_game.drop(['pp usage'],axis=1)
    bat_game = bat_game.drop(['mid usage'],axis=1)
    bat_game = bat_game.drop(['setup usage'],axis=1)
    bat_game = bat_game.drop(['death usage'],axis=1)
    bowl_game = bowl_game.drop(['pp usage'],axis=1)
    bowl_game = bowl_game.drop(['mid usage'],axis=1)
    bowl_game = bowl_game.drop(['setup usage'],axis=1)
    bowl_game = bowl_game.drop(['death usage'],axis=1)    
    
    if(factor != 11.25):
        bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        #bowl_game['usage'] = bowl_game['usage']+(2-bowl_game['usage'].sum())/bowl_game['usage'].shape[0]        
        #sum_usage_t1 = bowl_game.loc[bowl_game['team']==t1,'usage'].sum()
        #sum_usage_t2 = bowl_game.loc[bowl_game['team']==t2,'usage'].sum()
        #bowl_game.loc[bowl_game['team']==t1,'usage'] = bowl_game.loc[bowl_game['team']==t1,'usage']/sum_usage_t1
        #bowl_game.loc[bowl_game['team']==t2,'usage'] = bowl_game.loc[bowl_game['team']==t2,'usage']/sum_usage_t2
        #bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*28
        
        if(factor == 1):
            bat_game['xPts'] = bat_game['xPts'] + 6*(1-poisson.cdf(k=170,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=170,mu=bat_game['SR'])-poisson.cdf(k=150,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] + 2*(poisson.cdf(k=150,mu=bat_game['SR'])-poisson.cdf(k=130,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] - 2*(poisson.cdf(k=70,mu=bat_game['SR'])-poisson.cdf(k=60,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] - 4*(poisson.cdf(k=60,mu=bat_game['SR'])-poisson.cdf(k=50,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] - 6*poisson.cdf(k=50,mu=bat_game['SR'])*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))         
            bowl_game['xPts'] = bowl_game['xPts'] + 12*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] - 6*(1-poisson.cdf(k=12,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] - 4*(poisson.cdf(k=12,mu=bowl_game['ECON'])-poisson.cdf(k=11.,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] - 2*(poisson.cdf(k=11,mu=bowl_game['ECON'])-poisson.cdf(k=10,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] + 2*(poisson.cdf(k=7,mu=bowl_game['ECON'])-poisson.cdf(k=6,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*(poisson.cdf(k=6,mu=bowl_game['ECON'])-poisson.cdf(k=5,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] + 6*poisson.cdf(k=5,mu=bowl_game['ECON'])
            
            bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=30,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bat_game['xPts'] = bat_game['xPts'] + 8*(poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bat_game['xPts'] = bat_game['xPts'] + 16*(1-poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*poisson.pmf(k=3,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            bowl_game['xPts'] = bowl_game['xPts'] + 8*poisson.pmf(k=4,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            bowl_game['xPts'] = bowl_game['xPts'] + 16*poisson.pmf(k=5,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            
        elif(factor == 2.5):
            bat_game['xPts'] = bat_game['xPts'] + 6*(1-poisson.cdf(k=140,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=140,mu=bat_game['SR'])-poisson.cdf(k=120,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] + 2*(poisson.cdf(k=120,mu=bat_game['SR'])-poisson.cdf(k=100,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] - 2*(poisson.cdf(k=50,mu=bat_game['SR'])-poisson.cdf(k=40,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] - 4*(poisson.cdf(k=30,mu=bat_game['SR'])-poisson.cdf(k=40,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            bat_game['xPts'] = bat_game['xPts'] - 6*poisson.cdf(k=30,mu=bat_game['SR'])*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))         
            bowl_game['xPts'] = bowl_game['xPts'] + 4*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] - 6*(1-poisson.cdf(k=9,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] - 4*(poisson.cdf(k=9,mu=bowl_game['ECON'])-poisson.cdf(k=8,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] - 2*(poisson.cdf(k=8,mu=bowl_game['ECON'])-poisson.cdf(k=7,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] + 2*(poisson.cdf(k=4.5,mu=bowl_game['ECON'])-poisson.cdf(k=3.5,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*(poisson.cdf(k=3.5,mu=bowl_game['ECON'])-poisson.cdf(k=2.5,mu=bowl_game['ECON']))
            bowl_game['xPts'] = bowl_game['xPts'] + 6*poisson.cdf(k=2.5,mu=bowl_game['ECON'])
            
            bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bat_game['xPts'] = bat_game['xPts'] + 8*(poisson.cdf(k=200,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bat_game['xPts'] = bat_game['xPts'] + 16*(1-poisson.cdf(k=200,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*poisson.pmf(k=4,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            bowl_game['xPts'] = bowl_game['xPts'] + 8*poisson.pmf(k=5,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            
        elif(factor == 5/6):         
            bowl_game['xPts'] = bowl_game['xPts'] + 16*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor            
            bat_game['xPts'] = bat_game['xPts'] + 5*(poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=30,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bat_game['xPts'] = bat_game['xPts'] + 10*(poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bat_game['xPts'] = bat_game['xPts'] + 20*(1-poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            bowl_game['xPts'] = bowl_game['xPts'] + 5*poisson.pmf(k=3,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            bowl_game['xPts'] = bowl_game['xPts'] + 10*poisson.pmf(k=4,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            bowl_game['xPts'] = bowl_game['xPts'] + 20*poisson.pmf(k=5,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            
    else:
        bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*19
        bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
        bat_game['xPts'] = bat_game['xPts'] + 8*(poisson.cdf(k=200,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
        bat_game['xPts'] = bat_game['xPts'] + 16*(poisson.cdf(k=300,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=200,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
        bat_game['xPts'] = bat_game['xPts'] + 24*(1-poisson.cdf(k=300,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
        bowl_game['xPts'] = bowl_game['xPts'] + 4*poisson.pmf(k=4,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
        bowl_game['xPts'] = bowl_game['xPts'] + 8*poisson.pmf(k=5,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
     
    if(factor == 5/6): factor = 1 
    #print()
    #print(t1,"overs batted",20*factor*bat_game.loc[bat_game['team']==t1,'usage'].sum())
    #print(t2,"overs batted",20*factor*bat_game.loc[bat_game['team']==t2,'usage'].sum())
    #print(t1,"overs bowled",20*factor*bowl_game.loc[bowl_game['team']==t1,'usage'].sum())
    #print(t2,"overs bowled",20*factor*bowl_game.loc[bowl_game['team']==t2,'usage'].sum())
    print(t1,"runs",s1*c2*league_avg*(bat_game.loc[bat_game['team']==t1,'usage'].sum()))
    print("overs batted",20*factor*bat_game.loc[bat_game['team']==t1,'usage'].sum())
    print(t2,"runs",s2*c1*league_avg*(bat_game.loc[bat_game['team']==t2,'usage'].sum()))
    print("overs batted",20*factor*bat_game.loc[bat_game['team']==t2,'usage'].sum())
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

def final_projections(bat_game,bowl_game):
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
    final['total'] = final['bat'] + final['bowl'] + 4
    #final['max'] = final['bat max'] + final['bowl max'] + 4
    final = final.sort_values(['total'], ascending=[False])
    return final

a_final = final_projections(bat_game,bowl_game)

# %% generate 11 unique combos
def randomizer(a_projection,home,opps,unique_teams):
    team = [["1","2","3","4","5","6","7","8","9","10","11","C","VC","xPts"]]; i=0; j=0;
    players = a_projection.loc[(a_projection['team'] == home) | (a_projection['team'] == opps)]
    p = pow(players['total'],2).tolist()
    players = players['player'].tolist()
    sum_p = sum(p)
    p = [x/sum_p for x in p]
    
    while i<unique_teams:
        h=0; o=0;
        combo = np.random.choice(players, 11, p=p, replace=False)
        combo = combo.tolist()
        combo = sorted(combo)
        while j<11:
            t = a_projection.loc[a_projection['player'] == combo[j], 'team'].values[0]
            if(t==home): h+=1
            if(t==opps): o+=1
            j+=1
        if(h>10 or o>10): i=i-1
        else:
            cap = a_projection[a_projection.player.isin(combo)]
            pts = sum(cap['total'])
            p2 = pow(cap['total'],3).tolist()
            cap = cap['player'].tolist()
            sum_p2 = sum(p2)
            p2 = [x/sum_p2 for x in p2]
            y = np.random.choice(cap, 2, p=p2, replace=False)
            y = y.tolist()        
            pts += a_projection.loc[(a_projection['player']==y[0]),'total'].sum() + (a_projection.loc[(a_projection['player']==y[1]),'total'].sum()/2)
            combo += y + [pts]
            
            team.append(combo)
        i +=1; j=0
        
    team = pd.DataFrame(team)
    team.columns = team.iloc[0];team = team.drop(0)
    team = team.T
    return team


c=0;a_combinations=[];
while c<len(home):
    co = randomizer(a_final,home[c],opps[c],unique_combos)
    a_combinations.append(co)
    #a_diffs.append(dif)
    c+=1
    
#%% dump projections to the desired file
def dump_excel(output_dump,a_final,a_combinations):
    c=0
    with pd.ExcelWriter(output_dump) as writer:        
        a_final.to_excel(writer, sheet_name="Points", index=False)
        while(c<len(a_combinations)):
            #a_combinations[c].to_excel(writer, sheet_name=f"{home[c]}_{opps[c]}", index=False)
            c+=1
#dump_excel(output_dump,a_final,a_combinations)
