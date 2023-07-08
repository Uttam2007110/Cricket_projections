# -*- coding: utf-8 -*-
"""
Created on Wed Jun 7 12:41:19 2023
fangraphs projections to d11 xPts
@author: Subramanya.Ganti
"""
# %%  specify the teams playing
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np

home = ["HOU"]
opps = ["SEA"]
display = 'Athletics'    #Blue%20Jays
date = '2023-07-08'     #yyyy-mm-dd  

# %%  pull projections from fangraphs
def generate():
    i = 1
    df_bat = []; df_pit = []; df_rv = []
    while i < 31:
      df_list = pd.read_html(f'https://www.fangraphs.com/projections?pos=&stats=bat&type=rzips&statgroup=fantasy&fantasypreset=dashboard&lg=&team={i}')
      df_bat_new = df_list[6]
      if(i==1): df_bat = df_bat_new
      else: df_bat = pd.concat([df_bat, df_bat_new])
      
      df_list = pd.read_html(f'https://www.fangraphs.com/projections?pos=&stats=sta&type=rzips&statgroup=fantasy&fantasypreset=dashboard&lg=&team={i}')
      df_pit_new = df_list[6]
      if(i==1): df_pit = df_pit_new
      else: df_pit = pd.concat([df_pit, df_pit_new])
      
      df_list = pd.read_html(f'https://www.fangraphs.com/projections?pos=&stats=rel&type=rzips&statgroup=fantasy&fantasypreset=dashboard&lg=&team={i}')
      df_rv_new = df_list[6]
      if(i==1): df_rv = df_rv_new
      else: df_rv = pd.concat([df_rv, df_rv_new])
      print(df_bat_new['Team'][0],i)
      i += 1
    return (df_bat,df_pit,df_rv)  

def unique_list(df_bat,df_st,df_rv):
    unique_bat = df_bat[["Name","Team"]]
    unique_st = df_st[["Name","Team"]]
    unique_rv = df_rv[["Name","Team"]]
    unique_bat['Starting'] = 0
    unique_st['Starting'] = 0
    unique_rv['Starting'] = 1
       
    #with pd.ExcelWriter(output_file) as writer:        
    #    unique_bat.to_excel(writer, sheet_name="Hitters", index=False)
    #    unique_st.to_excel(writer, sheet_name="Starters", index=False)
    #    unique_rv.to_excel(writer, sheet_name="Releivers", index=False)
    
    print("dumped file with all avaliable players")
    return (unique_bat,unique_st,unique_rv)   

