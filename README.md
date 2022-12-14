# Cricket_projections
Generating projections for cricket leagues

The input files are .csv files from cricsheet. Choose the all_matches file for the league you want to generate projections for as the input_file in generate.py

There are 2 types of projection models being employed, a simple Marcel the monkey style forecast and another approach where we look a players similar peers and generate a projection based on how their comps have done. This comparison is done based on finding the mahalanobis distance (referred to as MDist in the output excel file) of the player in question to every player in the dataset and assigning weights to every comp (Approach borrowed from the Zips projection system for baseball). League wins are estimated using a pythagorean formula for runs scored and conceded.

generate.py - 
Used to generate season summary and player history by year for the league in question.

projections.py - 
takes the output from generate.py to dump projections based on past player stats.
input_file should be the same as the output_file of generate.py
proj_year is the year for which the projections have to be dumped.
output_file is the file with the projected player stats and projected league tables. 
dumps_file is the list of a particular players closest comps.

usage.py - 
methods in this file are called automatically from projections.py. Batting and bowling projections are scaled to ensure the aggregate sum matches in this method.

Outputs-
MDist table - League table based on mahlanobis distance based projections
MDist bowl - mahlanobis distance based bowler projections
MDist bat - mahlanobis distance based batter projections
Marcel table - League table based on Marcel the monkey style projections
Marcel bowl - Marcel the monkey style bowler projections
Marcel bat - Marcel the monkey style batter projections

Glossary-
usage = no of balls faced/bowled by a player divided by the no of balls faced/bowled by the players team
RSAA = runs scored above average per game (a +5 RSAA means a player scored 5 runs more than the average batter facing the same deliveries)
OAA = outs above average per game
RCAA = runs conceded above average per game
WTAA = wickets taken above average per game
pp - Poweplay (ov 1-6)
mid - middle overs (ov 7-12)
setup - setup overs (ov 13-16)
death - death overs (ov 17-20)
