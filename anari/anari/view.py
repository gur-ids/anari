def top_players_gp_mean_text(top_players):
    return 'Average games played by top scorers: {0} games'.format(top_players['GP'].mean())


def top_three_cap_hit_text(top_three_cap_hit, team_cap_hit):
    return 'Cap Hit of top three most expensive players: {0}%. Total Team Cap Hit (without goalies) is: {1}'.format(
            int(round(top_three_cap_hit)),
            team_cap_hit,
    )


def top_three_max_cap_hit_text(top_three_cap_hit, max_cap_hit):
    return 'Cap Hit of top three most expensive players: {0}%. Maximum Cap Hit is: {1}'.format(
            int(round(top_three_cap_hit)),
            max_cap_hit,
    )


def top_three_points_text(top_three_points, team_points):
    return 'Point contribution of top three most expensive players: {0}%. Total points is: {1}'.format(
        int(round(top_three_points)),
        team_points,
    )