def calculate(df_bat,df_st,df_rv,home,opps,lineups_bat,lineups_st,lineups_rv):
    #lineups_bat = pd.read_excel(output_file,'Hitters')
    #lineups_st = pd.read_excel(output_file,'Starters')
    #lineups_rv = pd.read_excel(output_file,'Releivers')

    bat = [["Player","Team","PA","H","2B","3B","HR","R","RBI","BB","SO","SB","LOB","IP","xPts"]]
    st = [["Player","Team","PA","IP","H","ER","HR","SO","BB","WHIP","LOB","ERA","xPts"]]
    rv = [["Player","Team","PA","IP","H","ER","HR","SO","BB","WHIP","LOB","ERA","xPts"]]

    for x in df_bat.values:
        #print(x)
        if(lineups_bat[lineups_bat['Name'] == x[1]]['Team'].values[0] == home and lineups_bat[lineups_bat['Name'] == x[1]]['Starting'].values[0] == 1):
            bat.append([x[1],x[2],x[4]/x[3],x[6]/x[4],x[7]/x[4],x[8]/x[4],x[9]/x[4],x[10]/x[4],x[11]/x[4],(x[12]+x[14])/x[4],x[13]/x[4],x[15]/x[4],0,0,0])
        if(lineups_bat[lineups_bat['Name'] == x[1]]['Team'].values[0] == opps and lineups_bat[lineups_bat['Name'] == x[1]]['Starting'].values[0] == 1):
            bat.append([x[1],x[2],x[4]/x[3],x[6]/x[4],x[7]/x[4],x[8]/x[4],x[9]/x[4],x[10]/x[4],x[11]/x[4],(x[12]+x[14])/x[4],x[13]/x[4],x[15]/x[4],0,0,0])
    bat = pd.DataFrame(bat)
    bat.columns = bat.iloc[0];bat = bat.drop(0)
    bat['LOB'] = (bat['H']+bat['BB']-bat['R'])/(bat['H']+bat['BB']-1.4*bat['HR'])
    bat['IP'] = (bat['PA']-bat['PA']*bat['R']-bat['PA']*bat['LOB']*(bat['H']+bat['BB']))/3
    bat_home_factor = 9/sum(bat.loc[(bat['Team']==home),'IP'])
    bat_opps_factor = 9/sum(bat.loc[(bat['Team']==opps),'IP'])
    bat.loc[bat["Team"] == home, "PA"] = bat["PA"]*bat_home_factor
    bat.loc[bat["Team"] == opps, "PA"] = bat["PA"]*bat_opps_factor
    bat.loc[bat["Team"] == home, "IP"] = bat["IP"]*bat_home_factor
    bat.loc[bat["Team"] == opps, "IP"] = bat["IP"]*bat_opps_factor

    for x in df_st.values:
        if(lineups_st[lineups_st['Name'] == x[1]]['Team'].values[0] == home and lineups_st[lineups_st['Name'] == x[1]]['Starting'].values[0] == 1):
            st.append([x[1],x[2],0,x[5]/x[4],x[11]/x[5],x[12]/x[5],x[13]/x[5],x[14]/x[5],x[15]/x[5],x[21],x[23],x[24],0])
        if(lineups_st[lineups_st['Name'] == x[1]]['Team'].values[0] == opps and lineups_st[lineups_st['Name'] == x[1]]['Starting'].values[0] == 1):
            st.append([x[1],x[2],0,x[5]/x[4],x[11]/x[5],x[12]/x[5],x[13]/x[5],x[14]/x[5],x[15]/x[5],x[21],x[23],x[24],0])
    st = pd.DataFrame(st)
    st.columns = st.iloc[0];st = st.drop(0)

    for x in df_rv.values:
        if(lineups_rv[lineups_rv['Name'] == x[1]]['Team'].values[0] == home and lineups_rv[lineups_rv['Name'] == x[1]]['Starting'].values[0] == 1):
            rv.append([x[1],x[2],0,x[5]/x[4],x[11]/x[5],x[12]/x[5],x[13]/x[5],x[14]/x[5],x[15]/x[5],x[21],x[23],x[24],0])
        if(lineups_rv[lineups_rv['Name'] == x[1]]['Team'].values[0] == opps and lineups_rv[lineups_rv['Name'] == x[1]]['Starting'].values[0] == 1):
            rv.append([x[1],x[2],0,x[5]/x[4],x[11]/x[5],x[12]/x[5],x[13]/x[5],x[14]/x[5],x[15]/x[5],x[21],x[23],x[24],0])
    rv = pd.DataFrame(rv)
    rv.columns = rv.iloc[0];rv = rv.drop(0)

    home_ip_delta = 9 - sum(st.loc[(st['Team']==home),'IP'])
    home_ip_factor = home_ip_delta/sum(rv.loc[(rv['Team']==home),'IP'])
    opps_ip_delta = 9 - sum(st.loc[(st['Team']==opps),'IP'])
    opps_ip_factor = opps_ip_delta/sum(rv.loc[(rv['Team']==opps),'IP'])

    rv.loc[rv["Team"] == home, "IP"] = rv["IP"]*home_ip_factor
    rv.loc[rv["Team"] == opps, "IP"] = rv["IP"]*opps_ip_factor

    for x in bat:
        if(x!='Player'and x!='Team'and x!='PA'and x!='LOB'and x!='IP'):bat[x] = bat[x]*bat['PA']
    bat_team = bat.groupby('Team', as_index=False).sum()
    bat_team = bat_team.drop(['Player'], axis=1)
    bat_team['LOB'] = (bat_team['H']+bat_team['BB']-bat_team['R'])/(bat_team['H']+bat_team['BB']-1.4*bat_team['HR'])

    pit = pd.concat([st, rv], axis=0)
    for x in pit:
        if(x!='Player'and x!='Team'and x!='WHIP'and x!='LOB'and x!='ERA'and x!='IP'):pit[x] = pit[x]*pit['IP']
    pit_team = pit.groupby('Team', as_index=False).sum()
    pit_team = pit_team.drop(['Player'], axis=1)
    pit_team['LOB'] = (pit_team['H']+pit_team['BB']-pit_team['ER'])/(pit_team['H']+pit_team['BB']-1.4*pit_team['HR'])

    league_bat = df_bat[["Name","Team","PA","H","2B","3B","HR","R","RBI","BB","SO","SB",]]
    league_bat['Name'] = "lol"
    league_bat = league_bat.groupby('Name', as_index=False).sum()
    league_bat = league_bat.drop(['Name'], axis=1)

    league_pit = pd.concat([df_st, df_rv], axis=0)
    league_pit = league_pit[["Name","Team","IP","H","ER","HR","SO","BB"]]
    league_pit['Name'] = "lol"
    league_pit = league_pit.groupby('Name', as_index=False).sum()
    league_pit = league_pit.drop(['Name'], axis=1)

    bat_team_factor = bat_team.copy()
    for x in bat_team_factor:
        #print(x)
        if(x == 'H' or x == 'HR' or x == 'BB' or x == 'SO'):
            bat_team_factor.loc[(bat_team_factor['Team']==home),x] = pit_team.loc[(pit_team['Team']==opps),x].values[0]/((9*league_pit[x]/league_pit['IP']).values[0]) 
            bat_team_factor.loc[(bat_team_factor['Team']==opps),x] = pit_team.loc[(pit_team['Team']==home),x].values[0]/((9*league_pit[x]/league_pit['IP']).values[0])
        if(x == 'PA' or x == 'SB' or x == 'LOB' or x == 'IP'):
            bat_team_factor.loc[(bat_team_factor['Team']==home),x] = 1
            bat_team_factor.loc[(bat_team_factor['Team']==opps),x] = 1
        if(x == 'R' or x == 'RBI'):
            bat_team_factor.loc[(bat_team_factor['Team']==home),x] = pit_team.loc[(pit_team['Team']==opps),'ER'].values[0]/((9*league_pit['ER']/league_pit['IP']).values[0]) 
            bat_team_factor.loc[(bat_team_factor['Team']==opps),x] = pit_team.loc[(pit_team['Team']==home),'ER'].values[0]/((9*league_pit['ER']/league_pit['IP']).values[0])
        if(x == '2B' or x == '3B'):
            bat_team_factor.loc[(bat_team_factor['Team']==home),x] = pit_team.loc[(pit_team['Team']==opps),'H'].values[0]/((9*league_pit['H']/league_pit['IP']).values[0]) 
            bat_team_factor.loc[(bat_team_factor['Team']==opps),x] = pit_team.loc[(pit_team['Team']==home),'H'].values[0]/((9*league_pit['H']/league_pit['IP']).values[0])

    pit_team_factor = pit_team.copy()
    for x in pit_team:
        #print(x)
        if(x == 'WHIP' or x == 'ERA' or x == 'LOB' or x == 'IP'):
            pit_team_factor.loc[(pit_team_factor['Team']==home),x] = 1
            pit_team_factor.loc[(pit_team_factor['Team']==opps),x] = 1
        if(x == 'H' or x == 'HR' or x == 'BB' or x == 'SO'):
            pit_team_factor.loc[(pit_team_factor['Team']==home),x] = (bat_team.loc[(bat_team['Team']==opps),x].values[0]/bat_team.loc[(bat_team['Team']==opps),'PA'].values[0])/((league_bat[x]/league_bat['PA']).values[0]) 
            pit_team_factor.loc[(pit_team_factor['Team']==opps),x] = (bat_team.loc[(bat_team['Team']==home),x].values[0]/bat_team.loc[(bat_team['Team']==home),'PA'].values[0])/((league_bat[x]/league_bat['PA']).values[0])
        if(x == 'ER'):
            pit_team_factor.loc[(pit_team_factor['Team']==home),x] = (bat_team.loc[(bat_team['Team']==opps),'R'].values[0]/bat_team.loc[(bat_team['Team']==opps),'PA'].values[0])/((league_bat['R']/league_bat['PA']).values[0]) 
            pit_team_factor.loc[(pit_team_factor['Team']==opps),x] = (bat_team.loc[(bat_team['Team']==home),'R'].values[0]/bat_team.loc[(bat_team['Team']==home),'PA'].values[0])/((league_bat['R']/league_bat['PA']).values[0])

    for x in bat:
        #print(x)
        if(x != 'Player' and x!= 'Team'):
            bat.loc[(bat['Team']==home),x] = bat.loc[(bat['Team']==home),x] * bat_team_factor.loc[(bat_team_factor['Team']==home),x].values[0]
            bat.loc[(bat['Team']==opps),x] = bat.loc[(bat['Team']==opps),x] * bat_team_factor.loc[(bat_team_factor['Team']==opps),x].values[0]
            
    for x in pit:
        #print(x)
        if(x != 'Player' and x!= 'Team'):
            pit.loc[(pit['Team']==home),x] = pit.loc[(pit['Team']==home),x] * pit_team_factor.loc[(pit_team_factor['Team']==home),x].values[0]
            pit.loc[(pit['Team']==opps),x] = pit.loc[(pit['Team']==opps),x] * pit_team_factor.loc[(pit_team_factor['Team']==opps),x].values[0]

    return (bat,pit)

