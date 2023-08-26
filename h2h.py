# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 16:46:51 2023
Generating fantasy xPts for dream 11 based on projections
@author: Subramanya.Ganti
"""
#%% choose the teams which are playing
import pandas as pd
import numpy as np
from scipy.stats import poisson,gmean,truncnorm
import datetime as dt
from openpyxl import load_workbook
pd.options.mode.chained_assignment = None  # default='warn'
np.seterr(all='ignore')

comp = 'tests'; year = '23'; unique_combos = 2
#if another league data is used as a proxy then set 1
home=[]; opps=[]; venue = []; proxy = 0; custom=0
#date based game selection if 0, else specific gameweek or entire season
gw = 0; writer = 0
#select teams manually
home = ["England"]; opps = ["Australia"]; venue = ["Lords"]
#select custom date
#custom = dt.datetime(2023,8,26) #year,month,date
#type of scoring system, default d11
coversoff = 0; ex22 = 0; cricdraft = 0

#%% find projections for the games in question
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'
if(proxy == 1): input_file = f"{path}/projections/{comp}_proxy_projections.xlsx"
else: input_file = f"{path}/projections/{comp}_projections.xlsx"
input_file1 = f"{path}/summary/{comp}_summary.xlsx"
output_dump = f"{path}/outputs/{comp}_{year}_game.xlsx"

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
            venue.append(x[5])
        elif(gw == x[2]):
            home.append(x[3])
            opps.append(x[4])
            venue.append(x[5])
            
    return (home,opps)

if(home==[] and opps==[]):
    if(custom !=0): now = custom
    else: now = dt.datetime.now()
    (home,opps) = fixtures_file(now,comp,gw)
else:
    now = dt.datetime.now()

if(comp=='hundred' or comp=='hundredw'):
    f = (5/6); #hundred
elif(comp=='odi' or comp=='odiw' or comp=='odiq' or comp=='rlc'):
    f = 2.5;   #odi
elif(comp=='tests' or comp == 'cc'):
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

def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

print("")
def gw_projection(a,b,input_file1,input_file,factor,v):
    t1 = a
    t2 = b
    print(t1,"vs",t2)
    print('Venue -',v)
    venues = pd.read_excel(input_file,'Venue factors')
    vrf = venues.loc[venues['Venue']==v,'runs'].sum()
    vwf = venues.loc[venues['Venue']==v,'wkts'].sum()
    if(vrf==0):vrf=1
    if(vwf==0):vwf=1
    (summary,bat,bowl) = h2h_alt(input_file1,input_file,1,factor)
    summary = summary.apply(pd.to_numeric, errors='ignore')
    league_avg = (summary.loc[(summary['Team']!="Free Agent"),'runs bat'].mean() + summary.loc[(summary['Team']!="Free Agent"),'runs bowl'].mean())/2
    bat['runs/ball'] = bat['runs/ball']*vrf
    bat['SR'] = bat['runs/ball']*100
    bowl['runs/ball'] = bowl['runs/ball']*vrf    
    
    if(factor<0.75):
        #old logic for balls faced
        ut1 = (bat.loc[bat['team']==t2,'usage'].sum())/(bowl.loc[bowl['team']==t1,'usage'].sum())
        ut2 = (bat.loc[bat['team']==t1,'usage'].sum())/(bowl.loc[bowl['team']==t2,'usage'].sum())
        bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1
        bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2
    else:
        #print(t1,"bowling",bowl.loc[bowl['team']==t1,'usage'].sum()*120*factor)
        #print(t2,"bowling",bowl.loc[bowl['team']==t2,'usage'].sum()*120*factor)
        #print(t1,"batting",bat.loc[bat['team']==t1,'usage'].sum()*120*factor)
        #print(t2,"batting",bat.loc[bat['team']==t2,'usage'].sum()*120*factor)
        #print(t1,"bowling wickets",(bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()*120*factor)
        #print(t2,"bowling wickets",(bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()*120*factor)
        #print(t1,"batting wickets",(bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()*120*factor)
        #print(t2,"batting wickets",(bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()*120*factor)
        
        #new logic for balls faced
        bb_t1 = bowl.loc[bowl['team']==t1,'usage'].sum()
        bb_t2 = bowl.loc[bowl['team']==t2,'usage'].sum()
        bf_t1 = bat.loc[bat['team']==t1,'usage'].sum()
        bf_t2 = bat.loc[bat['team']==t2,'usage'].sum()
        wbo_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()
        wbo_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()
        wba_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()
        wba_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()
        
        ut3 = min(pow(bb_t1*bf_t2*wba_t2/wbo_t1,0.5),1)
        ut4 = min(pow(bb_t2*bf_t1*wba_t1/wbo_t2,0.5),1)
        ut1b = ut3 / (bowl.loc[bowl['team']==t1,'usage'].sum())
        ut2b = ut4 / (bowl.loc[bowl['team']==t2,'usage'].sum())
        ut1bat = ut4 / (bat.loc[bat['team']==t1,'usage'].sum())
        ut2bat = ut3 / (bat.loc[bat['team']==t2,'usage'].sum())
        bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1b
        bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2b
        bat.loc[bat['team']==t2,'usage'] = bat.loc[bat['team']==t2,'usage'] * ut2bat
        bat.loc[bat['team']==t1,'usage'] = bat.loc[bat['team']==t1,'usage'] * ut1bat
        #print(bowl.loc[bowl['team']==t1,'usage'].sum(),bowl.loc[bowl['team']==t2,'usage'].sum(),ut3,ut4)
    
    bowl_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'runs/ball']*factor*120).sum()
    bowl_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'runs/ball']*factor*120).sum()
    bat_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'extras/ball']*factor*120).sum()
    bat_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'extras/ball']*factor*120).sum()
    #print("bowl t2",bowl_t2);
    #print("bowl t1",bowl_t1)
    #print("bat t2",bat_t2)
    #print("bat t1",bat_t1)
    #print(league_avg)
    s1 = bowl_t2/(league_avg*bowl.loc[bowl['team']==t2,'usage'].sum())
    c1 = bat_t2/(league_avg*bat.loc[bat['team']==t2,'usage'].sum())
    s2 = bowl_t1/(league_avg*bowl.loc[bowl['team']==t1,'usage'].sum())
    c2 = bat_t1/(league_avg*bat.loc[bat['team']==t1,'usage'].sum())
    
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
    bat_game['wickets/ball'] = bat_game['wickets/ball']*vwf
    bowl_game['wickets/ball'] = bowl_game['wickets/ball']*vwf
    #hundred has only 5 balls per over
    if(factor==(5/6)): bowl_game['ECON'] = 5*bowl_game['runs/ball']
    else: bowl_game['ECON'] = 6*bowl_game['runs/ball']
    
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
    
    SR = get_truncated_normal(mean=bat_game['SR'], sd=bat_game['SR']*0.36, low=0, upp=600)
    bf = get_truncated_normal(mean=bat_game['usage']*120*factor, sd=bat_game['usage']*120*0.6, low=0, upp=120*factor)
    rs = get_truncated_normal(mean=bat_game['runs/ball']*bat_game['usage']*120*factor, sd=bat_game['runs/ball']*bat_game['usage']*120*factor*0.6, low=0, upp=250*factor)
    ECON = get_truncated_normal(mean=bowl_game['ECON'], sd=bowl_game['ECON']*0.36, low=0, upp=36)
    wkts = get_truncated_normal(mean=bowl_game['wickets/ball']*bowl_game['usage']*120*factor, sd=bowl_game['wickets/ball']*bowl_game['usage']*120*factor*1.6, low=0, upp=10)
    
    if(factor != 11.25):
        bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*28
        
        if(factor == 1):    
            bat_game['xPts'] = bat_game['xPts'] + 6*(1-SR.cdf(170))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] + 4*(SR.cdf(170)-SR.cdf(150))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] + 2*(SR.cdf(150)-SR.cdf(130))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] - 2*(SR.cdf(70)-SR.cdf(60))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] - 4*(SR.cdf(60)-SR.cdf(50))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] - 6*(SR.cdf(50))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] + 4*(rs.cdf(50)-rs.cdf(30))
            bat_game['xPts'] = bat_game['xPts'] + 8*(rs.cdf(100)-rs.cdf(50))
            bat_game['xPts'] = bat_game['xPts'] + 16*(1-rs.cdf(100))
            bowl_game['xPts'] = bowl_game['xPts'] + 12*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] + 6*(ECON.cdf(5))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*(ECON.cdf(6)-ECON.cdf(5))
            bowl_game['xPts'] = bowl_game['xPts'] + 2*(ECON.cdf(7)-ECON.cdf(6))
            bowl_game['xPts'] = bowl_game['xPts'] - 2*(ECON.cdf(11)-ECON.cdf(10))
            bowl_game['xPts'] = bowl_game['xPts'] - 4*(ECON.cdf(12)-ECON.cdf(11))
            bowl_game['xPts'] = bowl_game['xPts'] - 6*(1-ECON.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*(wkts.cdf(4)-wkts.cdf(3))
            bowl_game['xPts'] = bowl_game['xPts'] + 8*(wkts.cdf(5)-wkts.cdf(4))
            bowl_game['xPts'] = bowl_game['xPts'] + 16*(1-wkts.cdf(5))
            
            #legacy code
            #bat_game['xPts'] = bat_game['xPts'] + 6*(1-poisson.cdf(k=170,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            #bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=170,mu=bat_game['SR'])-poisson.cdf(k=150,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            #bat_game['xPts'] = bat_game['xPts'] + 2*(poisson.cdf(k=150,mu=bat_game['SR'])-poisson.cdf(k=130,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            #bat_game['xPts'] = bat_game['xPts'] - 2*(poisson.cdf(k=70,mu=bat_game['SR'])-poisson.cdf(k=60,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            #bat_game['xPts'] = bat_game['xPts'] - 4*(poisson.cdf(k=60,mu=bat_game['SR'])-poisson.cdf(k=50,mu=bat_game['SR']))*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            #bat_game['xPts'] = bat_game['xPts'] - 6*poisson.cdf(k=50,mu=bat_game['SR'])*(1-poisson.cdf(k=10,mu=120*bat_game['usage']*factor))
            #bat_game['xPts'] = bat_game['xPts'] + 4*(poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=30,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            #bat_game['xPts'] = bat_game['xPts'] + 8*(poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120)-poisson.cdf(k=50,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            #bat_game['xPts'] = bat_game['xPts'] + 16*(1-poisson.cdf(k=100,mu=bat_game['runs/ball']*bat_game['usage']*factor*120))
            #bowl_game['xPts'] = bowl_game['xPts'] + 12*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            #bowl_game['xPts'] = bowl_game['xPts'] - 6*(1-poisson.cdf(k=12,mu=bowl_game['ECON']))
            #bowl_game['xPts'] = bowl_game['xPts'] - 4*(poisson.cdf(k=12,mu=bowl_game['ECON'])-poisson.cdf(k=11.,mu=bowl_game['ECON']))
            #bowl_game['xPts'] = bowl_game['xPts'] - 2*(poisson.cdf(k=11,mu=bowl_game['ECON'])-poisson.cdf(k=10,mu=bowl_game['ECON']))
            #bowl_game['xPts'] = bowl_game['xPts'] + 2*(poisson.cdf(k=7,mu=bowl_game['ECON'])-poisson.cdf(k=6,mu=bowl_game['ECON']))
            #bowl_game['xPts'] = bowl_game['xPts'] + 4*(poisson.cdf(k=6,mu=bowl_game['ECON'])-poisson.cdf(k=5,mu=bowl_game['ECON']))
            #bowl_game['xPts'] = bowl_game['xPts'] + 6*poisson.cdf(k=5,mu=bowl_game['ECON'])
            #bowl_game['xPts'] = bowl_game['xPts'] + 4*poisson.pmf(k=3,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            #bowl_game['xPts'] = bowl_game['xPts'] + 8*poisson.pmf(k=4,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            #bowl_game['xPts'] = bowl_game['xPts'] + 16*poisson.pmf(k=5,mu=bowl_game['wickets/ball']*bowl_game['usage']*120*factor)
            
        elif(factor == 2.5):
            bat_game['xPts'] = bat_game['xPts'] + 6*(1-SR.cdf(140))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] + 4*(SR.cdf(140)-SR.cdf(120))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] + 2*(SR.cdf(120)-SR.cdf(100))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] - 2*(SR.cdf(50)-SR.cdf(40))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] - 4*(SR.cdf(40)-SR.cdf(30))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] - 6*(SR.cdf(30))*(1-bf.cdf(10))
            bat_game['xPts'] = bat_game['xPts'] + 4*(rs.cdf(100)-rs.cdf(50))
            bat_game['xPts'] = bat_game['xPts'] + 8*(rs.cdf(200)-rs.cdf(100))
            bat_game['xPts'] = bat_game['xPts'] + 16*(1-rs.cdf(200))
            bowl_game['xPts'] = bowl_game['xPts'] + 12*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] + 6*(ECON.cdf(2.5))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*(ECON.cdf(3.5)-ECON.cdf(2.5))
            bowl_game['xPts'] = bowl_game['xPts'] + 2*(ECON.cdf(4.5)-ECON.cdf(3.5))
            bowl_game['xPts'] = bowl_game['xPts'] - 2*(ECON.cdf(8)-ECON.cdf(7))
            bowl_game['xPts'] = bowl_game['xPts'] - 4*(ECON.cdf(9)-ECON.cdf(8))
            bowl_game['xPts'] = bowl_game['xPts'] - 6*(1-ECON.cdf(9))
            bowl_game['xPts'] = bowl_game['xPts'] + 0*(wkts.cdf(4)-wkts.cdf(3))
            bowl_game['xPts'] = bowl_game['xPts'] + 4*(wkts.cdf(5)-wkts.cdf(4))
            bowl_game['xPts'] = bowl_game['xPts'] + 8*(1-wkts.cdf(5))
            
        elif(factor == 5/6):
            bat_game['xPts'] = bat_game['xPts'] + 5*(rs.cdf(50)-rs.cdf(30))
            bat_game['xPts'] = bat_game['xPts'] + 10*(rs.cdf(100)-rs.cdf(50))
            bat_game['xPts'] = bat_game['xPts'] + 20*(1-rs.cdf(100))
            bowl_game['xPts'] = bowl_game['xPts'] + 16*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] + 5*(wkts.cdf(4)-wkts.cdf(3))
            bowl_game['xPts'] = bowl_game['xPts'] + 10*(wkts.cdf(5)-wkts.cdf(4))
            bowl_game['xPts'] = bowl_game['xPts'] + 20*(1-wkts.cdf(5))
            
    else:
        bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*19        
        bat_game['xPts'] = bat_game['xPts'] + 4*(rs.cdf(100)-rs.cdf(50))
        bat_game['xPts'] = bat_game['xPts'] + 8*(rs.cdf(200)-rs.cdf(100))
        bat_game['xPts'] = bat_game['xPts'] + 16*(rs.cdf(300)-rs.cdf(200))
        bat_game['xPts'] = bat_game['xPts'] + 24*(1-rs.cdf(300))
        bowl_game['xPts'] = bowl_game['xPts'] + 4*(wkts.cdf(5)-wkts.cdf(4))
        bowl_game['xPts'] = bowl_game['xPts'] + 8*(1-wkts.cdf(5))
    
    if(factor == 5/6): factor = 1
    runs_t1 = round(s1*c2*league_avg*(bat_game.loc[bat_game['team']==t1,'usage'].sum()),2)
    runs_t2 = round(s2*c1*league_avg*(bat_game.loc[bat_game['team']==t2,'usage'].sum()),2)
    win_t1 = round(pow(runs_t1,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    win_t2 = round(pow(runs_t2,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    print(t1,runs_t1,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t1,'usage'].sum(),2),"overs")
    print(t2,runs_t2,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t2,'usage'].sum(),2),"overs")
    print("P(win) :-",t1,win_t1,"-",win_t2,t2)
    print(" ")
    return (bat_game,bowl_game,summary)

def cricdraft_projection(a,b,input_file1,input_file,factor,v):
    t1 = a
    t2 = b
    print(t1,"vs",t2)
    print('Venue -',v)
    venues = pd.read_excel(input_file,'Venue factors')
    vrf = venues.loc[venues['Venue']==v,'runs'].sum()
    vwf = venues.loc[venues['Venue']==v,'wkts'].sum()
    if(vrf==0):vrf=1
    if(vwf==0):vwf=1
    (summary,bat,bowl) = h2h_alt(input_file1,input_file,1,factor)
    summary = summary.apply(pd.to_numeric, errors='ignore')
    league_avg = (summary.loc[(summary['Team']!="Free Agent"),'runs bat'].mean() + summary.loc[(summary['Team']!="Free Agent"),'runs bowl'].mean())/2
    bat['runs/ball'] = bat['runs/ball']*vrf
    bat['SR'] = bat['runs/ball']*100
    bowl['runs/ball'] = bowl['runs/ball']*vrf
    
    #print(t1,"bowling",bowl.loc[bowl['team']==t1,'usage'].sum()*120*factor)
    #print(t2,"bowling",bowl.loc[bowl['team']==t2,'usage'].sum()*120*factor)
    #print(t1,"batting",bat.loc[bat['team']==t1,'usage'].sum()*120*factor)
    #print(t2,"batting",bat.loc[bat['team']==t2,'usage'].sum()*120*factor)
    #print(t1,"bowling wickets",(bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()*120*factor)
    #print(t2,"bowling wickets",(bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()*120*factor)
    #print(t1,"batting wickets",(bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()*120*factor)
    #print(t2,"batting wickets",(bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()*120*factor)
    
    #new logic for balls faced
    bb_t1 = bowl.loc[bowl['team']==t1,'usage'].sum()
    bb_t2 = bowl.loc[bowl['team']==t2,'usage'].sum()
    bf_t1 = bat.loc[bat['team']==t1,'usage'].sum()
    bf_t2 = bat.loc[bat['team']==t2,'usage'].sum()
    wbo_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()
    wbo_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()
    wba_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()
    wba_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()
    
    ut3 = min(pow(bb_t1*bf_t2*wba_t2/wbo_t1,0.5),1)
    ut4 = min(pow(bb_t2*bf_t1*wba_t1/wbo_t2,0.5),1)
    ut1b = ut3 / (bowl.loc[bowl['team']==t1,'usage'].sum())
    ut2b = ut4 / (bowl.loc[bowl['team']==t2,'usage'].sum())
    ut1bat = ut4 / (bat.loc[bat['team']==t1,'usage'].sum())
    ut2bat = ut3 / (bat.loc[bat['team']==t2,'usage'].sum())
    bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1b
    bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2b
    bat.loc[bat['team']==t2,'usage'] = bat.loc[bat['team']==t2,'usage'] * ut2bat
    bat.loc[bat['team']==t1,'usage'] = bat.loc[bat['team']==t1,'usage'] * ut1bat
    #print(bowl.loc[bowl['team']==t1,'usage'].sum(),bowl.loc[bowl['team']==t2,'usage'].sum(),ut3,ut4)
    
    bowl_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'runs/ball']*factor*120).sum()
    bowl_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'runs/ball']*factor*120).sum()
    bat_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'extras/ball']*factor*120).sum()
    bat_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'extras/ball']*factor*120).sum()
    #print("bowl t2",bowl_t2);
    #print("bowl t1",bowl_t1)
    #print("bat t2",bat_t2)
    #print("bat t1",bat_t1)
    #print(league_avg)
    s1 = bowl_t2/(league_avg*bowl.loc[bowl['team']==t2,'usage'].sum())
    c1 = bat_t2/(league_avg*bat.loc[bat['team']==t2,'usage'].sum())
    s2 = bowl_t1/(league_avg*bowl.loc[bowl['team']==t1,'usage'].sum())
    c2 = bat_t1/(league_avg*bat.loc[bat['team']==t1,'usage'].sum())
    
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
    bat_game['wickets/ball'] = bat_game['wickets/ball']*vwf
    bowl_game['wickets/ball'] = bowl_game['wickets/ball']*vwf
    #hundred has only 5 balls per over
    if(factor==(5/6)): bowl_game['ECON'] = 5*bowl_game['runs/ball']
    else: bowl_game['ECON'] = 6*bowl_game['runs/ball']
    
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

    bat_game['xPts'] = 120*factor*bat_game['usage']*(bat_game['runs/ball']+3*bat_game['6s/ball'])

    bat_game = bat_game.drop(['pp usage'],axis=1)
    bat_game = bat_game.drop(['mid usage'],axis=1)
    bat_game = bat_game.drop(['setup usage'],axis=1)
    bat_game = bat_game.drop(['death usage'],axis=1)
    bowl_game = bowl_game.drop(['pp usage'],axis=1)
    bowl_game = bowl_game.drop(['mid usage'],axis=1)
    bowl_game = bowl_game.drop(['setup usage'],axis=1)
    bowl_game = bowl_game.drop(['death usage'],axis=1)    
    
    SR = get_truncated_normal(mean=bat_game['SR'], sd=bat_game['SR']*0.36, low=0, upp=600)
    bf = get_truncated_normal(mean=bat_game['usage']*120*factor, sd=bat_game['usage']*120*0.6, low=0, upp=120*factor)
    rs = get_truncated_normal(mean=bat_game['runs/ball']*bat_game['usage']*120*factor, sd=bat_game['runs/ball']*bat_game['usage']*120*factor*0.6, low=0, upp=250*factor)
    ECON = get_truncated_normal(mean=bowl_game['ECON'], sd=bowl_game['ECON']*0.36, low=0, upp=36)
    wkts = get_truncated_normal(mean=bowl_game['wickets/ball']*bowl_game['usage']*120*factor, sd=bowl_game['wickets/ball']*bowl_game['usage']*120*factor*1.6, low=0, upp=10)
    bb = get_truncated_normal(mean=bowl_game['usage']*120*factor, sd=bowl_game['usage']*120*0.2, low=0, upp=0.2*120*factor)
    
    if(factor != 11.25):
        bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*30
        bat_game['xPts'] = bat_game['xPts'] - 25*rs.cdf(1)*(1-bf.cdf(4))
        
        if(factor <= 1):    
            bat_game['xPts'] = bat_game['xPts'] + 2.5*bat_game['runs/ball']*bat_game['usage']*120*factor*(1-SR.cdf(230))*(1-rs.cdf(16))
            bat_game['xPts'] = bat_game['xPts'] + 2*bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(230)-SR.cdf(200))*(1-rs.cdf(16))
            bat_game['xPts'] = bat_game['xPts'] + 1.5*bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(200)-SR.cdf(175))*(1-rs.cdf(16))
            bat_game['xPts'] = bat_game['xPts'] + bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(175)-SR.cdf(155))*(1-rs.cdf(16))
            bat_game['xPts'] = bat_game['xPts'] + 0.5*bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(155)-SR.cdf(140))*(1-rs.cdf(16))
            bat_game['xPts'] = bat_game['xPts'] - 5*(SR.cdf(110)-SR.cdf(95))*(1-bf.cdf(12))
            bat_game['xPts'] = bat_game['xPts'] - 10*(SR.cdf(95)-SR.cdf(75))*(1-bf.cdf(12))
            bat_game['xPts'] = bat_game['xPts'] - 15*(SR.cdf(75)-SR.cdf(50))*(1-bf.cdf(12))
            bat_game['xPts'] = bat_game['xPts'] - 20*(SR.cdf(50))*(1-bf.cdf(12))
            bat_game['xPts'] = bat_game['xPts'] + 25*(rs.cdf(100)-rs.cdf(50))
            bat_game['xPts'] = bat_game['xPts'] + 50*(1-rs.cdf(100))
            bowl_game['xPts'] = bowl_game['xPts'] + 15*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] + 100*(ECON.cdf(3.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] + 70*(ECON.cdf(4.5)-ECON.cdf(3.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] + 45*(ECON.cdf(5.5)-ECON.cdf(4.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] + 25*(ECON.cdf(6.5)-ECON.cdf(5.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] + 10*(ECON.cdf(7.5)-ECON.cdf(6.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] - 5*(ECON.cdf(10.5)-ECON.cdf(9.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] - 10*(ECON.cdf(12)-ECON.cdf(10.5))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] - 15*(ECON.cdf(14)-ECON.cdf(12))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] - 20*(1-ECON.cdf(14))*(1-bb.cdf(12))
            bowl_game['xPts'] = bowl_game['xPts'] + 25*(wkts.cdf(4)-wkts.cdf(3))
            bowl_game['xPts'] = bowl_game['xPts'] + 35*(wkts.cdf(5)-wkts.cdf(4))
            bowl_game['xPts'] = bowl_game['xPts'] + 50*(1-wkts.cdf(5))
            
        elif(factor == 2.5):
            bat_game['xPts'] = bat_game['xPts'] + 2.5*bat_game['runs/ball']*bat_game['usage']*120*factor*(1-SR.cdf(175))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] + 2*bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(175)-SR.cdf(145))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] + 1.5*bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(145)-SR.cdf(125))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] + bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(125)-SR.cdf(110))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] + 0.5*bat_game['runs/ball']*bat_game['usage']*120*factor*(SR.cdf(110)-SR.cdf(95))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] - 5*(SR.cdf(80)-SR.cdf(65))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] - 10*(SR.cdf(65)-SR.cdf(50))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] - 15*(SR.cdf(50)-SR.cdf(40))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] - 20*(SR.cdf(40))*(1-bf.cdf(24))
            bat_game['xPts'] = bat_game['xPts'] + 25*(rs.cdf(100)-rs.cdf(50))
            bat_game['xPts'] = bat_game['xPts'] + 50*(rs.cdf(150)-rs.cdf(100))
            bat_game['xPts'] = bat_game['xPts'] + 100*(1-rs.cdf(150))
            bowl_game['xPts'] = bowl_game['xPts'] + 10*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
            bowl_game['xPts'] = bowl_game['xPts'] + 100*(ECON.cdf(2.5))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] + 70*(ECON.cdf(3.5)-ECON.cdf(2.5))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] + 45*(ECON.cdf(4.25)-ECON.cdf(3.5))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] + 25*(ECON.cdf(4.75)-ECON.cdf(4.25))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] + 10*(ECON.cdf(5.25)-ECON.cdf(4.75))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] - 5*(ECON.cdf(6.5)-ECON.cdf(5.75))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] - 10*(ECON.cdf(8)-ECON.cdf(6.5))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] - 15*(ECON.cdf(10.5)-ECON.cdf(8))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] - 20*(1-ECON.cdf(10.5))*(1-bb.cdf(24))
            bowl_game['xPts'] = bowl_game['xPts'] + 25*(wkts.cdf(4)-wkts.cdf(3))
            bowl_game['xPts'] = bowl_game['xPts'] + 35*(wkts.cdf(5)-wkts.cdf(4))
            bowl_game['xPts'] = bowl_game['xPts'] + 50*(wkts.cdf(6)-wkts.cdf(5))
            bowl_game['xPts'] = bowl_game['xPts'] + 75*(wkts.cdf(7)-wkts.cdf(6))
            bowl_game['xPts'] = bowl_game['xPts'] + 100*(1-wkts.cdf(7))
            
    else:
        bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*19        
        bat_game['xPts'] = bat_game['xPts'] + 4*(rs.cdf(100)-rs.cdf(50))
        bat_game['xPts'] = bat_game['xPts'] + 8*(rs.cdf(200)-rs.cdf(100))
        bat_game['xPts'] = bat_game['xPts'] + 16*(rs.cdf(300)-rs.cdf(200))
        bat_game['xPts'] = bat_game['xPts'] + 24*(1-rs.cdf(300))
        bowl_game['xPts'] = bowl_game['xPts'] + 4*(wkts.cdf(5)-wkts.cdf(4))
        bowl_game['xPts'] = bowl_game['xPts'] + 8*(1-wkts.cdf(5))
    
    if(factor == 5/6): factor = 1
    runs_t1 = round(s1*c2*league_avg*(bat_game.loc[bat_game['team']==t1,'usage'].sum()),2)
    runs_t2 = round(s2*c1*league_avg*(bat_game.loc[bat_game['team']==t2,'usage'].sum()),2)
    win_t1 = round(pow(runs_t1,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    win_t2 = round(pow(runs_t2,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    print(t1,runs_t1,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t1,'usage'].sum(),2),"overs")
    print(t2,runs_t2,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t2,'usage'].sum(),2),"overs")
    print("P(win) :-",t1,win_t1,"-",win_t2,t2)
    print(" ")
    return (bat_game,bowl_game,summary)

def ex22_projection(a,b,input_file1,input_file,factor,v):
    t1 = a
    t2 = b
    print(t1,"vs",t2)
    print('Venue -',v)
    venues = pd.read_excel(input_file,'Venue factors')
    vrf = venues.loc[venues['Venue']==v,'runs'].sum()
    vwf = venues.loc[venues['Venue']==v,'wkts'].sum()
    if(vrf==0):vrf=1
    if(vwf==0):vwf=1
    (summary,bat,bowl) = h2h_alt(input_file1,input_file,1,factor)
    summary = summary.apply(pd.to_numeric, errors='ignore')
    league_avg = (summary.loc[(summary['Team']!="Free Agent"),'runs bat'].mean() + summary.loc[(summary['Team']!="Free Agent"),'runs bowl'].mean())/2
    bat['runs/ball'] = bat['runs/ball']*vrf
    bat['SR'] = bat['runs/ball']*100
    bowl['runs/ball'] = bowl['runs/ball']*vrf
    
    #print(t1,"bowling",bowl.loc[bowl['team']==t1,'usage'].sum()*120*factor)
    #print(t2,"bowling",bowl.loc[bowl['team']==t2,'usage'].sum()*120*factor)
    #print(t1,"batting",bat.loc[bat['team']==t1,'usage'].sum()*120*factor)
    #print(t2,"batting",bat.loc[bat['team']==t2,'usage'].sum()*120*factor)
    #print(t1,"bowling wickets",(bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()*120*factor)
    #print(t2,"bowling wickets",(bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()*120*factor)
    #print(t1,"batting wickets",(bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()*120*factor)
    #print(t2,"batting wickets",(bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()*120*factor)
    
    #new logic for balls faced
    bb_t1 = bowl.loc[bowl['team']==t1,'usage'].sum()
    bb_t2 = bowl.loc[bowl['team']==t2,'usage'].sum()
    bf_t1 = bat.loc[bat['team']==t1,'usage'].sum()
    bf_t2 = bat.loc[bat['team']==t2,'usage'].sum()
    wbo_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()
    wbo_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()
    wba_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()
    wba_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()
    
    ut3 = min(pow(bb_t1*bf_t2*wba_t2/wbo_t1,0.5),1)
    ut4 = min(pow(bb_t2*bf_t1*wba_t1/wbo_t2,0.5),1)
    ut1b = ut3 / (bowl.loc[bowl['team']==t1,'usage'].sum())
    ut2b = ut4 / (bowl.loc[bowl['team']==t2,'usage'].sum())
    ut1bat = ut4 / (bat.loc[bat['team']==t1,'usage'].sum())
    ut2bat = ut3 / (bat.loc[bat['team']==t2,'usage'].sum())
    bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1b
    bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2b
    bat.loc[bat['team']==t2,'usage'] = bat.loc[bat['team']==t2,'usage'] * ut2bat
    bat.loc[bat['team']==t1,'usage'] = bat.loc[bat['team']==t1,'usage'] * ut1bat
    #print(bowl.loc[bowl['team']==t1,'usage'].sum(),bowl.loc[bowl['team']==t2,'usage'].sum(),ut3,ut4)
    
    bowl_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'runs/ball']*factor*120).sum()
    bowl_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'runs/ball']*factor*120).sum()
    bat_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'extras/ball']*factor*120).sum()
    bat_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'extras/ball']*factor*120).sum()
    #print("bowl t2",bowl_t2);
    #print("bowl t1",bowl_t1)
    #print("bat t2",bat_t2)
    #print("bat t1",bat_t1)
    #print(league_avg)
    s1 = bowl_t2/(league_avg*bowl.loc[bowl['team']==t2,'usage'].sum())
    c1 = bat_t2/(league_avg*bat.loc[bat['team']==t2,'usage'].sum())
    s2 = bowl_t1/(league_avg*bowl.loc[bowl['team']==t1,'usage'].sum())
    c2 = bat_t1/(league_avg*bat.loc[bat['team']==t1,'usage'].sum())
    
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
    bat_game['wickets/ball'] = bat_game['wickets/ball']*vwf
    bowl_game['wickets/ball'] = bowl_game['wickets/ball']*vwf
    #hundred has only 5 balls per over
    if(factor==(5/6)): bowl_game['ECON'] = 5*bowl_game['runs/ball']
    else: bowl_game['ECON'] = 6*bowl_game['runs/ball']
    
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

    bat_game = bat_game.drop(['pp usage'],axis=1)
    bat_game = bat_game.drop(['mid usage'],axis=1)
    bat_game = bat_game.drop(['setup usage'],axis=1)
    bat_game = bat_game.drop(['death usage'],axis=1)
    bowl_game = bowl_game.drop(['pp usage'],axis=1)
    bowl_game = bowl_game.drop(['mid usage'],axis=1)
    bowl_game = bowl_game.drop(['setup usage'],axis=1)
    bowl_game = bowl_game.drop(['death usage'],axis=1)
    
    bat_game['xPts'] = 0.0; bowl_game['xPts'] = 0.0
    rs = get_truncated_normal(mean=bat_game['runs/ball']*bat_game['usage']*120*factor, sd=bat_game['runs/ball']*bat_game['usage']*120*factor*0.6, low=0, upp=250*factor)
    wkts = get_truncated_normal(mean=bowl_game['wickets/ball']*bowl_game['usage']*120*factor, sd=bowl_game['wickets/ball']*bowl_game['usage']*120*factor*1.6, low=0, upp=10)
    
    if(factor == 1):        
        bat_game['xPts'] = bat_game['xPts']+(bat_game['usage']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])*120*factor)
        bat_game['xPts'] += 7*(rs.cdf(100)-rs.cdf(50))
        bat_game['xPts'] += 15*(1-rs.cdf(100))
        bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        bowl_game['xPts'] += 20*bowl_game['usage']*bowl_game['wickets/ball']*120*factor
        bowl_game['xPts'] += 5*(wkts.cdf(4)-wkts.cdf(3))
        bowl_game['xPts'] += 8*(1-wkts.cdf(4))
        bowl_game['xPts'] += 7*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
        
    elif(factor == 2.5):
        bat_game['xPts'] += bat_game['usage']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])*120*factor
        bat_game['xPts'] += 5*(rs.cdf(100)-rs.cdf(50))
        bat_game['xPts'] += 8*(1-rs.cdf(100))
        bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        bowl_game['xPts'] += 25*bowl_game['usage']*bowl_game['wickets/ball']*120*factor
        bowl_game['xPts'] += 5*(wkts.cdf(5)-wkts.cdf(4))
        bowl_game['xPts'] += 8*(1-wkts.cdf(5))
        bowl_game['xPts'] += 5*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
        
    elif(factor == 5/6):         
        bat_game['xPts'] += bat_game['usage']*(bat_game['runs/ball']+bat_game['4s/ball']+2*bat_game['6s/ball'])*120*factor
        bat_game['xPts'] += 8*(1-rs.cdf(50))
        bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
        bowl_game['xPts'] += 20*bowl_game['usage']*bowl_game['wickets/ball']*120*factor
        bowl_game['xPts'] += 5*(wkts.cdf(4)-wkts.cdf(3))
        bowl_game['xPts'] += 8*(1-wkts.cdf(4))
        
    else: #test match
        bat_game['xPts'] += bat_game['usage']*(0.5*bat_game['runs/ball']+bat_game['4s/ball']+3*bat_game['6s/ball'])*120*factor
        bat_game['xPts'] += 5*(rs.cdf(100)-rs.cdf(50))
        bat_game['xPts'] += 8*(rs.cdf(200)-rs.cdf(100))
        bat_game['xPts'] += 15*(1-rs.cdf(200))
        bowl_game['xPts'] += 12*bowl_game['usage']*bowl_game['wickets/ball']*120*factor
        bowl_game['xPts'] += 10*(1-wkts.cdf(5))
        bowl_game['xPts'] += 1*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor
     
    if(factor == 5/6): factor = 1
    runs_t1 = round(s1*c2*league_avg*(bat_game.loc[bat_game['team']==t1,'usage'].sum()),2)
    runs_t2 = round(s2*c1*league_avg*(bat_game.loc[bat_game['team']==t2,'usage'].sum()),2)
    win_t1 = round(pow(runs_t1,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    win_t2 = round(pow(runs_t2,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    print(t1,runs_t1,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t1,'usage'].sum(),2),"overs")
    print(t2,runs_t2,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t2,'usage'].sum(),2),"overs")
    print("P(win) :-",t1,win_t1,"-",win_t2,t2)
    print(" ")
    return (bat_game,bowl_game,summary)

def coversoff_projection(a,b,input_file1,input_file,factor,v):
    t1 = a
    t2 = b
    print(t1,"vs",t2)
    print('Venue -',v)
    venues = pd.read_excel(input_file,'Venue factors')
    vrf = venues.loc[venues['Venue']==v,'runs'].sum()
    vwf = venues.loc[venues['Venue']==v,'wkts'].sum()
    if(vrf==0):vrf=1
    if(vwf==0):vwf=1
    (summary,bat,bowl) = h2h_alt(input_file1,input_file,1,factor)
    summary = summary.apply(pd.to_numeric, errors='ignore')
    league_avg = (summary.loc[(summary['Team']!="Free Agent"),'runs bat'].mean() + summary.loc[(summary['Team']!="Free Agent"),'runs bowl'].mean())/2
    bat['runs/ball'] = bat['runs/ball']*vrf
    bat['SR'] = bat['runs/ball']*100
    bowl['runs/ball'] = bowl['runs/ball']*vrf

    #print(t1,"bowling",bowl.loc[bowl['team']==t1,'usage'].sum()*120*factor)
    #print(t2,"bowling",bowl.loc[bowl['team']==t2,'usage'].sum()*120*factor)
    #print(t1,"batting",bat.loc[bat['team']==t1,'usage'].sum()*120*factor)
    #print(t2,"batting",bat.loc[bat['team']==t2,'usage'].sum()*120*factor)
    #print(t1,"bowling wickets",(bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()*120*factor)
    #print(t2,"bowling wickets",(bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()*120*factor)
    #print(t1,"batting wickets",(bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()*120*factor)
    #print(t2,"batting wickets",(bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()*120*factor)
    
    #new logic for balls faced
    bb_t1 = bowl.loc[bowl['team']==t1,'usage'].sum()
    bb_t2 = bowl.loc[bowl['team']==t2,'usage'].sum()
    bf_t1 = bat.loc[bat['team']==t1,'usage'].sum()
    bf_t2 = bat.loc[bat['team']==t2,'usage'].sum()
    wbo_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'wickets/ball']).sum()
    wbo_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'wickets/ball']).sum()
    wba_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'wickets/ball']).sum()
    wba_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'wickets/ball']).sum()
    
    ut3 = min(pow(bb_t1*bf_t2*wba_t2/wbo_t1,0.5),1)
    ut4 = min(pow(bb_t2*bf_t1*wba_t1/wbo_t2,0.5),1)
    ut1b = ut3 / (bowl.loc[bowl['team']==t1,'usage'].sum())
    ut2b = ut4 / (bowl.loc[bowl['team']==t2,'usage'].sum())
    ut1bat = ut4 / (bat.loc[bat['team']==t1,'usage'].sum())
    ut2bat = ut3 / (bat.loc[bat['team']==t2,'usage'].sum())
    bowl.loc[bowl['team']==t1,'usage'] = bowl.loc[bowl['team']==t1,'usage'] * ut1b
    bowl.loc[bowl['team']==t2,'usage'] = bowl.loc[bowl['team']==t2,'usage'] * ut2b
    bat.loc[bat['team']==t2,'usage'] = bat.loc[bat['team']==t2,'usage'] * ut2bat
    bat.loc[bat['team']==t1,'usage'] = bat.loc[bat['team']==t1,'usage'] * ut1bat
    #print(bowl.loc[bowl['team']==t1,'usage'].sum(),bowl.loc[bowl['team']==t2,'usage'].sum(),ut3,ut4)
    
    bowl_t2 = (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'runs/ball']*factor*120).sum()
    bowl_t1 = (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'runs/ball']*factor*120).sum()
    bat_t2 = (bat.loc[bat['team']==t2,'usage']*bat.loc[bat['team']==t2,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t1,'usage']*bowl.loc[bowl['team']==t1,'extras/ball']*factor*120).sum()
    bat_t1 = (bat.loc[bat['team']==t1,'usage']*bat.loc[bat['team']==t1,'runs/ball']*factor*120).sum() + (bowl.loc[bowl['team']==t2,'usage']*bowl.loc[bowl['team']==t2,'extras/ball']*factor*120).sum()
    #print("bowl t2",bowl_t2);
    #print("bowl t1",bowl_t1)
    #print("bat t2",bat_t2)
    #print("bat t1",bat_t1)
    #print(league_avg)
    s1 = bowl_t2/(league_avg*bowl.loc[bowl['team']==t2,'usage'].sum())
    c1 = bat_t2/(league_avg*bat.loc[bat['team']==t2,'usage'].sum())
    s2 = bowl_t1/(league_avg*bowl.loc[bowl['team']==t1,'usage'].sum())
    c2 = bat_t1/(league_avg*bat.loc[bat['team']==t1,'usage'].sum())
    
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
    bat_game['wickets/ball'] = bat_game['wickets/ball']*vwf
    bowl_game['wickets/ball'] = bowl_game['wickets/ball']*vwf
    #hundred has only 5 balls per over
    if(factor==(5/6)): bowl_game['ECON'] = 5*bowl_game['runs/ball']
    else: bowl_game['ECON'] = 6*bowl_game['runs/ball']

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
        
    bat_game = bat_game.drop(['pp usage'],axis=1)
    bat_game = bat_game.drop(['mid usage'],axis=1)
    bat_game = bat_game.drop(['setup usage'],axis=1)
    bat_game = bat_game.drop(['death usage'],axis=1)
    #initialize points as 0
    bat_game['xPts'] = 0.0; bowl_game['xPts'] = 0.0
    SR = get_truncated_normal(mean=bat_game['SR'], sd=bat_game['SR']*0.36, low=0, upp=600)
    bf = get_truncated_normal(mean=bat_game['usage']*120*factor, sd=bat_game['usage']*120*0.6, low=0, upp=120*factor)
    rs = get_truncated_normal(mean=bat_game['runs/ball']*bat_game['usage']*120*factor, sd=bat_game['runs/ball']*bat_game['usage']*120*factor*0.6, low=0, upp=250*factor)
    ECON = get_truncated_normal(mean=bowl_game['ECON'], sd=bowl_game['ECON']*0.36, low=0, upp=36)
    wkts = get_truncated_normal(mean=bowl_game['wickets/ball']*bowl_game['usage']*120*factor, sd=bowl_game['wickets/ball']*bowl_game['usage']*120*factor*1.6, low=0, upp=10)
    bb = get_truncated_normal(mean=bowl_game['usage']*120*factor, sd=bowl_game['usage']*120*0.2, low=0, upp=0.2*120*factor)
    #runs 4s and 6s have pts
    bat_game['xPts'] = 120*factor*bat_game['usage']*(bat_game['runs/ball']+10*bat_game['6s/ball']+6*bat_game['4s/ball'])
    #duck        
    #bat_game['xPts'] = bat_game['xPts'] - 50*rs.cdf(1)*bf.cdf(5)
    #less tha 4 runs -25
    #bat_game['xPts'] = bat_game['xPts'] - 25*(rs.cdf(4)-rs.cdf(1))*bf.cdf(5)
    #run rate bonus
    #bat_game['xPts'] = bat_game['xPts'] + 120*factor*bat_game['usage']*bat_game['runs/ball'] - (4/3)*(bat_game['usage']*factor*120)
    #SR bonuses
    bat_game['xPts'] = bat_game['xPts'] + 120*(1-SR.cdf(200))*(1-rs.cdf(20))
    bat_game['xPts'] = bat_game['xPts'] + 100*(SR.cdf(200)-SR.cdf(180))*(1-rs.cdf(20))
    bat_game['xPts'] = bat_game['xPts'] + 80*(SR.cdf(180)-SR.cdf(160))*(1-rs.cdf(25))
    bat_game['xPts'] = bat_game['xPts'] + 60*(SR.cdf(160)-SR.cdf(140))*(1-rs.cdf(25))
    bat_game['xPts'] = bat_game['xPts'] - 20*(SR.cdf(140)-SR.cdf(130))*(1-bf.cdf(6))
    bat_game['xPts'] = bat_game['xPts'] - 80*(SR.cdf(130)-SR.cdf(100))*(1-bf.cdf(6))
    bat_game['xPts'] = bat_game['xPts'] - 100*(SR.cdf(100))*(1-bf.cdf(6))
    #milestone bonuses
    bat_game['xPts'] = bat_game['xPts'] + 20*(rs.cdf(35)-rs.cdf(20))
    bat_game['xPts'] = bat_game['xPts'] + 40*(rs.cdf(50)-rs.cdf(35))
    bat_game['xPts'] = bat_game['xPts'] + 70*(rs.cdf(65)-rs.cdf(50))
    bat_game['xPts'] = bat_game['xPts'] + 120*(rs.cdf(75)-rs.cdf(65))
    bat_game['xPts'] = bat_game['xPts'] + 150*(1-rs.cdf(75))       
    #bowler cant bowl more than 20% of the overs except in tests
    if(factor!=11.25):bowl_game['usage'] = np.minimum(bowl_game['usage'],0.2)
    bowl_game = bowl_game.drop(['pp usage'],axis=1)
    bowl_game = bowl_game.drop(['mid usage'],axis=1)
    bowl_game = bowl_game.drop(['setup usage'],axis=1)
    bowl_game = bowl_game.drop(['death usage'],axis=1)
    #wicket is 35 pts
    bowl_game['xPts'] = 120*factor*bowl_game['usage']*bowl_game['wickets/ball']*35
    #dot balls pts
    bowl_game['xPts'] += 120*factor*bowl_game['usage']*bowl_game['dots/ball']*5
    #ECON bonuses
    if(factor==5/6):
        bowl_game['xPts'] = bowl_game['xPts'] - 100*(1-ECON.cdf(8.5))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] - 80*(ECON.cdf(8.5)-ECON.cdf(7.5))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] - 40*(ECON.cdf(7.5)-ECON.cdf(7))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 60*(ECON.cdf(7)-ECON.cdf(6))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 80*(ECON.cdf(6)-ECON.cdf(5))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 100*(ECON.cdf(5)-ECON.cdf(4))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 120*(ECON.cdf(3))*(1-bb.cdf(6))
    else:
        bowl_game['xPts'] = bowl_game['xPts'] - 100*(1-ECON.cdf(9.5))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] - 80*(ECON.cdf(9.5)-ECON.cdf(8.5))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] - 40*(ECON.cdf(8.5)-ECON.cdf(8))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 60*(ECON.cdf(8)-ECON.cdf(7))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 80*(ECON.cdf(7)-ECON.cdf(6))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 100*(ECON.cdf(6)-ECON.cdf(4))*(1-bb.cdf(6))
        bowl_game['xPts'] = bowl_game['xPts'] + 120*(ECON.cdf(4))*(1-bb.cdf(6))
    #milestone bonuses
    #bowl_game['xPts'] = bowl_game['xPts'] + 30*(wkts.cdf(3)-wkts.cdf(2))
    bowl_game['xPts'] = bowl_game['xPts'] + 80*(wkts.cdf(4)-wkts.cdf(3))
    bowl_game['xPts'] = bowl_game['xPts'] + 120*(wkts.cdf(5)-wkts.cdf(4))
    bowl_game['xPts'] = bowl_game['xPts'] + 150*(wkts.cdf(6)-wkts.cdf(5))
    bowl_game['xPts'] = bowl_game['xPts'] + 200*(1-wkts.cdf(6))
    #maiden over
    bowl_game['xPts'] = bowl_game['xPts'] + 100*np.power(bowl_game['dots/ball'],6)*20*bowl_game['usage']*factor

    if(factor == 5/6): factor = 1
    runs_t1 = round(s1*c2*league_avg*(bat_game.loc[bat_game['team']==t1,'usage'].sum()),2)
    runs_t2 = round(s2*c1*league_avg*(bat_game.loc[bat_game['team']==t2,'usage'].sum()),2)
    win_t1 = round(pow(runs_t1,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    win_t2 = round(pow(runs_t2,15.5/factor)/(pow(runs_t1,15.5/factor)+pow(runs_t2,15.5/factor)),3)
    print(t1,runs_t1,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t1,'usage'].sum(),2),"overs")
    print(t2,runs_t2,"runs in",round(20*factor*bat_game.loc[bat_game['team']==t2,'usage'].sum(),2),"overs")
    print("P(win) :-",t1,win_t1,"-",win_t2,t2)
    print(" ")
    return (bat_game,bowl_game,summary)

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
        #partimers removed from bowling list, min 1 over in t20s, review this
        if(coversoff == 1 or cricdraft == 1): bowl_game.drop(bowl_game[bowl_game['usage'] < 0.05].index, inplace = True)
        else: bowl_game.drop(bowl_game[bowl_game['usage'] < 0.01].index, inplace = True)
        final.append([x,p_team,0,bat_game.loc[(bat_game['batsman']==x),'xPts'].mean(),bowl_game.loc[(bowl_game['bowler']==x),'xPts'].mean(),bat_game.loc[(bat_game['batsman']==x),'usage'].mean(),bowl_game.loc[(bowl_game['bowler']==x),'usage'].mean()])
        
    final = pd.DataFrame(final)
    final.columns = final.iloc[0];final = final.drop(0)
    final = final.fillna(0)
    if(coversoff == 1): final['total'] = final['bat'] + final['bowl'] + 25
    elif(ex22 == 1 or cricdraft == 1): final['total'] = final['bat'] + final['bowl']
    else: final['total'] = final['bat'] + final['bowl'] + 4
    #final['max'] = final['bat max'] + final['bowl max'] + 4
    final = final.sort_values(['total'], ascending=[False])
    return final

def execute_projections():
    c = 0;
    for x in home:
        a = home[c]
        b = opps[c]
        v = venue[c]
        if (c==0):
            if(coversoff == 1): (bat_game,bowl_game,table) = coversoff_projection(a,b,input_file1,input_file,f,v)
            elif(cricdraft == 1): (bat_game,bowl_game,table) = cricdraft_projection(a,b,input_file1,input_file,f,v)
            elif(ex22 == 1): (bat_game,bowl_game,table) = ex22_projection(a,b,input_file1,input_file,f,v)
            else: (bat_game,bowl_game,table) = gw_projection(a,b,input_file1,input_file,f,v)
        else : 
            if(coversoff == 1): (bat,bowl,table) = coversoff_projection(a,b,input_file1,input_file,f,v)
            elif(cricdraft == 1): (bat,bowl,table) = cricdraft_projection(a,b,input_file1,input_file,f,v)
            elif(ex22 == 1): (bat,bowl,table) = ex22_projection(a,b,input_file1,input_file,f,v)
            else: (bat,bowl,table) = gw_projection(a,b,input_file1,input_file,f,v)
            bat_game = pd.concat([bat_game,bat])
            bowl_game = pd.concat([bowl_game,bowl])
        c = c + 1
    a_final = final_projections(bat_game,bowl_game)
    return a_final,table,bat_game,bowl_game

a_final,a_table,bat_game,bowl_game = execute_projections()

# %% generate n unique combos
def randomizer(a_projection,home,opps,unique_teams):
    team = [["1","2","3","4","5","6","7","8","9","10","11","C","VC","xPts"]]; i=0; j=0;
    players = a_projection.loc[(a_projection['team'] == home) | (a_projection['team'] == opps)]
    p = pow(players['total'],3).tolist()
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
            p2 = pow(cap['total'],4).tolist()
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

if(ex22 == 0 and coversoff == 0):
    c=0;combinations=[];
    while c<len(home):
        co = randomizer(a_final,home[c],opps[c],unique_combos)
        combinations.append(co)
        #a_diffs.append(dif)
        c+=1

#%% dump projections to the desired file
date = now.strftime("%m-%d-%y")
def write_to_excel(date,output_dump,final):
    try:
        book = load_workbook(output_dump)
        with pd.ExcelWriter(output_dump, engine = 'openpyxl',mode='a', if_sheet_exists = 'replace') as writer:
            writer.book = book
            writer.sheets = {ws.title:ws for ws in book.worksheets}
            final.to_excel(writer, sheet_name=f'{date}',index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(output_dump) as writer:        
            final.to_excel(writer, sheet_name=f'{date}',index=False)
            
def cricdraft_write(gw,output_dump,final):
    try:
        book = load_workbook(output_dump)
        with pd.ExcelWriter(output_dump, engine = 'openpyxl',mode='a', if_sheet_exists = 'replace') as writer:
            writer.book = book
            writer.sheets = {ws.title:ws for ws in book.worksheets}
            final.to_excel(writer, sheet_name = f'gw{gw}',index=False)
    except FileNotFoundError:
        with pd.ExcelWriter(output_dump) as writer:        
            final.to_excel(writer, sheet_name=f'gw{gw}', index=False)

if(writer != 0 and gw == 0):
    write_to_excel(date,output_dump,a_final)
elif(coversoff == 0 and ex22 == 0 and cricdraft ==0 and writer == 1):
    output_dump = f'{path}/outputs/{comp}_gw{gw}.xlsx'
    with pd.ExcelWriter(output_dump) as writer:        
        a_final.to_excel(writer, sheet_name='Points',index=False)
elif(coversoff == 1 and gw > 0 and writer == 1):
    output_dump = f'{path}/outputs/{comp}_cricbattle.xlsx'
    with pd.ExcelWriter(output_dump) as writer:        
        a_final.to_excel(writer, sheet_name="Points", index=False)
elif(cricdraft == 1 and gw > 0 and writer == 1):
    output_dump = f'{path}/outputs/{comp}_draft.xlsx'
    cricdraft_write(gw,output_dump,a_final)
