def filter_players_by_points(players, min_points):
    return players.loc[players['PTS'] >= min_points]


# functions related to colimn +/-
val = '+/-'

def get_defenders(df):
    return df.loc[df['Position'] == 'D']

def get_avg_val(df):
    return df[val].mean()

def get_med_val(df): 
    return df[val].median()