def results(bat,pit):
    bat['LOB'] = (bat['H']+bat['BB']-bat['R'])/(bat['H']+bat['BB']-1.4*bat['HR'])
    pit['ERA'] = 9*pit['ER']/pit['IP']
    pit['LOB'] = (pit['H']+pit['BB']-pit['ER'])/(pit['H']+pit['BB']-1.4*pit['HR'])
    pit['WHIP'] = (pit['H'] + pit['BB'])/pit['IP']
    pit = pit.drop(['PA'], axis=1)
    bat = bat.drop(['IP'], axis=1)
    bat = bat.drop(['LOB'], axis=1)

    bat['xPts'] = 4*(bat['BB']+bat['H']-bat['2B']-bat['3B']-bat['HR'])+6*bat['2B']+10*bat['3B']+12*bat['HR']+8*bat['SB']+3*(bat['R']+bat['RBI'])
    pit['xPts'] = 3*pit['IP']+2*pit['SO']-3*pit['ER']-pit['H']-pit['BB']

    names = np.unique(np.concatenate([bat['Player'].values,pit['Player'].values]))
    final = [["Player","Team","xPts"]]

    for x in names:
        try : p_bat = bat.loc[(bat['Player']==x),'Team'].values[0]  
        except IndexError: p_bat = "Free Agent"
        try : p_pit = pit.loc[(pit['Player']==x),'Team'].values[0]
        except IndexError: p_pit = "Free Agent"
        if(p_bat == "Free Agent"): p_team = p_pit
        else : p_team = p_bat

        b = bat.loc[(bat['Player']==x),'xPts'].mean()
        p = pit.loc[(pit['Player']==x),'xPts'].mean()
        if(np.isnan(p)):p=0
        if(np.isnan(b)):b=0
        final.append([x,p_team,b+p])
        
    final = pd.DataFrame(final)
    final.columns = final.iloc[0];final = final.drop(0)
    final = final.fillna(0)

    #with pd.ExcelWriter(output_dump) as writer: 
    #    final.to_excel(writer, sheet_name="xPts", index=False)      
    #    bat.to_excel(writer, sheet_name="Batters", index=False)
    #    pit.to_excel(writer, sheet_name="Pitchers", index=False)
    return (final,bat,pit)

