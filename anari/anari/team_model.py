import pandas as pd

def pre_process(path):
    return pd.read_csv(path)

def get_team(df, team_name):
    return df.loc[df['Team'] == team_name]

def get_team_avg_scores(df): 
    return df.groupby(['Team'], as_index = False).mean()