# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 01:55:40 2023
NBA projections courtesy numberFire
@author: GF63
"""
# %%  specify the teams playing
import pandas as pd
import numpy as np

date = '6/12/23'   #month/day/year
squads = ["Miami-Heat","Denver-Nuggets"]

file = "C:/Users/GF63/Desktop/cricket/NBA prices.xlsx"
teams = ["Milwaukee-Bucks","Boston-Celtics","Philadelphia-76ers","Cleveland-Cavaliers","New-York-Knicks",
"Brooklyn-Nets","Miami-Heat","Atlanta-Hawks","Toronto-Raptors","Chicago-Bulls","Indiana-Pacers",
"Washington-Wizards","Orlando-Magic","Charlotte-Hornets","Detroit-Pistons","Denver-Nuggets",
"Memphis-Grizzlies","Sacramento-Kings","Phoenix-Suns","Los-Angeles-Clippers","Golden-State-Warriors",
"Los-Angeles-Lakers","Minnesota-Timberwolves","New-Orleans-Pelicans","Oklahoma-City-Thunder",
"Dallas-Mavericks","Utah-Jazz","Portland-Trail-Blazers","Houston-Rockets","San-Antonio-Spurs"]

# %%  extract all the avaliable players
def extract_players(teams):
    i = 0; j = 0; player = [["Name","Team"]]
    while i<len(teams):
        lol = teams[i]
        table = pd.read_html(f'https://www.numberfire.com/nba/teams/stats/{lol}')
        list_player = table[0]
        while j<len(list_player):
            string = list_player.values[j][0]
            size = len(string)
            #print(string,"5th from the end",string[-5])
            if(string[-5] == ' '): string = string[:size-5]
            else: string = string[:size-4]
            #print(string)
            string = string.replace(" ", "-")
            string = string.replace("J.", "J")  #for PJ Tucker
            string = string.replace("'", "-")
            string = string.replace("Jr.", "Jr")
            string = string.replace(".", "-")
            string = string.replace("Ish-Smith", "Ishmael-Smith")   #feed his ass to the white whale
            string = string.replace("Patrick-Baldwin", "Patrick-Baldwin-Jr")
            string = string.replace("Dennis-Smith-Jr","Dennis-Smith-Jr.")
            string = string.replace("Desmond-Bane","Desmond-Bane-1")
            string = string.replace("Troy-Brown-Jr","Troy-Brown")
            string = string.replace("Willy-Hernangomez","Guillermo-Hernangomez")
            string = string.replace("Devonte--Graham","Devonte-Graham")
            player.append([string,lol])
            j = j + 1
        j = 0
        print(teams[i],i+1)
        i = i + 1
    player = pd.DataFrame(player)
    player = pd.DataFrame(player)
    player.columns = player.iloc[0];player = player.drop(0)
    print("All players data collected")
    return player

player = extract_players(teams)

# %%  calculate projections
def xPts(player):
    i = 0; initial = 0;
    while i<len(player):
        name = player.loc[i+1][0]
        p_team = player.loc[i+1][1]
        if p_team in squads:
            try:
                table2 = pd.read_html(f'https://www.numberfire.com/nba/players/projections/{name}')
                if(len(table2) == 3): n = 0
                else: n = 1
                log = table2[n]
                val = log.index[log['Date'] == date].tolist()
                if(len(val) == 0): val = -1
                else: val = val[0]
                proj = table2[n+1]
                if(val>-1):
                    print(name)
                    p = proj.loc[[val]]
                    p['Name'] = name
                    p['Team'] = p_team
                    if(initial == 0): projections = p; initial = 1
                    else: projections = pd.concat([projections,p])
            except ValueError: print(name,"skipped as URL is wrong")
        i = i + 1
    projections = projections.drop(['Salary','Value','FGM-A','FTM-A','3PM-A'],axis=1)
    first_column = projections.pop('Name')
    projections.insert(0, 'Name', first_column)
    second_column = projections.pop('Team')
    projections.insert(1, 'Team', second_column)
    #projections['Name'] = projections['Name'].str.replace("-", " ")
    #projections['Team'] = projections['Team'].str.replace("-", " ")
    projections['FP'] = projections['PTS']+1.2*projections['REB']+1.5*projections['AST']+3*(projections['STL']+projections['BLK'])-projections['TOV']
    projections = projections[projections['FP'] != 0]
    projections = projections.sort_values(by=['FP'],ascending=False)
    return projections

f_points = xPts(player)
data = pd.read_excel(file,'Sheet1')
data = data.fillna(100)
f_points = f_points.merge(data, on='Name', how='left')
f_points = f_points.fillna(100)
f_points = f_points.drop(['Squad'],axis=1)

# %%  generate 11 unique lineup combinations
def randomizer(f_points,home,opps):
    team = [["C","PF","SF","SG","PG","6","7","8"]]; i=0; j=0; diffs=[]
    centers = f_points.loc[f_points['Pos'] == 5]
    c = pow(centers['FP'],3).tolist()
    centers = centers['Name'].tolist()
    sum_c = sum(c)
    c = [x/sum_c for x in c]
    power = f_points.loc[f_points['Pos'] == 4]
    pf = pow(power['FP'],3).tolist()
    power = power['Name'].tolist()
    sum_pf = sum(pf)
    pf = [x/sum_pf for x in pf]
    small = f_points.loc[f_points['Pos'] == 3]
    sf = pow(small['FP'],3).tolist()
    small = small['Name'].tolist()
    sum_sf = sum(sf)
    sf = [x/sum_sf for x in sf]
    shooting = f_points.loc[f_points['Pos'] == 2]
    sg = pow(shooting['FP'],3).tolist()
    shooting = shooting['Name'].tolist()
    sum_sg = sum(sg)
    sg = [x/sum_sg for x in sg]
    point = f_points.loc[f_points['Pos'] == 1]
    pg = pow(point['FP'],3).tolist()
    point = point['Name'].tolist()
    sum_pg = sum(pg)
    pg = [x/sum_pg for x in pg]
    
    while i<11:
        h=0; o=0; cost=0
        p1 = np.random.choice(centers, 1, p=c, replace=False)
        p2 = np.random.choice(power, 1, p=pf, replace=False)
        p3 = np.random.choice(small, 1, p=sf, replace=False)
        p4 = np.random.choice(shooting, 1, p=sg, replace=False)
        p5 = np.random.choice(point, 1, p=pg, replace=False)
        p1 = p1.tolist(); p2 = p2.tolist();p3 = p3.tolist();p4 = p4.tolist(); p5 = p5.tolist();
        combo = p1+p2+p3+p4+p5
        rest = f_points[~f_points.Name.isin(combo)]
        r = pow(rest['FP'],3).tolist()
        rest = rest['Name'].tolist()
        sum_r = sum(r)
        r = [x/sum_r for x in r]
        p678 = np.random.choice(rest,3, p=r, replace=False)
        p678 = p678.tolist()
        combo = combo+p678
        #print(combo)
        while j<8:
            t = f_points.loc[f_points['Name'] == combo[j], 'Team'].values[0]
            cost += f_points.loc[f_points['Name'] == combo[j], 'Cost'].values[0]
            if(t==home): h+=1
            if(t==opps): o+=1
            j+=1
        if(h>5 or o>5 or cost>100): i=i-1
        else: team.append(combo); print("valid combo",i+1,"found"); print(combo)
        i +=1; j=0
        
    team = pd.DataFrame(team)
    team.columns = team.iloc[0];team = team.drop(0)
    team = team.T
    return team
    
a_team = randomizer(f_points,squads[0],squads[1])
