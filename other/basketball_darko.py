# -*- coding: utf-8 -*-
"""
Created on Wed Dec 4 21:59:23 2024
NBA projections courtesy DARKO
@author: GF63
"""
# %%  specify the teams playing
import pandas as pd
import numpy as np
from itertools import chain
from pulp import LpMaximize, LpProblem, lpSum, LpVariable, GLPK
from sklearn.cluster import KMeans
from scipy.stats import truncnorm
from scipy.stats import zscore
from scipy.stats import multivariate_normal
pd.options.mode.chained_assignment = None  # default='warn'

teams = ['Miami Heat','Toronto Raptors']
#teams = ['Boston Celtics','Detroit Pistons']
n = 11
file = "C:/Users/GF63/Desktop/cricket/NBA prices.xlsx"

correlation = pd.read_excel('C:/Users/GF63/Desktop/cricket/barttorvik/nba_roles.xlsx','correlation matrix')
correlation.set_index('role', inplace=True)

# %%  initialize functions
def projected_minutes(teams):
    DARKO = pd.read_html('https://spreadsheets.google.com/tq?tqx=out:html&tq=&key=1mhwOLqPu2F9026EQiVxFPIN1t9RGafGpl-dokaIsm9c&gid=284274620')[0]
    DARKO = header_first_row(DARKO)
    
    box_talent = DARKO.copy()
    box_talent.loc[box_talent['x_position']=='c_pos','position'] = 'big'
    box_talent.loc[(box_talent['x_position']=='pf_pos')|(box_talent['x_position']=='sf_pos'),'position'] = 'wing'
    box_talent.loc[(box_talent['x_position']=='sg_pos')|(box_talent['x_position']=='pg_pos'),'position'] = 'guard'

    box_talent['pts_100'] = box_talent['pts_100'].str.replace(r'%', '', regex=True)
    box_talent['pts_100'] = (pd.to_numeric(box_talent['pts_100'])/100)
    box_talent['orb_100'] = box_talent['orb_100'].str.replace(r'%', '', regex=True)
    box_talent['orb_100'] = (pd.to_numeric(box_talent['orb_100'])/100)
    box_talent['drb_100'] = box_talent['drb_100'].str.replace(r'%', '', regex=True)
    box_talent['drb_100'] = (pd.to_numeric(box_talent['drb_100'])/100)

    pivot = pd.pivot_table(box_talent,values=['drb_100','ast_100','stl_100','rim_fga_100','fg3a_100'],columns='position',aggfunc=np.mean)
    pivot = pivot.T

    dataset = box_talent[['nba_id','player_name','team_name','position','x_position','minutes','ast_100', 'drb_100', 'fg3a_100', 'rim_fga_100', 'stl_100']]

    dataset['big'] = np.exp(-np.sqrt(((dataset[['ast_100', 'drb_100', 'fg3a_100', 'rim_fga_100', 'stl_100']] - pivot.loc['big']).apply(lambda num: num**2)).sum(axis=1)))
    dataset['wing'] = np.exp(-np.sqrt(((dataset[['ast_100', 'drb_100', 'fg3a_100', 'rim_fga_100', 'stl_100']] - pivot.loc['wing']).apply(lambda num: num**2)).sum(axis=1)))
    dataset['guard'] = np.exp(-np.sqrt(((dataset[['ast_100', 'drb_100', 'fg3a_100', 'rim_fga_100', 'stl_100']] - pivot.loc['guard']).apply(lambda num: num**2)).sum(axis=1)))
    #dataset['sg'] = np.exp(-np.sqrt(((dataset[['ast_100', 'drb_100', 'fg3a_100', 'rim_fga_100', 'stl_100']] - pivot.loc['sg_pos']).apply(lambda num: num**2)).sum(axis=1)))
    #dataset['pg'] = np.exp(-np.sqrt(((dataset[['ast_100', 'drb_100', 'fg3a_100', 'rim_fga_100', 'stl_100']] - pivot.loc['pg_pos']).apply(lambda num: num**2)).sum(axis=1)))

    dataset['sum'] = dataset['big']+dataset['wing']+dataset['guard'] #+dataset['sg']+dataset['pg']
    dataset[['big','wing','guard']] = dataset.loc[:,"big":"guard"].div(dataset["sum"], axis=0)

    dataset.loc[dataset['position']=='big','big'] += 1
    dataset.loc[dataset['position']=='wing','wing'] += 1
    dataset.loc[dataset['position']=='guard','guard'] += 1
    dataset['sum'] = dataset['big']+dataset['wing']+dataset['guard'] #+dataset['sg']+dataset['pg']
    dataset[['big','wing','guard']] = dataset.loc[:,"big":"guard"].div(dataset["sum"], axis=0)

    dataset = dataset[['player_name', 'team_name', 'position', 'x_position','minutes','big', 'wing', 'guard']]
    dataset = dataset[dataset['team_name'].isin(teams)]
    dataset = dataset.sort_values(by=['team_name','minutes'],ascending=[True,False])
    dataset['adj_minutes'] = dataset['minutes'].copy()
    return DARKO,dataset

