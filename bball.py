# -*- coding: utf-8 -*-
"""
Created on Wed Jun 21 18:19:46 2023

@author: Subramanya.Ganti
"""
# %%  specify the teams playing
import pandas as pd
import numpy as np

date = '6/13/23'   #month/day/year
squads = ["Denver-Nuggets","Miami-Heat"]

teams = ["Milwaukee-Bucks","Boston-Celtics","Philadelphia-76ers","Cleveland-Cavaliers","New-York-Knicks",
"Brooklyn-Nets","Miami-Heat","Atlanta-Hawks","Toronto-Raptors","Chicago-Bulls","Indiana-Pacers",
"Washington-Wizards","Orlando-Magic","Charlotte-Hornets","Detroit-Pistons","Denver-Nuggets","Memphis-Grizzlies",
"Sacramento-Kings","Phoenix-Suns","Los-Angeles-Clippers","Golden-State-Warriors",
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
            player.append([string,lol])
            j = j + 1
        j = 0
        print(teams[i],"done")
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
            print(name)
            table2 = pd.read_html(f'https://www.numberfire.com/nba/players/projections/{name}')
            if(len(table2) == 3): n = 0
            else: n = 1
            log = table2[n]
            val = log.index[log['Date'] == date].tolist()
            if(len(val) == 0): val = -1
            else: val = val[0]
            proj = table2[n+1]
            if(val>-1):
                p = proj.loc[[val]]
                p['Name'] = name
                p['Team'] = p_team
                if(initial == 0): projections = p; initial = 1
                else: projections = pd.concat([projections,p])
        i = i + 1
    projections = projections.drop(['Salary','Value','FGM-A','FTM-A','3PM-A'],axis=1)
    first_column = projections.pop('Name')
    projections.insert(0, 'Name', first_column)
    second_column = projections.pop('Team')
    projections.insert(1, 'Team', second_column)
    projections['Name'] = projections['Name'].str.replace("-", " ")
    projections['Team'] = projections['Team'].str.replace("-", " ")
    projections['FP'] = projections['PTS']+1.2*projections['REB']+1.5*projections['AST']+3*(projections['STL']+projections['BLK'])-projections['TOV']
    return projections

projections = xPts(player)
 
