# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 17:44:13 2025

@author: Subramanya.Ganti
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

start_season = 2021
end_season = 2025

i = start_season; df_all = []
while(i<end_season+1):
    df = pd.read_excel('C:/Users/Subramanya.Ganti/Downloads/cricket/excel/bart/results.xlsx',f'{i}')
    first_column_name = df.columns[0]
    df.drop(columns=[first_column_name], inplace=True)
    df_all.append(df)
    i += 1
    
df_all = pd.concat(df_all)
df_all.reset_index(drop=True, inplace=True)

def cluster_dataframe(df, cluster_cols, avg_col, n_clusters):
    """
    Clusters a DataFrame based on specified columns, adds cluster labels,
    and orders clusters by the average of another column.

    Args:
        df (pd.DataFrame): Input DataFrame.
        cluster_cols (list): List of column names to use for clustering.
        avg_col (str): Column name to use for ordering clusters.
        n_clusters (int): Number of clusters.

    Returns:
        pd.DataFrame: DataFrame with added cluster labels and ordered clusters.
    """

    # Scale the clustering columns
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(df[cluster_cols])

    # Perform K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, n_init = 'auto') #random_state = ?
    df['cluster'] = kmeans.fit_predict(scaled_features)

    # Calculate average of avg_col for each cluster
    cluster_means = df.groupby('cluster')[avg_col].mean().sort_values(ascending=False).index
    #print(df.groupby('cluster')[avg_col].mean())

     # Create a mapping from original cluster labels to ordered labels
    cluster_mapping = {old_label: new_label for new_label, old_label in enumerate(cluster_means)}

    # Apply the mapping to the 'cluster' column
    df['cluster'] = df['cluster'].map(cluster_mapping)
    df['cluster'] = df['cluster'] + 1
    df = df.sort_values(by=['cluster', 'rotation'], ascending=[True, False])
    df = df.set_index('cluster')
    
    return df

df_all = cluster_dataframe(df_all.copy().reset_index(drop=True),['bust','rotation','starter','all star','all nba','mvp','floor','ceil'],'ceil',6)

i = start_season; df_final = []
while(i<end_season+1):
    df = df_all[df_all['season'] == i]
    df = df.drop_duplicates(subset=['player'], keep='first')
    df_final.append(df)
    i += 1

del i; del df; del first_column_name