def adjust_mins(dataset,orgs,positions):
    dataset = dataset[dataset['team_name']==orgs]
    dataset['minutes_big'] = dataset['minutes'] * dataset['big']
    dataset['minutes_wing'] = dataset['minutes'] * dataset['wing']
    dataset['minutes_guard'] = dataset['minutes'] * dataset['guard']
    
    for col in dataset.columns[8:]:
        dataset[f'{col}_rank'] = dataset[col].rank(ascending=False)
    
    for p in positions:
        decay = 1; limits = 1
        #print(p,'minutes optimized')
        if(p=='big'): limits=2
        dataset[f'adj_minutes_{p}'] = dataset[f'minutes_{p}'].copy()
        while(dataset[f'adj_minutes_{p}'].sum()<95.9/limits or dataset[f'adj_minutes_{p}'].sum()>96.1/limits):
            
            if(dataset[f'minutes_{p}'].sum()>96/limits): dataset[f'adj_minutes_{p}'] = dataset[f'minutes_{p}'] * np.power(decay,-dataset[f'minutes_{p}_rank'])
            if(dataset[f'minutes_{p}'].sum()<96/limits): dataset[f'adj_minutes_{p}'] = dataset[f'minutes_{p}'] * np.power(decay,dataset[f'minutes_{p}_rank'])        
            decay += 0.0001
            #print(decay,dataset[f'adj_minutes_{p}'].sum())
        
    dataset['adj_minutes'] = dataset['adj_minutes_guard'] + dataset['adj_minutes_wing'] + dataset['adj_minutes_big']
    dataset = dataset[['player_name', 'team_name', 'position', 'x_position','minutes','adj_minutes','big', 'wing', 'guard']]
    return dataset

def aggregate_mins(dataset,teams,positions):
    dataset_a = adjust_mins(dataset,teams[0],positions)
    dataset_b = adjust_mins(dataset,teams[1],positions)
    dataset = pd.concat([dataset_a, dataset_b], axis=0)
    dataset.loc[dataset['adj_minutes']==0,'adj_minutes'] = 0.1
    dataset = dataset.sort_values(by=['team_name','adj_minutes'],ascending=[True,False])
    return dataset
    

def extract_data_DARKO_v2(box_talent,p_mins):
    p_mins = p_mins[['player_name', 'team_name', 'adj_minutes']]
    #box_talent = pd.read_html('https://spreadsheets.google.com/tq?tqx=out:html&tq=&key=1mhwOLqPu2F9026EQiVxFPIN1t9RGafGpl-dokaIsm9c&gid=284274620')[0]
    #box_talent = header_first_row(box_talent)
    full_player_list = box_talent[['player_name','team_name']]
    
    for x in box_talent.values:
        try:
            box_talent.loc[box_talent['player_name']==x[1],'minutes'] = p_mins.loc[p_mins['player_name']==x[1],'adj_minutes'].values[0]
        except:
            box_talent.loc[box_talent['player_name']==x[1],'minutes'] = 0.1
    
    box_talent['pts_100'] = box_talent['pts_100'].str.replace(r'%', '', regex=True)
    box_talent['pts'] = (pd.to_numeric(box_talent['pts_100'])/100) * (box_talent['pace']/100) * (box_talent['minutes']/48)

    box_talent['blk'] = (box_talent['blk_100']) * (box_talent['pace']/100) * (box_talent['minutes']/48)

    box_talent['orb_100'] = box_talent['orb_100'].str.replace(r'%', '', regex=True)
    box_talent['orb'] = (pd.to_numeric(box_talent['orb_100'])/100) * (box_talent['pace']/100) * (box_talent['minutes']/48)

    box_talent['drb_100'] = box_talent['drb_100'].str.replace(r'%', '', regex=True)
    box_talent['drb'] = (pd.to_numeric(box_talent['drb_100'])/100) * (box_talent['pace']/100) * (box_talent['minutes']/48)

    box_talent['ast'] = (box_talent['ast_100']) * (box_talent['pace']/100) * (box_talent['minutes']/48)
    box_talent['tov'] = (box_talent['tov_100']) * (box_talent['pace']/100) * (box_talent['minutes']/48)
    box_talent['stl'] = (box_talent['stl_100']) * (box_talent['pace']/100) * (box_talent['minutes']/48)
    box_talent['fg3a'] = (box_talent['fg3a_100']) * (box_talent['pace']/100) * (box_talent['minutes']/48)
    box_talent['fga'] = (box_talent['fga_100']) * (box_talent['pace']/100) * (box_talent['minutes']/48)

    box_talent['3PAr'] = box_talent['fg3_ar'].str.replace(r'%', '', regex=True)
    box_talent['3PAr'] = (pd.to_numeric(box_talent['3PAr'])/100)

    box_talent['FTr'] = box_talent['ft_ar'].str.replace(r'%', '', regex=True)
    box_talent['FTr'] = (pd.to_numeric(box_talent['FTr'])/100)
    
    f_points = box_talent[['nba_id','player_name', 'team_name', 'minutes', 'pts', 'blk', 'orb', 'drb', 'ast', 'tov', 'stl', 'fga', '3PAr', 'FTr']]
    f_points.rename(columns = {'nba_id':'playerid'}, inplace = True)
    f_points = f_points.sort_values(by=['minutes'],ascending=False)
    #f_points = f_points.loc[f_points['minutes']>0.1]
    return f_points,full_player_list

