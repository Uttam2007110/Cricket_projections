# -*- coding: utf-8 -*-
"""
Created on Thu Jul  6 14:53:48 2023

@author: Subramanya.Ganti
"""
import numpy as np
import pandas as pd
import random

#keep the groupings as 5-6-6-5
team_names = ['Hampshire','Worcestershire']
a = ["","","","",""]
b = ["","","","","",""]
c = ["","","","","",""]
d = ["","","","",""]
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'

def names_game(team_names):
    names = pd.read_excel(f"{path}/game.xlsx",'Points')
    names = names.sort_values(['total'], ascending=[False])
    names = names.loc[names['team'].isin(team_names)]
    names = names['player'].tolist()
    a = names[0:5]
    b = names[5:11]
    c = names[11:17]
    d = names[17:22]
    return (a,b,c,d)

def shuffle_cricket(a,b,c,d):
    team = [["C","VC","3","4","5","6","7","8","9","10","11"]]
    i = 0
    ra = [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]
    rb = [6,6,5,5,4,4,4,4,3,3,3,3,3,2,2,2,2,1,1,1]
    rc = [0,0,1,0,2,1,1,0,3,2,2,1,0,4,3,2,1,4,3,2]
    rd = [0,0,0,1,0,1,1,2,0,1,1,2,3,0,1,2,3,1,2,3]

    while i<20:
        random.shuffle(a)
        random.shuffle(b)
        random.shuffle(c)
        random.shuffle(d)
        team.append(a[:ra[i]]+b[:rb[i]]+c[:rc[i]]+d[:rd[i]])
        i +=1

    team = pd.DataFrame(team)
    team.columns = team.iloc[0];team = team.drop(0)    
    return team

(a,b,c,d) = names_game(team_names)
team = shuffle_cricket(a,b,c,d)