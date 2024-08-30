# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 18:54:20 2024

@author: Subramanya.Ganti
"""
import numpy as np
import pandas as pd
from itertools import product

comp = 'blast'
proj_year = 2025
path = 'C:/Users/Subramanya.Ganti/Downloads/cricket'
input_file = f'{path}/summary/{comp}_aggregate.xlsx'

venue_pace_spin = pd.read_excel(input_file,'venue pace_spin')
matchups = list(product(['spin','pace'],venue_pace_spin['venue'].unique()))
matchups = pd.DataFrame(matchups, columns =['bowl_type','venue'])
matchups['season'] = proj_year
#matchups['weight'] = 0
matchups['bias'] = 0.5

spin_la_balls = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='spin','balls'].sum()
spin_la_runs = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='spin','runs'].sum()
spin_la_wickets = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='spin','wickets'].sum()
pace_la_balls = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='pace','balls'].sum()
pace_la_runs = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='pace','runs'].sum()
pace_la_wickets = venue_pace_spin.loc[venue_pace_spin['bowl_type']=='pace','wickets'].sum()

for x in matchups.values:
    #print(x)
    matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'] = 8*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
        5*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
        4*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
        3*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
        2*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum() +\
        venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()
        
    matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'runs'] = 8*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
        5*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
        4*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
        3*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
        2*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum() +\
        venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'runs'].sum()
        
    matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'wickets'] = 8*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
        5*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
        4*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
        3*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
        2*venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum() +\
        venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'wickets'].sum()
    
    #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-1)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 8
    #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-2)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 5
    #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-3)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 4
    #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-4)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 3
    #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-5)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 2
    #if(venue_pace_spin.loc[(venue_pace_spin['season']==proj_year-6)&(venue_pace_spin['venue']==x[1])&(venue_pace_spin['bowl_type']==x[0]),'balls'].sum()>0): matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'weight'] += 1

    matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'] += 20000
    if(x[0] == 'spin'):
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'runs'] += 20000*(spin_la_runs/spin_la_balls)
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'wickets'] += 20000*(spin_la_wickets/spin_la_balls)
    else:
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'runs'] += 20000*(pace_la_runs/pace_la_balls)
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'wickets'] += 20000*(pace_la_wickets/pace_la_balls)
        
matchups['AVG'] = matchups['balls']/matchups['wickets']
matchups['SR'] = 100*matchups['runs']/matchups['balls']

matchups.loc[matchups['bowl_type']=='pace','rf'] = (matchups['runs']/matchups['balls'])/(pace_la_runs/pace_la_balls)
matchups.loc[matchups['bowl_type']=='spin','rf'] = (matchups['runs']/matchups['balls'])/(spin_la_runs/spin_la_balls)
matchups.loc[matchups['bowl_type']=='pace','wf'] = (matchups['wickets']/matchups['balls'])/(pace_la_wickets/pace_la_balls)
matchups.loc[matchups['bowl_type']=='spin','wf'] = (matchups['wickets']/matchups['balls'])/(spin_la_wickets/spin_la_balls)

for x in matchups.values:
    if(x[0] == 'spin'):
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'bias'] = (matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'].sum()-20000+0.0001)/(matchups.loc[(matchups['venue']==x[1]),'balls'].sum()-40000+0.0002)
    else:
        matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'bias'] = (matchups.loc[(matchups['bowl_type']==x[0])&(matchups['venue']==x[1]),'balls'].sum()-20000+0.0001)/(matchups.loc[(matchups['venue']==x[1]),'balls'].sum()-40000+0.0002)

matchups = matchups[['venue','season','rf','wf','bowl_type','bias']]

m2 = pd.DataFrame(columns = matchups.columns)
m2['venue'] = matchups['venue'].unique()
m2['season'] = proj_year
m2['bowl_type'] = 'all'
m2['bias'] = 1

for x in m2.values:
    #print(x)
    m2.loc[m2['venue']==x[0],'rf'] = (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'rf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'bias'].sum()) +\
                                     (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'rf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'bias'].sum())
                                     
    m2.loc[m2['venue']==x[0],'wf'] = (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'wf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='spin'),'bias'].sum()) +\
                                     (matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'wf'].sum()*matchups.loc[(matchups['venue']==x[0])&(matchups['bowl_type']=='pace'),'bias'].sum())

final = pd.concat([matchups, m2], axis=0)
final = final.apply(pd.to_numeric, errors='ignore')
final = final.sort_values('venue')
final = final.rename(columns={'rf': 'runs', 'wf': 'wkts'})