def assign_prices(file,f_points):
    try:
        data = pd.read_excel(file,'DARKO')
        data = data.fillna(100)
        f_points = f_points.merge(data, on='player_name', how='left')
        f_points = f_points.fillna(100)
        f_points = f_points.drop(['squad'],axis=1)
    except FileNotFoundError:
        f_points['pos'] = 1
        f_points['cost'] = 0.5
    return f_points
    
def header_first_row(df):
    new_header = df.iloc[0] #grab the first row for the header
    df = df[1:] #take the data less the header row
    df.columns = new_header #set the header row as the df header
    df = df.apply(pd.to_numeric, errors='ignore')
    return df

def clustering_known_centroids(f_points):
    sample = pd.read_excel('C:/Users/GF63/Desktop/cricket/barttorvik/nba_roles.xlsx','sample')
    centroids = pd.read_excel('C:/Users/GF63/Desktop/cricket/barttorvik/nba_roles.xlsx','centroids')
    centroids2 = centroids.copy()
    
    f_points['FGA/36'] = 36*f_points['fga']/f_points['minutes']
    f_points['OREB/36'] = 36*f_points['orb']/f_points['minutes']
    f_points['DREB/36'] = 36*f_points['drb']/f_points['minutes']
    f_points['AST/36'] = 36*f_points['ast']/f_points['minutes']
    f_points['TOV/36'] = 36*f_points['tov']/f_points['minutes']
    f_points['BLK/36'] = 36*f_points['blk']/f_points['minutes']
    f_points['STL/36'] = 36*f_points['stl']/f_points['minutes']
    f_points['season'] = -1
    f_points['player'] = f_points['player_name']
    f_points['MIN'] = f_points['minutes']

    roles = f_points[['playerid','player','season','MIN','FGA/36','OREB/36','DREB/36','AST/36','TOV/36','BLK/36','STL/36','3PAr','FTr']]
    roles = pd.concat([sample, roles], axis=0)
    
    centroids = centroids.drop(['Cluster','role'],axis=1)
    centroids = centroids.to_numpy()
    data = roles[['FGA/36', 'OREB/36', 'DREB/36', 'AST/36', 'TOV/36', 'BLK/36', 'STL/36', '3PAr', 'FTr']]
    data = data.apply(zscore)
    kmeans_model = KMeans(init=centroids, n_clusters=5, n_init=1)
    roles['Cluster'] = kmeans_model.fit_predict(data)
    
    for x in roles.values:
        roles.loc[(roles['playerid']==x[0])&(roles['season']==x[2]),'role'] = centroids2.loc[centroids2['Cluster']==x[13],'role'].values[0]
    
    roles = roles.loc[roles['season']==-1]
    return roles

def player_stdev(f_points):
    f_points.loc[f_points['role b']=='center','stdev'] = 6.9 + f_points['xPts'] * 0.168
    f_points.loc[f_points['role b']=='forward','stdev'] = 5.93 + f_points['xPts'] * 0.206
    f_points.loc[f_points['role b']=='passer','stdev'] = 5.98 + f_points['xPts'] * 0.205
    f_points.loc[f_points['role b']=='shooter','stdev'] = 5.46 + f_points['xPts'] * 0.23
    f_points.loc[f_points['role b']=='star','stdev'] = 8.12 + f_points['xPts'] * 0.098
    return f_points

