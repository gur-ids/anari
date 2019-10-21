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


def team_detail_title(hoverData, criteria, other_criteria):
    return '<b>{0}</b><br>{1}'.format(
        hoverData['points'][0]['text'] if hoverData is not None else 'Nashville Predators',
        other_criteria + ', ' + criteria
    )


def name_salary(name, salary):
    milli = '${:,.2f}M'.format(salary/1000000)
    return name + ', ' + milli


position_label_values = [
        {'label': 'Center', 'value': 'C'},
        {'label': 'Defenceman', 'value': 'D'},
        {'label': 'Left Wing', 'value': 'LW'},
        {'label': 'Right Wing', 'value': 'RW'}
    ]

position_agg_method = [
        {'label': 'Mean', 'value': 'mean'},
        {'label': 'Variance', 'value': 'variance'},
        {'label': 'Sum', 'value': 'sum'},
    ]

dropdown_label_values = [
    {'value': '+/-', 'label': 'Points gained or lost in total while on ice during even game'},
    {'value': 'Age', 'label': 'Age of player'},
    {'value': 'Salary', 'label': 'Yearly salary'},
    {'value': 'Cap Hit', 'label': 'Yearly salary without bonuses'},
    {'value': 'TOI/GP', 'label': 'Time on ice per game played'},
    {'value': 'IPP%', 'label': 'Percentage of being present on ice during goals vs all goals'},
    {'value': 'PTS', 'label': 'Points (Assists + Scored goals)'}
]
