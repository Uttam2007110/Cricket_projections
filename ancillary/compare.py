# -*- coding: utf-8 -*-
"""
Created on Fri May 12 17:24:35 2023
comparing stats across different leagues
@author: Subramanya.Ganti
"""

import pandas as pd
import numpy as np

file1 = 'C:/Users/Subramanya.Ganti/Downloads/cricket/summary/cc_summary.xlsx'
file2 = 'C:/Users/Subramanya.Ganti/Downloads/cricket/summary/tests_summary.xlsx'
output_dump = "C:/Users/Subramanya.Ganti/Downloads/cricket/outputs/league_comparision.xlsx"
dump = 0

def bowling(file1,file2):
    file1 = pd.read_excel(file1,'bowling seasons')
    file2 = pd.read_excel(file2,'bowling seasons')

    l1 = file1[['bowler','season','RCAA','balls_bowler','runs_off_bat','outs_bowler','xwickets','xruns']].copy()
    l2 = file2[['bowler','season','RCAA','balls_bowler','runs_off_bat','outs_bowler','xwickets','xruns']].copy()
    common = [["player","season","RCAA_l1","balls_l1","runs_l1","wickets_l1","xwickets_l1","xruns_l1","RCAA_l2","balls_l2","runs_l2","wickets_l2","xwickets_l2","xruns_l2"]]

    for x in l1.values:
        for y in l2.values:
            if(x[0]==y[0] and x[1]==y[1]):
                common.append([x[0],x[1],x[2],x[3],x[4],x[5],x[6],x[7],y[2],y[3],y[4],y[5],y[6],y[7]])

    common = pd.DataFrame(common)
    common.columns = common.iloc[0];common = common.drop(0)
    common = common.apply(pd.to_numeric, errors='ignore')    
    return common

def batting(file1,file2):
    file1 = pd.read_excel(file1,'batting seasons')
    file2 = pd.read_excel(file2,'batting seasons')

    l1 = file1[['batsman','season','RSAA','wickets/ball','SR','balls_batsman','xruns']].copy()
    l2 = file2[['batsman','season','RSAA','wickets/ball','SR','balls_batsman','xruns']].copy()
    common = [["player","season","RSAA_l1","wkts/ball_l1","SR_l1","balls_l1","xruns_l1","RSAA_l2","wkts/ball_l2","SR_l2","balls_l2","xruns_l2"]]

    for x in l1.values:
        for y in l2.values:
            if(x[0]==y[0] and x[1]==y[1]):
                common.append([x[0],x[1],x[2],x[3],x[4],x[5],x[6],y[2],y[3],y[4],y[5],y[6]])

    common = pd.DataFrame(common)
    common.columns = common.iloc[0];common = common.drop(0)
    common = common.apply(pd.to_numeric, errors='ignore')    
    return common

common_bat = batting(file1,file2)
common_bowl = bowling(file1,file2)

if(dump == 1):
    with pd.ExcelWriter(output_dump) as writer:        
        common_bat.to_excel(writer, sheet_name="batting", index=False)
        common_bowl.to_excel(writer, sheet_name="bowling", index=False)

runs_l1 = sum(common_bat['SR_l1']*common_bat['balls_l1']/100)
runs_l2 = sum(common_bat['SR_l2']*common_bat['balls_l2']/100)
print("l1 RSAA per 120 balls",120*(runs_l1-sum(common_bat['xruns_l1']))/sum(common_bat['balls_l1']))
print("l2 RSAA per 120 balls",120*(runs_l2-sum(common_bat['xruns_l2']))/sum(common_bat['balls_l2']))

l1_sr = 100*runs_l1/sum(common_bat['balls_l1'])
l1_xsr = 100*sum(common_bat['xruns_l1'])/sum(common_bat['balls_l1'])
l2_sr = 100*runs_l2/sum(common_bat['balls_l2'])
l2_xsr = 100*sum(common_bat['xruns_l2'])/sum(common_bat['balls_l2'])
print("l1 SR",100*runs_l1/sum(common_bat['balls_l1']))
print("l1 xSR",100*sum(common_bat['xruns_l1'])/sum(common_bat['balls_l1']))
print("l2 SR",100*runs_l2/sum(common_bat['balls_l2']))
print("l2 xSR",100*sum(common_bat['xruns_l2'])/sum(common_bat['balls_l2']))
print("common seasons",len(common_bat))
print("factor l2 v l1",(l2_sr/l1_sr)/(l2_xsr/l1_xsr))