def f_points_clean_up(f_points,redo_clustering):
    if(redo_clustering == 0):
        #f_points['3PAr'] = f_points['3PAr'].str.replace(r'%', '', regex=True)
        #f_points['3PAr'] = pd.to_numeric(f_points['3PAr'])/100
        #f_points['FTr'] = f_points['FTr'].str.replace(r'%', '', regex=True)
        #f_points['FTr'] = pd.to_numeric(f_points['FTr'])/100
        #f_points['fga'] = f_points['fg3a']/f_points['3PAr']
        #f_points['tov'] = f_points['ast']/f_points['ast/tov']
    
        roles = clustering_known_centroids(f_points)
        f_points['role b'] = roles['role']
        f_points['xPts'] = f_points['pts']+1.2*f_points['orb']+1.2*f_points['drb']+1.5*f_points['ast']+3*(f_points['stl']+f_points['blk'])-f_points['tov']
        f_points = f_points[['player_name', 'team_name', 'role b','minutes', 'pts', 'blk', 'orb', 'drb',
                             'ast', 'stl','tov','xPts']]
    else:
        #f_points['xPts'] = f_points['xPts/min']*f_points['minutes']
        f_points['old_minutes'] = f_points['xPts']/f_points['xPts/min']
        f_points['pts'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['blk'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['orb'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['drb'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['ast'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['stl'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['tov'] *=  f_points['minutes']/f_points['old_minutes']
        f_points['xPts'] = f_points['pts']+1.2*f_points['orb']+1.2*f_points['drb']+1.5*f_points['ast']+3*(f_points['stl']+f_points['blk'])-f_points['tov']
        
        f_points = f_points.sort_values(by=['minutes'],ascending=False)
        f_points = f_points.drop('old_minutes', axis=1)

    f_points = player_stdev(f_points)
    f_points['count'] = f_points.groupby(['role b','team_name']).cumcount() + 1
    f_points["role"] = f_points["role b"] + " " + f_points["count"].astype(str)
    f_points = f_points.drop('count',axis=1)
    f_points = f_points.sort_values(by=['team_name','minutes'],ascending=[True,False])
    return f_points

def covariance_matrix(f_points,correlation,team):
    covariance = pd.DataFrame(columns=correlation.columns, index=correlation.index)
    for x in covariance.columns:
        for y in covariance.index:
            covariance[x][y] = f_points.loc[(f_points['role']==x)&(f_points['team_name']==team),'stdev'].sum() \
                             * f_points.loc[(f_points['role']==y)&(f_points['team_name']==team),'stdev'].sum() \
                             * correlation[x][y]
        
    covariance = covariance.fillna(0)
    return covariance

def multivariate_sim(f_points,correlation,team):
    covariance = covariance_matrix(f_points,correlation,team)
    xpts = pd.DataFrame(columns=['player_name','xPts'], index=covariance.index)
    for z in xpts.index:
        try:
            xpts['xPts'][z] = f_points.loc[(f_points['role']==z)&(f_points['team_name']==team),'xPts'].sum()
            xpts['player_name'][z] = f_points.loc[(f_points['role']==z)&(f_points['team_name']==team),'player_name'].values[0]
        except:
            xpts['xPts'][z] = 0
            xpts['player_name'][z] = 'NA'
            
    xpts['xPts'] = multivariate_normal.rvs(mean=xpts.iloc[:,1], cov=covariance)
    xpts = xpts.loc[xpts['player_name']!='NA']
    return xpts

def solver(f_points):
    duplicate = f_points.copy()
    dummy_team = duplicate['team_name'][0]
    duplicate['dummy_team'] = np.where(duplicate['team_name']==dummy_team,1,0)
    duplicate['PG'] = np.where(duplicate['pos']==1,1,0)
    duplicate['SG'] = np.where(duplicate['pos']==2,1,0)
    duplicate['SF'] = np.where(duplicate['pos']==3,1,0)
    duplicate['PFs'] = np.where(duplicate['pos']==4,1,0)
    duplicate['C'] = np.where(duplicate['pos']==5,1,0)
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
    model += (lpSum( x[k] * duplicate['cost'][k] for k in range (0, len(duplicate))) <= 100, "cost")
    model += (lpSum( x[k] * duplicate['PG'][k] for k in range (0, len(duplicate))) >= 1, "PG")
    model += (lpSum( x[k] * duplicate['SG'][k] for k in range (0, len(duplicate))) >= 1, "SG")
    model += (lpSum( x[k] * duplicate['SF'][k] for k in range (0, len(duplicate))) >= 1, "SF")
    model += (lpSum( x[k] * duplicate['PFs'][k] for k in range (0, len(duplicate))) >= 1, "PF")
    model += (lpSum( x[k] * duplicate['C'][k] for k in range (0, len(duplicate))) >= 1, "C")
    model += (lpSum( x[k] * duplicate['dummy_team'][k] for k in range (0, len(duplicate))) >= 3, "Team min")
    model += (lpSum( x[k] * duplicate['dummy_team'][k] for k in range (0, len(duplicate))) <= 5, "Team max")
    
    for k in range (0, len(duplicate)): model += (x[k]-c[k]-vc[k] >= 0,f"unique C-VC {k}")
    
    # Set objective
    model += lpSum( (x[k]+c[k]+0.5*vc[k]) * duplicate['xPts'][k] for k in range (0, len(duplicate)))
    
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

def iterator(f_points,n,teams):
    print()
    for t in teams: print(round(f_points.loc[f_points['team_name']==t,'pts'].sum(),1),t,"(",round(f_points.loc[f_points['team_name']==t,'minutes'].sum(),1),")")
    print()
    #review this!
    f_points = f_points[f_points['minutes'] >= 2]
    f_points.reset_index(drop=True, inplace=True)
    a_team = [["1","2","3","4","5","6","7","8","Star","Pro","xPts",'xMins','Cost']];
    k=1
    while(k<n+1):      
        #random noise introduced in mins/efficiency
        f_points_copy = f_points.copy()
        if(k>1):
            t1_sim = multivariate_sim(f_points,correlation,teams[0])
            t2_sim = multivariate_sim(f_points,correlation,teams[1])
            for i in f_points_copy['player_name'].values:
                f_points_copy.loc[(f_points_copy['team_name']==teams[0])&(f_points_copy['player_name']==i),'xPts'] = t1_sim.loc[t1_sim['player_name']==i,'xPts'].sum()
                f_points_copy.loc[(f_points_copy['team_name']==teams[1])&(f_points_copy['player_name']==i),'xPts'] = t2_sim.loc[t2_sim['player_name']==i,'xPts'].sum()
            #print(f_points_copy[['player_name','xPts']])
        solution,xPts,cost = solver(f_points_copy)
        solution = solution.sort_values(by=['pos'],ascending=True)
        names = solution.loc[solution['Sel'] >= 1, 'player_name']
        names = names.to_list()
        
        xPts=0; xmins=0
        for j in names:
            xmins += f_points.loc[f_points['player_name'] == j, 'minutes'].values[0]
            xPts += f_points.loc[f_points['player_name'] == j, 'xPts'].values[0]
        cap = solution.loc[solution['Sel'] == 2, 'player_name']
        cap = cap.to_list()
        vice = solution.loc[solution['Sel'] == 1.5, 'player_name']
        vice = vice.to_list()
        xPts += f_points.loc[f_points['player_name'] == cap[0], 'xPts'].values[0] + (f_points.loc[f_points['player_name'] == vice[0], 'xPts'].values[0])/2
        xmins = round(xmins,2)
        names = names + cap + vice + [xPts] + [xmins] + [cost]
        if(xmins in chain(*a_team)):
            k = k - 1
        else:
            a_team.append(names)
            print(f"solution {k} found")
        k = k + 1   
    return a_team

DARKO,p_mins = projected_minutes(teams)

# %%  set custom player minutes
p_mins = aggregate_mins(p_mins,teams,['guard','wing','big'])

# %%  extract DARKO projections for the players
f_points,full_player_list = extract_data_DARKO_v2(DARKO,p_mins)
f_points = f_points[f_points['team_name'].isin(teams)]
f_points = f_points_clean_up(f_points,0)
f_points['xPts/min'] = f_points['xPts']/f_points['minutes']
f_points = assign_prices(file,f_points)
f_points = f_points.loc[f_points['minutes']>0.1]
#simulation = multivariate_sim(f_points,correlation,teams[0])

# %%  generate n unique lineups
#f_points = f_points_clean_up(f_points,1)
a_team = iterator(f_points,n,teams)
a_team = pd.DataFrame(a_team)
a_team.columns = a_team.iloc[0];a_team = a_team.drop(0)
a_team = a_team.apply(pd.to_numeric, errors='ignore')
a_team = a_team.sort_values(by=['xPts'],ascending=False)
a_team.index = np.arange(1, len(a_team)+1)
f_points = f_points.drop('role', axis=1)