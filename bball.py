# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 01:55:40 2023
NBA projections courtesy numberFire
@author: GF63
"""
# %%  specify the teams playing
import pandas as pd
import numpy as np
from itertools import chain
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable, GLPK
pd.options.mode.chained_assignment = None  # default='warn'

date = '11/24/23'     #month/day/year
#squads = ['Boston-Celtics','Orlando-Magic']
squads = ['Phoenix-Suns','Memphis-Grizzlies']
#squads = ['New-York-Knicks','Miami-Heat']
#squads = ['Milwaukee-Bucks','Washington-Wizards']
#squads = ['Golden-State-Warriors','San-Antonio-Spurs']
#squads = ['Los-Angeles-Clippers','New-Orleans-Pelicans']
#squads = ['','']

# 0-picks up players from the team pages, 1-from ROS projections page, 2-from the NBA prices.xlsx
player_list = 2; n = 11
file = "C:/Users/GF63/Desktop/cricket/NBA prices.xlsx"
#file = "C:/Users/Subramanya.Ganti/Downloads/cricket/NBA prices.xlsx"

teams = ['Atlanta-Hawks', 'Boston-Celtics', 'Brooklyn-Nets', 'Charlotte-Hornets',
 'Chicago-Bulls', 'Cleveland-Cavaliers', 'Dallas-Mavericks', 'Denver-Nuggets',
 'Detroit-Pistons', 'Golden-State-Warriors', 'Houston-Rockets', 'Indiana-Pacers',
 'Los-Angeles-Clippers', 'Los-Angeles-Lakers', 'Memphis-Grizzlies', 'Miami-Heat',
 'Milwaukee-Bucks', 'Minnesota-Timberwolves', 'New-Orleans-Pelicans', 'New-York-Knicks',
 'Oklahoma-City-Thunder', 'Orlando-Magic', 'Philadelphia-76ers', 'Phoenix-Suns',
 'Portland-Trail-Blazers', 'Sacramento-Kings', 'San-Antonio-Spurs', 'Toronto-Raptors',
 'Utah-Jazz', 'Washington-Wizards']

#f_points['FP'] = f_points['FP/MIN']*f_points['MIN']

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
            string = string.replace("Dennis-Smith","Dennis-Smith-Jr.")
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

def extract_players_v2():
    centers = pd.read_html('https://www.numberfire.com/nba/fantasy/remaining-projections/centers?scope=total')
    centers = centers[0]
    forwards = pd.read_html('https://www.numberfire.com/nba/fantasy/remaining-projections/forwards?scope=total')
    forwards = forwards[0]
    guards = pd.read_html('https://www.numberfire.com/nba/fantasy/remaining-projections/guards?scope=total')
    guards = guards[0]
    
    for x in centers['Player'].values:
        words = x.split()
        secondwords = iter(words)
        next(secondwords)
        split = [' '.join((first, second)) for first, second in zip(words, secondwords)]
        #print(split[0],split[len(split)-1])
        centers.loc[centers['Player']==x,'Player'] = split[0]
        centers.loc[centers['Player']==split[0],'Team'] = split[len(split)-1][-4:]
        
    for x in forwards['Player'].values:
        words = x.split()
        secondwords = iter(words)
        next(secondwords)
        split = [' '.join((first, second)) for first, second in zip(words, secondwords)]
        #print(split[0],split[len(split)-1])
        forwards.loc[forwards['Player']==x,'Player'] = split[0]
        forwards.loc[forwards['Player']==split[0],'Team'] = split[len(split)-1][-4:]
        
    for x in guards['Player'].values:
        words = x.split()
        secondwords = iter(words)
        next(secondwords)
        split = [' '.join((first, second)) for first, second in zip(words, secondwords)]
        #print(split[0],split[len(split)-1])
        guards.loc[guards['Player']==x,'Player'] = split[0]
        guards.loc[guards['Player']==split[0],'Team'] = split[len(split)-1][-4:]
    
    
    names = [centers, forwards, guards]
    names = pd.concat(names)
    names = names.drop_duplicates()
    names.rename(columns = {'Player':'Name'}, inplace = True)
    
    names['Team'] = names['Team'].replace('ATL)', 'Atlanta-Hawks')
    names['Team'] = names['Team'].replace('BOS)', 'Boston-Celtics')
    names['Team'] = names['Team'].replace('BKN)', 'Brooklyn-Nets')
    names['Team'] = names['Team'].replace('CHA)', 'Charlotte-Hornets')
    names['Team'] = names['Team'].replace('CHI)', 'Chicago-Bulls')
    names['Team'] = names['Team'].replace('CLE)', 'Cleveland-Cavaliers')
    names['Team'] = names['Team'].replace('DAL)', 'Dallas-Mavericks')
    names['Team'] = names['Team'].replace('DEN)', 'Denver-Nuggets')
    names['Team'] = names['Team'].replace('DET)', 'Detroit-Pistons')
    names['Team'] = names['Team'].replace(' GS)', 'Golden-State-Warriors')
    names['Team'] = names['Team'].replace('HOU)', 'Houston-Rockets')
    names['Team'] = names['Team'].replace('IND)', 'Indiana-Pacers')
    names['Team'] = names['Team'].replace('LAC)', 'Los-Angeles-Clippers')
    names['Team'] = names['Team'].replace('LAL)', 'Los-Angeles-Lakers')
    names['Team'] = names['Team'].replace('MEM)', 'Memphis-Grizzlies')
    names['Team'] = names['Team'].replace('MIA)', 'Miami-Heat')
    names['Team'] = names['Team'].replace('MIL)', 'Milwaukee-Bucks')
    names['Team'] = names['Team'].replace('MIN)', 'Minnesota-Timberwolves')
    names['Team'] = names['Team'].replace(' NO)', 'New-Orleans-Pelicans')
    names['Team'] = names['Team'].replace(' NY)', 'New-York-Knicks')
    names['Team'] = names['Team'].replace('OKC)', 'Oklahoma-City-Thunder')
    names['Team'] = names['Team'].replace('ORL)', 'Orlando-Magic')
    names['Team'] = names['Team'].replace('PHI)', 'Philadelphia-76ers')
    names['Team'] = names['Team'].replace('PHX)', 'Phoenix-Suns')
    names['Team'] = names['Team'].replace('POR)', 'Portland-Trail-Blazers')
    names['Team'] = names['Team'].replace('SAC)', 'Sacramento-Kings')
    names['Team'] = names['Team'].replace(' SA)', 'San-Antonio-Spurs')
    names['Team'] = names['Team'].replace('TOR)', 'Toronto-Raptors')
    names['Team'] = names['Team'].replace('TAH)', 'Utah-Jazz')
    names['Team'] = names['Team'].replace('WSH)', 'Washington-Wizards')
    
    names = names.applymap(lambda x: str(x.replace(' ','-')))
    names = names.applymap(lambda x: str(x.replace("J.", "J")))  #for PJ Tucker
    names = names.applymap(lambda x: str(x.replace("'", "-")))
    names = names.applymap(lambda x: str(x.replace("Jr.", "Jr")))
    names = names.applymap(lambda x: str(x.replace(".", "-")))
    names = names.applymap(lambda x: str(x.replace("Ish-Smith", "Ishmael-Smith")))   #feed his ass to the white whale
    names = names.applymap(lambda x: str(x.replace("Patrick-Baldwin", "Patrick-Baldwin-Jr")))
    names = names.applymap(lambda x: str(x.replace("Dennis-Smith","Dennis-Smith-Jr.")))
    names = names.applymap(lambda x: str(x.replace("Dennis-Smith-Jr","Dennis-Smith-Jr.")))
    names = names.applymap(lambda x: str(x.replace("Desmond-Bane","Desmond-Bane-1")))
    names = names.applymap(lambda x: str(x.replace("Troy-Brown-Jr","Troy-Brown")))
    names = names.applymap(lambda x: str(x.replace("Willy-Hernangomez","Guillermo-Hernangomez")))
    names = names.applymap(lambda x: str(x.replace("Devonte--Graham","Devonte-Graham")))
    names = names.applymap(lambda x: str(x.replace("Michael-Porter", "Michael-Porter-Jr")))
    names = names.applymap(lambda x: str(x.replace("Gary-Payton", "Gary-Payton-II")))
    names = names.applymap(lambda x: str(x.replace("Danuel-House", "Danuel-House-Jr")))    
    names = names.applymap(lambda x: str(x.replace("Nick-Smith","Nick-Smith-Jr")))
    names = names.applymap(lambda x: str(x.replace("Bruce-Brown","Bruce-Brown-Jr")))
    names = names.applymap(lambda x: str(x.replace("Wendell-Carter","Wendell-Carter-Jr")))
    names = names.applymap(lambda x: str(x.replace("Wendell-Moore","Wendell-Moore-Jr")))
    names = names.applymap(lambda x: str(x.replace("Gary-Trent","Gary-Trent-Jr")))
    names = names.applymap(lambda x: str(x.replace("Marvin-Bagley", "Marvin-Bagley-III")))
    names = names.applymap(lambda x: str(x.replace("Trey-Murphy", "Trey-Murphy-III")))
    names = names.applymap(lambda x: str(x.replace("Jaime-Jaquez","Jaime-Jaquez-Jr")))
    names = names.applymap(lambda x: str(x.replace("Kira-Lewis","Kira-Lewis-Jr")))
    names = names.applymap(lambda x: str(x.replace("Vince-Williams","Vince-Williams-Jr")))
    names = names.applymap(lambda x: str(x.replace("Kenneth-Lofton","Kenneth-Lofton-Jr")))
    names = names.applymap(lambda x: str(x.replace("Larry-Nance","Larry-Nance-Jr")))
    names = names.applymap(lambda x: str(x.replace("Jaren-Jackson","Jaren-Jackson-Jr")))
    names = names.applymap(lambda x: str(x.replace("Derrick-Jones","Derrick-Jones-Jr")))
    names = names.applymap(lambda x: str(x.replace("John-Butler","John-Butler-Jr")))
    names = names.applymap(lambda x: str(x.replace("Brandon-Boston","Brandon-Boston-Jr")))
    names = names.applymap(lambda x: str(x.replace("Andre-Jackson","Andre-Jackson-Jr")))

    print("All players data collected")
    names.reset_index(drop=True, inplace=True)
    return names

if(player_list == 1): 
    player = extract_players_v2()
elif(player_list == 0): 
    player = extract_players(teams)
else: 
    try: 
        player = pd.read_excel(file,'Sheet1')
        player.rename(columns = {'Squad':'Team'}, inplace = True)
        player.drop(['Pos','Cost'], axis=1, inplace=True)
    except FileNotFoundError:
        print("file with player names and prices not found")

# %%  calculate projections
def xPts(player):
    i = 0; initial = 0;
    while i<len(player)-1:
        name = player.loc[i][0]       #review the +1 logic for loc
        p_team = player.loc[i][1]
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
    projections['FP'] = projections['PTS']+1.2*projections['REB']+1.5*projections['AST']+3*(projections['STL']+projections['BLK'])-projections['TOV']
    projections = projections[projections['PTS'] > 0]
    projections = projections.sort_values(by=['FP'],ascending=False)
    return projections

f_points = xPts(player)
f_points.reset_index(drop=True, inplace=True)
f_points['FP/MIN'] = f_points['FP']/f_points['MIN']
try:
    data = pd.read_excel(file,'Sheet1')
    data = data.fillna(100)
    f_points = f_points.merge(data, on='Name', how='left')
    f_points = f_points.fillna(100)
    f_points = f_points.drop(['Squad'],axis=1)
except FileNotFoundError:
    f_points['Pos'] = 1
    f_points['Cost'] = 0.5

# %%  generate n unique lineup combinations (legacy)
def randomizer(f_points_og,f_points,home,opps,n):
    team = [["PG","SG","SF","PF","C","6","7","8","Star","Pro","xPts",'xMins','Cost']]; i=0; j=0; it=0   
    while (i<n and it<30000):
        #random noise introduced in mins/efficiency
        f_points['RV'] = np.random.normal(f_points_og['FP/MIN'],f_points_og['FP/MIN']/7)
        f_points['FP'] = f_points['RV']*f_points['MIN']
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
        
        h=0; o=0; cost=0; xmins=0; pts=0; actual=0; min_c=400
        if(it >= 500):min_c=370
        if(it >= 1500):min_c=340
        if(it >= 5000):min_c=315
        if(it >= 10000):min_c=300
        if(it >= 15000):min_c=0
        p1 = np.random.choice(centers, 1, p=c, replace=False)
        p2 = np.random.choice(power, 1, p=pf, replace=False)
        p3 = np.random.choice(small, 1, p=sf, replace=False)
        p4 = np.random.choice(shooting, 1, p=sg, replace=False)
        p5 = np.random.choice(point, 1, p=pg, replace=False)
        p1 = p1.tolist(); p2 = p2.tolist();p3 = p3.tolist();p4 = p4.tolist(); p5 = p5.tolist();
        combo = p5+p4+p3+p2+p1
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
            xmins += f_points.loc[f_points['Name'] == combo[j], 'MIN'].values[0]
            actual += f_points_og.loc[f_points_og['Name'] == combo[j], 'FP'].values[0]
            if(t==home): h+=1
            if(t==opps): o+=1
            cap = f_points[f_points.Name.isin(combo)]
            pts = sum(cap['FP'])
            p2 = pow(cap['FP'],6).tolist()
            cap = cap['Name'].tolist()
            sum_p2 = sum(p2)
            p2 = [x/sum_p2 for x in p2]
            y = np.random.choice(cap, 2, p=p2, replace=False)
            pts += f_points.loc[(f_points['Name']==y[0]),'FP'].sum() + (f_points.loc[(f_points['Name']==y[1]),'FP'].sum()/2)           
            y = y.tolist()
            j+=1
        xmins = round(xmins,2)
        if(h>5 or o>5 or cost>100 or cost<95 or pts<min_c or (xmins in chain(*team))): i=i-1
        else:
            actual += f_points_og.loc[(f_points_og['Name']==y[0]),'FP'].sum() + (f_points_og.loc[(f_points_og['Name']==y[1]),'FP'].sum()/2)
            #print(f_points_og.loc[(f_points_og['Name']==y[0]),'FP'].sum(),f_points_og.loc[(f_points_og['Name']==y[1]),'FP'].sum())
            team.append(combo); print("valid combo",i+1,"iteration",it+1)            
            combo += y + [actual] + [xmins] + [cost]
            
        i +=1; j=0; it+=1
        
    team = pd.DataFrame(team)
    team.columns = team.iloc[0];team = team.drop(0)
    team = team.apply(pd.to_numeric, errors='ignore')
    #team = team.T
    return team

f_points['Name'] = f_points['Name'].str.replace("-", " ")
f_points['Team'] = f_points['Team'].str.replace("-", " ")    
#a_team = randomizer(f_points,f_points.copy(),squads[0].replace('-',' '),squads[1].replace('-',' '),n)

# %%  PuLP solver
print()
for t in squads:
    print(round(f_points.loc[f_points['Team']==t.replace('-',' '),'PTS'].sum(),1),t.replace('-',' '),"(",round(f_points.loc[f_points['Team']==t.replace('-',' '),'MIN'].sum(),1),")")
print()

def solver(f_points):
    duplicate = f_points.copy()
    dummy_team = duplicate['Team'][0]
    duplicate['dummy_team'] = np.where(duplicate['Team']==dummy_team,1,0)
    duplicate['PG'] = np.where(duplicate['Pos']==1,1,0)
    duplicate['SG'] = np.where(duplicate['Pos']==2,1,0)
    duplicate['SF'] = np.where(duplicate['Pos']==3,1,0)
    duplicate['PFs'] = np.where(duplicate['Pos']==4,1,0)
    duplicate['C'] = np.where(duplicate['Pos']==5,1,0)
    duplicate['Sel'] = 0
    model = LpProblem(name="resource-allocation", sense=LpMaximize)
    
    # Define the decision variables
    x = {i: LpVariable(name=f"x{i}", cat="Binary") for i in range (0, len(duplicate))}
    c = {i: LpVariable(name=f"c{i}", cat="Binary") for i in range (0, len(duplicate))}
    vc = {i: LpVariable(name=f"vc{i}", cat="Binary") for i in range (0, len(duplicate))}
    
    # Add constraints
    model += (lpSum(x.values()) == 8, "total players in team")
    model += (lpSum(c.values()) == 1, "captain")
    model += (lpSum(vc.values()) == 1, "vice captain")
    model += (lpSum( x[k] * duplicate['Cost'][k] for k in range (0, len(duplicate))) <= 100, "cost")
    model += (lpSum( x[k] * duplicate['PG'][k] for k in range (0, len(duplicate))) >= 1, "PG")
    model += (lpSum( x[k] * duplicate['SG'][k] for k in range (0, len(duplicate))) >= 1, "SG")
    model += (lpSum( x[k] * duplicate['SF'][k] for k in range (0, len(duplicate))) >= 1, "SF")
    model += (lpSum( x[k] * duplicate['PFs'][k] for k in range (0, len(duplicate))) >= 1, "PF")
    model += (lpSum( x[k] * duplicate['C'][k] for k in range (0, len(duplicate))) >= 1, "C")
    model += (lpSum( x[k] * duplicate['dummy_team'][k] for k in range (0, len(duplicate))) >= 3, "Team min")
    model += (lpSum( x[k] * duplicate['dummy_team'][k] for k in range (0, len(duplicate))) <= 5, "Team max")
    
    for k in range (0, len(duplicate)): model += (x[k]-c[k]-vc[k] >= 0,f"unique C-VC {k}")
    
    # Set objective
    model += lpSum( (x[k]+c[k]+0.5*vc[k]) * duplicate['FP'][k] for k in range (0, len(duplicate)))
    
    # Solve the optimization problem
    status = model.solve(solver=GLPK(msg=False))    
    #print(f"{LpStatus[model.status]}, xPts {model.objective.value()}")
    xpts = model.objective.value()
    
    #for var in model.variables(): print(var.name,var.value())
    for name, constraint in model.constraints.items():
        if(name == 'cost'): cost = 100+constraint.value()
        #print(f"{name}: {constraint.value()}")   
    for k in range (0, len(duplicate)): duplicate['Sel'][k] = x[k].value() + c[k].value() + 0.5*vc[k].value()
    
    return duplicate,xpts,cost

def iterator(f_points,n):
    a_team = [["1","2","3","4","5","6","7","8","Star","Pro","xPts",'xMins','Cost']];
    k=1
    while(k<n+1):      
        #random noise introduced in mins/efficiency
        f_points_copy = f_points.copy()
        if(k>1):
            f_points_copy['RV'] = np.random.normal(f_points['FP/MIN'],f_points['FP/MIN']/6)
            f_points_copy['FP'] = f_points_copy['RV']*f_points_copy['MIN']       
        solution,xPts,cost = solver(f_points_copy)
        solution = solution.sort_values(by=['Pos'],ascending=True)
        names = solution.loc[solution['Sel'] >= 1, 'Name']
        names = names.to_list()
        
        xPts=0; xmins=0
        for j in names:
            xmins += f_points.loc[f_points['Name'] == j, 'MIN'].values[0]
            xPts += f_points.loc[f_points['Name'] == j, 'FP'].values[0]
        cap = solution.loc[solution['Sel'] == 2, 'Name']
        cap = cap.to_list()
        vice = solution.loc[solution['Sel'] == 1.5, 'Name']
        vice = vice.to_list()
        xPts += f_points.loc[f_points['Name'] == cap[0], 'FP'].values[0] + (f_points.loc[f_points['Name'] == vice[0], 'FP'].values[0])/2
        xmins = round(xmins,2)
        names = names + cap + vice + [xPts] + [xmins] + [cost]
        if(xmins in chain(*a_team)):
            k = k - 1
        else:
            a_team.append(names)
            print(f"solution {k} found")
        k = k + 1
    return a_team

a_team = iterator(f_points,n)
a_team = pd.DataFrame(a_team)
a_team.columns = a_team.iloc[0];a_team = a_team.drop(0)
a_team = a_team.apply(pd.to_numeric, errors='ignore')
