import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import graphs as g
import hockey_player_fun as hpf
import hockey_player_model as hpm
import team_model as tm
import view as v
from notes import notes

# initial pre-processing
df = hpm.pre_process('../data/nhl_2017-2018.csv')
teams_df = tm.pre_process('../data/team_stats_2017-2018.csv')
df2016 = hpm.pre_process2016('../data/NHL_2016-17.csv')
print(df2016.head())

# handling pre-processed data
top_players_df = hpf.filter_players_by(df, 'Cap Hit', 4000000)

MAX_CAP_HIT = tm.get_max_cap_hit()

# produced view
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.layout = html.Div([
    html.H1(children='NHL meik mani'),
    dcc.Tabs(id="tabs", value='basic-info-tab', children=[
        dcc.Tab(label='Basic Info', value='basic-info-tab'),
        dcc.Tab(label='Team stats', value='team-stats'),
    ]),
    html.Div(id='tabs-content'),
])

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'basic-info-tab':
        return html.Div(children=[
            g.box_plot_by_points(top_players_df),
            g.scatter_plot_toi_pts('toi_pts', top_players_df),
            dcc.Markdown(notes),
        ])
    elif tab == 'team-stats':
        return html.Div(id='render_team_stats')


position_filter_data = [
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

left_table_y_label = ['+/-', 'Age', 'Salary', 'Cap Hit', 'TOI/GP', 'IPP%', 'PAX']
right_table_x_label = ['+/-', 'Age', 'PTS', 'Cap Hit', 'TOI/GP', 'PAX', 'IPP%', 'Salary']

@app.callback(Output('render_team_stats', 'children'),
              [Input('tabs', 'value')])
def render_team_stats(tab):
    return html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='y_axis_condition',
                    options=[{'label': i, 'value': i} for i in left_table_y_label],
                    value='+/-'),
                dcc.Checklist(
                    id='player_position_filter',
                    options=[{'label': i.get('label'), 'value': i.get('value')} for i in position_filter_data],
                    value=['C', 'D', 'LW', 'RW'],
                    labelStyle={'display': 'inline-block'}
                ),
                dcc.RadioItems(
                    id='agg_method',
                    options=[{'label': i.get('label'), 'value': i.get('value')} for i in position_agg_method],
                    value='mean',
                    labelStyle={'display': 'inline-block'}
                )
            ], className="six columns"),
            html.Div([
                dcc.Dropdown(
                    id='x_axis_condition',
                    options=[{'label': i, 'value': i} for i in right_table_x_label],
                    value='PTS')
            ], className="six columns")
        ], className="row"),

        html.Div([
            html.Div([
                dcc.Graph(id='teams-overview'),
            ], className="six columns"),

            html.Div(
                children=[
                    html.Div(id='team-details-scatter'),
                    html.Div(id='team-details-distribution'),
                    html.Div(id='team-details-top-paid'),
                ],
                className="six columns",
            )
        ], className="row")

    ], style={'display': 'none' if tab != 'team-stats' else 'block'})


@app.callback(
    Output('teams-overview', 'figure'),
    [
        Input('player_position_filter', 'value'),
        Input('y_axis_condition', 'value'),
        Input('agg_method', 'value'),
    ])
def update_overview_team_graphs(player_positions, criteria, agg_method):
    teams_subset = tm.top_bottom_teams(teams_df)
    players_of_team = tm.get_teams(df, teams_subset['Team'])
    players_of_team = players_of_team[players_of_team.Position.isin(player_positions)]

    if agg_method == 'mean':
        players_of_team = tm.get_mean_by(players_of_team, criteria)
    elif agg_method == 'variance':
        players_of_team = tm.get_variance_by(players_of_team, criteria)
    elif agg_method == 'sum':
        players_of_team = tm.get_sum_by(players_of_team, criteria)

    teams_subset = teams_subset.merge(players_of_team, left_on='Team', right_on='Team')

    return g.update_overview_team_graphs(teams_subset, criteria, agg_method)


@app.callback(
    [
        Output('team-details-scatter', 'children'),
        Output('team-details-distribution', 'children'),
        Output('team-details-top-paid', 'children'),
    ],
    [
        Input('teams-overview', 'hoverData'),
        Input('player_position_filter', 'value'),
        Input('y_axis_condition', 'value'),
        Input('x_axis_condition', 'value'),
    ])
def update_detailed_team_graphs(hoverData, player_positions, criteria, other_criteria):
    team_name = hoverData['points'][0]['customdata'] if hoverData is not None else 'NSH'
    players = tm.get_team(df, team_name)
    players = players[players.Position.isin(player_positions)]

    top_paid_df = hpf.top_paid_players(players)
    cap_hit = tm.get_team_total_cap_hit(players)
    top_paid_cap_hit = hpf.cap_hit_share(top_paid_df, cap_hit)
    top_paid_cap_hit_total = hpf.cap_hit_share(top_paid_df, MAX_CAP_HIT)
    points = tm.get_team_total_points(players)
    top_paid_points = hpf.points_share(top_paid_df, points)

    title = v.team_detail_title(hoverData, criteria, other_criteria)

    scatter = g.update_detailed_team_graphs(players, other_criteria, criteria, title)
    distribution = g.cap_hit_distribution(players)

    top_paid = [
        g.generate_table(top_paid_df),
        html.P(v.top_paid_cap_hit_text(top_paid_cap_hit, cap_hit)),
        html.P(v.top_paid_max_cap_hit_text(top_paid_cap_hit_total, MAX_CAP_HIT)),
        html.P(v.top_paid_points_text(top_paid_points, points)),
    ]

    return scatter, distribution, top_paid


# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
