def filter_players_by(players, column, value):
    return players.loc[players[column] >= value]


def top_paid_players(df):
    top_three = df.sort_values(by=['Cap Hit'], ascending=False).head(3)
    return top_three[[
        'H-Ref Name',
        'Position',
        'GP',
        'G',
        'A',
        'PTS',
        '+/-',
        'TOI/GP',
        'IPP%',
        'Cap Hit',
        ]]


def cap_hit_share(players, cap_hit):
    return players['Cap Hit'].sum() / cap_hit * 100


def points_share(players, points):
    return players['PTS'].sum() / points * 100
