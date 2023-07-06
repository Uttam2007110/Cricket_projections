# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 18:04:33 2023

@author: Subramanya.Ganti
"""
#%% initialize
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import datetime
import time

league = 'EPL'
season = '2022-2023'
input_file = 'C:/Users/Subramanya.Ganti/Downloads/fbref.xlsx'
player_list = pd.read_excel(input_file,'players')
team_list = pd.read_excel(input_file,'teams')
team_list.drop(team_list.loc[team_list[league]==0].index, inplace=True)
team_list = team_list.drop(['EPL', 'Bundesliga','La Liga','Serie A','Ligue 1'], axis=1)

#%% define functions
def column_names_corrected(columns):
    i = 0; new_columns = []
    while i<len(columns):
        new_columns.append(columns[i][1])
        i += 1
    return new_columns

def team_strengths():
    df_list2 = pd.read_html('https://projects.fivethirtyeight.com/soccer-predictions/global-club-rankings')
    df_list2 = df_list2[0]
    df_list2.columns = column_names_corrected(df_list2.columns)
    df_list2 = df_list2.drop('1-week change', axis=1)
    df_list2 = df_list2.drop('Rank', axis=1)
    return df_list2

def players_in_league(team_list):
    i=0; 
    while i<len(team_list):
        code = team_list.iloc[[i]]['Code'].values[0]
        team = team_list.iloc[[i]]['Team'].values[0]
        df_team = pd.read_html(f'https://fbref.com/en/squads/{code}/{team}-Stats')
        player_team = df_team[0]
        player_team.drop(player_team.tail(2).index,inplace=True)
        player_team.columns = column_names_corrected(player_team.columns)
        player_team = player_team['Player']
        if(i==0): player_league_list = player_team
        else:  player_league_list = pd.concat([player_league_list, player_team], ignore_index=True)
        i += 1
        print(team,"data extracted")
        time.sleep(1)
    return player_league_list

def players_id(player_list,player_league_list):
    i=0; list_dummy = [["Player","Link"]]; c=0
    print("player exception list")
    while i<len(player_league_list):
        try : 
            link = player_list.loc[(player_list['PlayerFBref']==player_league_list[i]),'UrlFBref'].values[0]
            list_dummy.append([player_league_list[i],link])
        except IndexError:
            c += 1
            print(player_league_list[i])
            #list_dummy.append([player_league_list[i],"NA"])
        i += 1
    print(c,"total errors")
    list_dummy = pd.DataFrame(list_dummy)
    list_dummy.columns = list_dummy.iloc[0];list_dummy = list_dummy.drop(0)
    list_dummy = list_dummy.drop_duplicates(subset=['Player'])
    list_dummy = list_dummy.reset_index()
    list_dummy = list_dummy.drop(['index'], axis=1)
    return list_dummy

def player_corrected(player_league_list,n):
    link = player_league_list.iloc[n]['Link']
    name = player_league_list.iloc[n]['Player']
    i = 0; c = 0
    try:
        df_player = pd.read_html(f'https://fbref.com/en/players/{link}')
        while i<len(df_player): 
            lol = df_player[i]
            lol.columns = column_names_corrected(lol.columns)
            try : 
                df_player[i] = lol[lol['Age'].apply(lambda x: str(x).isdigit())]
                df_player[i] = df_player[i].drop(['Matches'], axis=1)
            except KeyError:
                c += 1
                df_player[i] = df_player[i]
            df_player[i] = df_player[i].reset_index()
            df_player[i] = df_player[i].drop(['index'], axis=1)      
            df_player[i] = df_player[i].apply(pd.to_numeric, errors='ignore')
            df_player[i] = df_player[i].fillna(0)
            i += 1
    except ValueError:
        df_player = [[]] 
        
    #outfielders who have played as an emergency keeper
    if(name=="Pontus Jansson"):
        del df_player[-1]
    return (df_player,c)

def weighted(df_player,season,n,name):
    j = 1; c = 0
    age=99;w_mins=0; w_g=0; w_a=0; w_xgd=0; w_xad=0; w_cc=0; w_p=0; w_pa=0; w_s=0; w_sot=0; w_t=0; w_i=0; w_yc=0; w_rc=0; w_pen=0; w_pena=0;
    w_mp=0; w_minp=0; w_stp=0; w_subp=0; w_minst=0; w_min_sub=0; team = 'Free Agent'
    weight=16; 
    if(len(df_player)-n < 3): return [name,age,team,w_stp,w_subp,w_minst,w_min_sub,w_mins,w_g,w_s,w_sot,w_xgd,w_p,w_pa,w_a,w_xad,w_cc,w_t,w_i,w_yc,w_rc,w_pen,w_pena,weight]
    if(len(df_player)-n == 9): c = 0
    if(len(df_player)-n == 10): c = 1
    if(len(df_player)-n == 11): c = 2  
    df2 = df_player[n+1+c]    #shooting
    df3 = df_player[n+2+c]    #passing
    df4 = df_player[n+5+c]    #tackles and interceptions
    df5 = df_player[n+7+c]    #starts and subs
    df6 = df_player[n+8+c]    #discipline
    if(c==1):c=2
    df1 = df_player[n+c]      #general
    
    index1 = df1.index[(df1['Season']==season)].values
    index = df3.index[(df3['Season']==season)].values
    for x in index1:
        age = df1.iloc[x]['Age']
        team = df1.iloc[x]['Squad']
        w_mins += 6*df1.iloc[x]['Min']
        if(df1.iloc[x]['Min']==0): weight-=6
        w_mp += 6*df1.iloc[x]['MP']
        w_minp += 6*df5.iloc[x]['Min%']
        w_stp += 6*df5.iloc[x]['Starts']
        w_subp += 6*df5.iloc[x]['Subs']
        w_minst += 6*df5.iloc[x]['Mn/Start']*df5.iloc[x]['Starts']
        w_min_sub += 6*df5.iloc[x]['Mn/Sub']*df5.iloc[x]['Subs']
    for x in index:
        try : 
            w_pen += 6*df2.iloc[x]['PK']
            w_pena += 6*df2.iloc[x]['PKatt']
            w_g += 6*df2.iloc[x]['Gls']
            w_s += 6*df2.iloc[x]['Sh']
            w_sot += 6*df2.iloc[x]['SoT']
            w_xgd += 6*df2.iloc[x]['G-xG']
        except KeyError: 
            w_pen += 0
            w_pena += 0
            w_g += 0
            w_s += 0
            w_sot += 0
            w_xgd += 0
        w_p += 6*df3.iloc[x]['Cmp']
        w_pa += 6*df3.iloc[x]['Att']
        w_a += 6*df3.iloc[x]['Ast']
        w_xad += 6*df3.iloc[x]['A-xAG']
        w_cc += 6*df3.iloc[x]['KP']
        w_t += 6*df4.iloc[x]['Tkl']
        w_i += 6*df4.iloc[x]['Int']
        w_yc += 6*df6.iloc[x]['CrdY']
        w_rc += 6*df6.iloc[x]['CrdR']
        
    while j<5:
        index01 = df1.index[(df1['Age']==age-j)].values
        index00 = df3.index[(df3['Age']==age-j)].values
        for x in index01:
            w_mins += (5-j)*df1.iloc[x]['Min']
            if(df1.iloc[x]['Min']==0): weight-=5-j
            w_mp += (5-j)*df1.iloc[x]['MP']
            w_minp += (5-j)*df5.iloc[x]['Min%']
            w_stp += (5-j)*df5.iloc[x]['Starts']
            w_subp += (5-j)*df5.iloc[x]['Subs']
            w_minst += (5-j)*df5.iloc[x]['Mn/Start']*df5.iloc[x]['Starts']
            w_min_sub += (5-j)*df5.iloc[x]['Mn/Sub']*df5.iloc[x]['Subs']
        for x in index00:
            try : 
                w_pen += (5-j)*df2.iloc[x]['PK']
                w_pena += (5-j)*df2.iloc[x]['PKatt']
                w_g += (5-j)*df2.iloc[x]['Gls']
                w_s += (5-j)*df2.iloc[x]['Sh']
                w_sot += (5-j)*df2.iloc[x]['SoT']
                w_xgd += (5-j)*df2.iloc[x]['G-xG']
            except KeyError: 
                w_pen += 0
                w_pena += 0
                w_g += 0
                w_s += 0
                w_sot += 0
                w_xgd += 0
            w_p += (5-j)*df3.iloc[x]['Cmp']
            w_pa += (5-j)*df3.iloc[x]['Att']
            w_a += (5-j)*df3.iloc[x]['Ast']
            w_xad += (5-j)*df3.iloc[x]['A-xAG']
            w_cc += (5-j)*df3.iloc[x]['KP']
            w_t += (5-j)*df4.iloc[x]['Tkl']
            w_i += (5-j)*df4.iloc[x]['Int']
            w_yc += (5-j)*df6.iloc[x]['CrdY']
            w_rc += (5-j)*df6.iloc[x]['CrdR']            
        j += 1
    
    if(c>0): 
        w_pen = 0
        w_pena = 0
        w_g = 0
        w_s = 0
        w_sot = 0
        w_xgd = 0
    w_minst = w_minst/(w_stp+0.000001)
    w_min_sub = w_min_sub/(w_subp+0.000001)
    w_stp = w_minp*w_stp/(100*w_mp*weight)
    w_subp = w_minp*w_subp/(100*w_mp*weight)
    
    return [name,age,team,w_stp,w_subp,w_minst,w_min_sub,w_mins,w_g,w_s,w_sot,w_xgd,w_p[0],w_pa[0],w_a,w_xad,w_cc,w_t[0],w_i,w_yc,w_rc,w_pen,w_pena,weight]

def weighted_proj_dump(player_league_list):
    i=0; player_weighted=[["Player","Age","Team","Start%","Sub%","Mins/St","Mins/Sub","Mins","Goals","Shots","SOT","xGD","P","PA","Assists","xAD","KP","Tackles","Int","YC","RC","Pens","Pens A","Weight"]]
    now = datetime.datetime.now()
    print("projections dump starting now",now.time())
    while i<len(player_league_list):
        (df_player,c) = player_corrected(player_league_list,i)
        name = player_league_list.iloc[i]['Player']
        if(len(df_player)>=9):           
            print(i,name)            
            player_weighted.append(weighted(df_player,season,c,name))
        else:
            print(i,name,"skipped due to lack of data")
        i+=1
        time.sleep(1)
    player_weighted = pd.DataFrame(player_weighted)
    player_weighted.columns = player_weighted.iloc[0];player_weighted = player_weighted.drop(0)
    player_weighted = player_weighted.apply(pd.to_numeric, errors='ignore')
    now2 = datetime.datetime.now()
    print("projections dump completed",now2.time())
    return player_weighted

def player_debug(player_league_list,i):
    player_weighted = []
    (df_player,c) = player_corrected(player_league_list,i)
    name = player_league_list.iloc[i]['Player']
    print(name)
    try:
        player_weighted=(weighted(df_player,season,c,name))
    except KeyError:
        print("error: label mismatch")
    return (df_player,c,player_weighted)

#%% player list
player_league_list = players_in_league(team_list)
player_league_list = players_id(player_list,player_league_list)

#%% player projections
#(df_player,c,player_weighted) = player_debug(player_league_list,10)
player_weighted = weighted_proj_dump(player_league_list)
