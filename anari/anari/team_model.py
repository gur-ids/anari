import pandas as pd

MAX_CAP_HIT_MILLIONS = 75000000


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
    return df.groupby(['Team'], as_index=False).mean()


def get_mean_by(df, criteria):
    return df.groupby('Team', as_index=False)[criteria].mean()


def get_variance_by(df, criteria):
    return df.groupby('Team', as_index=False)[criteria].var()


def get_sum_by(df, criteria):
    return df.groupby('Team', as_index=False)[criteria].sum()


def get_team_total_cap_hit(df):
    return df['Cap Hit'].sum()


def get_max_cap_hit():
    return MAX_CAP_HIT_MILLIONS


def get_team_total_points(df):
    return df['PTS'].sum()


def get_team_full_name(df, team_name):
    return df.loc[df['Team'] == team_name, 'Team Name']


def top_bottom_teams(teams):
    return teams.sort_values(by='Points', ascending=False)
