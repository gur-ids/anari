import pandas as pd

def pre_process(path):
    return pd.read_csv(path)

def get_team(df, team_name):
    return df.loc[df['Team'] == team_name]
def get_teams(df, team_names):
    dfr = pd.DataFrame()
    for name in team_names:
        dfr = dfr.append(get_team(df, name))
    return dfr

def get_team_avg_scores(df): 
    return df.groupby(['Team'], as_index = False).mean()