(df_bat,df_st,df_rv) = generate()

df_st['LOB%'] = df_st['LOB%'].str.replace('%', '')
df_st['LOB%'] = df_st['LOB%'].astype(float)/100
df_rv['LOB%'] = df_rv['LOB%'].str.replace('%', '')
df_rv['LOB%'] = df_rv['LOB%'].astype(float)/100

(unique_bat,unique_st,unique_rv)=unique_list(df_bat,df_st,df_rv)

# %%  modify the unique_ files with the players starting and generate xPts
c = 0;
while c < len(home):
    print(home[c],"vs",opps[c])
    (bat_new,pit_new) = calculate(df_bat,df_st,df_rv,home[c],opps[c],unique_bat,unique_st,unique_rv)
    if(c==0):
        bat = bat_new
        pit = pit_new
    else: 
        bat = pd.concat([bat, bat_new])
        pit = pd.concat([pit, pit_new])
    c += 1
(a_projection,bat,pit) = results(bat,pit)
a_projection = a_projection.sort_values(by=['xPts'],ascending=False)
a_projection = a_projection.head(20)
a_projection['Pos'] = 'b'

# %% generate 11 unique combos 
def randomizer(a_projection,home,opps):
    team = [["P","C","3","4","5","6","7","8","9"]]; i=0; j=0
    pitchers = a_projection.loc[a_projection['Pos'] == 'p']
    p = pitchers['xPts'].tolist()
    pitchers = pitchers['Player'].tolist()
    sum_p = sum(p)
    p = [x/sum_p for x in p]   
    catchers = a_projection.loc[a_projection['Pos'] == 'c']
    c = catchers['xPts'].tolist()
    catchers = catchers['Player'].tolist()
    sum_c = sum(c)
    c = [x/sum_c for x in c]
    bats = a_projection.loc[a_projection['Pos'] == 'b']
    b = bats['xPts'].tolist()
    bats = bats['Player'].tolist()
    sum_b = sum(b)
    b = [x/sum_b for x in b]
    
    while i<11:
        h=0; o=0;
        x = np.random.choice(pitchers, 1, p=p, replace=False)
        y = np.random.choice(catchers, 1, p=c, replace=False)
        z = np.random.choice(bats, 7, p=b, replace=False)
        x = x.tolist(); y = y.tolist(); z = z.tolist();
        combo = x + y + z
        while j<9:
            t = a_projection.loc[a_projection['Player'] == combo[j], 'Team'].values[0]
            if(t==home): h+=1
            if(t==opps): o+=1
            j+=1
        if(h>6 or o>6): i=i-1
        else: team.append(combo)
        i +=1; j=0
        
    team = pd.DataFrame(team)
    team.columns = team.iloc[0];team = team.drop(0)
    return team
        
