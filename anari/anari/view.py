def top_paid_cap_hit_text(top_paid_cap_hit, team_cap_hit):
    return 'Cap Hit of top three most expensive players: {0}%. Total Team Cap Hit (without goalies) is: {1}'.format(
            int(round(top_paid_cap_hit)),
            team_cap_hit,
    )


def top_paid_max_cap_hit_text(top_paid_cap_hit, max_cap_hit):
    return 'Cap Hit of top three most expensive players: {0}%. Maximum Cap Hit is: {1}'.format(
            int(round(top_paid_cap_hit)),
            max_cap_hit,
    )


def top_paid_points_text(top_paid_points, team_points):
    return 'Point contribution of top three most expensive players: {0}%. Total points is: {1}'.format(
        int(round(top_paid_points)),
        team_points,
    )
