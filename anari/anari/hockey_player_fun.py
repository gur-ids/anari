def filter_players_by_points(players, min_points):
    return players.loc[players['PTS'] >= min_points]