a_combinations = randomizer(a_projection,home[0],opps[0])

# %% live pts for the game in question
def real_time(display,date):
    df_list = pd.read_html(f'https://www.fangraphs.com/liveboxscore.aspx?date={date}&team={display}&dh=0&season=2023#home_standard')
    a = 18
    if(len(df_list[8])<5): a = 20
    bat_home = df_list[a]
    bat_away = df_list[a+2]
    pit_home = df_list[a+1]
    pit_away = df_list[a+3]

    bat_home.drop(bat_home.tail(1).index,inplace=True)
    bat_away.drop(bat_away.tail(1).index,inplace=True)
    pit_home.drop(pit_home.tail(1).index,inplace=True)
    pit_away.drop(pit_away.tail(1).index,inplace=True)
    
    print("current inning",divmod(pit_home['IP'],1)[0].sum())
    pit_home['IP'] = divmod(pit_home['IP'],1)[0] + (10/3)*divmod(pit_home['IP'],1)[1]
    pit_away['IP'] = divmod(pit_away['IP'],1)[0] + (10/3)*divmod(pit_away['IP'],1)[1] 

    bat_home['Pts'] = 4*(bat_home['BB']+bat_home['H']-bat_home['2B']-bat_home['3B']-bat_home['HR'])+6*bat_home['2B']+10*bat_home['3B']+12*bat_home['HR']+8*bat_home['SB']+3*(bat_home['R']+bat_home['RBI'])
    pit_home['Pts'] = 3*pit_home['IP']+2*pit_home['SO']-3*pit_home['ER']-pit_home['H']-pit_home['BB']
    bat_away['Pts'] = 4*(bat_away['BB']+bat_away['H']-bat_away['2B']-bat_away['3B']-bat_away['HR'])+6*bat_away['2B']+10*bat_away['3B']+12*bat_away['HR']+8*bat_away['SB']+3*(bat_away['R']+bat_away['RBI'])
    pit_away['Pts'] = 3*pit_away['IP']+2*pit_away['SO']-3*pit_away['ER']-pit_away['H']-pit_away['BB']
    
    print("score",bat_home['R'].sum(),"-",bat_away['R'].sum())
    bat_home = bat_home[['Name','Pts']]
    bat_away = bat_away[['Name','Pts']]
    pit_home = pit_home[['Name','Pts']]
    pit_away = pit_away[['Name','Pts']]
    final = pd.concat([bat_home,bat_away,pit_home,pit_away], axis=0)
    final = final.sort_values(by=['Pts'],ascending=False)
    return final

a_live = real_time(display,date)
