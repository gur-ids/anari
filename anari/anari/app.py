import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
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

# handling pre-processed data
top_players_df = hpf.filter_players_by(df, 'Cap Hit', 4000000)

w_top_df = tm.get_team(df, 'NSH')
w_bottom_df = tm.get_team(df, 'COL')
w_out_df = tm.get_team(df, 'STL')

w_top_name = tm.get_team_full_name(teams_df, 'NSH')
w_bottom_name = tm.get_team_full_name(teams_df, 'COL')
w_out_name = tm.get_team_full_name(teams_df, 'STL')

max_cap_hit = tm.get_max_cap_hit()

w_bottom_top_paid_df = hpf.top_paid_players(w_bottom_df)
w_bottom_cap_hit = tm.get_team_total_cap_hit(w_bottom_df)
w_bottom_top_paid_cap_hit = hpf.cap_hit_share(w_bottom_top_paid_df, w_bottom_cap_hit)
w_bottom_top_paid_cap_hit_total = hpf.cap_hit_share(w_bottom_top_paid_df, max_cap_hit)
w_bottom_points = tm.get_team_total_points(w_bottom_df)
w_bottom_top_paid_points = hpf.points_share(w_bottom_top_paid_df, w_bottom_points)

# produced view
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.layout = html.Div([
    html.H1(children='NHL meik mani'),
    dcc.Tabs(id="tabs", value='basic-info-tab', children=[
        dcc.Tab(label='Basic Info', value='basic-info-tab'),
        dcc.Tab(label='Make statistics great again', value='great-stat-tab'),
        dcc.Tab(label='Team stats', value='team-stats'),
    ]),
    html.Div(id='tabs-content'),
    html.Div(id='render_team_stats')
])

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'basic-info-tab':
        return html.Div(children=[
            g.box_plot_by_points(top_players_df),
            g.scatter_plot_toi_pts('toi_pts', top_players_df)
        ])
    elif tab == 'great-stat-tab':

        team_trace_w_top = go.Histogram(
                x=w_top_df['Cap Hit'],
        )

        team_trace_out = go.Histogram(
                x=w_out_df['Cap Hit'],
        )

        return html.Div([
            dcc.Markdown(notes),
            html.H1(children='Western Conference'),

            # TODO: use functions
            html.H2(children=w_top_name),
            dcc.Graph(
                figure={
                    'data': [team_trace_w_top],
                    'layout': {
                        'title': 'Cap Hit distribution',
                    },
                }
            ),
            # TODO: top players

            html.H2(children=w_bottom_name),
            g.cap_hit_distribution(w_bottom_df),
            g.generate_table(w_bottom_top_paid_df),
            html.Div([
                html.P(v.top_paid_cap_hit_text(w_bottom_top_paid_cap_hit, w_bottom_cap_hit)),
                html.P(v.top_paid_max_cap_hit_text(w_bottom_top_paid_cap_hit_total, max_cap_hit)),
                html.P(v.top_paid_points_text(w_bottom_top_paid_points, w_bottom_points)),
            ]),

            # TODO: use functions
            html.H2(children=w_out_name),
            dcc.Graph(
                figure={
                    'data': [team_trace_out],
                    'layout': {
                        'title': 'Cap Hit distribution',
                    },
                }
            ),
            # TODO: top players
        ])


position_filter_data = [
    {'label': 'Center', 'value': 'C'},
    {'label': 'Defenceman', 'value': 'D'},
    {'label': 'Left Wing', 'value': 'LW'},
    {'label': 'Right Wing', 'value': 'RW'}
]
position_agg_method = [
    {'label': 'Mean', 'value': 'mean'},
    {'label': 'Variance', 'value': 'variance'}
]

left_table_y_label = ['+/-', 'Age', 'Salary', 'TOI/GP', 'IPP%', 'PAX']
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
                dcc.Graph(id='teams_overview'),
            ], className="six columns"),

            html.Div(
                children=[
                    dcc.Graph(id='team-details-scatter'),
                    html.P(id='team-details-distribution'),
                ],
                className="six columns",
            )
        ], className="row")

    ], style={'display': 'none' if tab != 'team-stats' else 'block'})


@app.callback(
    dash.dependencies.Output('teams_overview', 'figure'),
    [
        dash.dependencies.Input('player_position_filter', 'value'),
        dash.dependencies.Input('y_axis_condition', 'value'),
        dash.dependencies.Input('agg_method', 'value'),
    ])
def update_overview_team_graphs(player_positions, criteria, agg_method):
    teams_subset = tm.top_bottom_teams(teams_df)
    players_of_team = tm.get_teams(df, teams_subset['Team'])
    players_of_team = players_of_team[players_of_team.Position.isin(player_positions)]

    if agg_method == 'mean':
        players_of_team = tm.get_mean_by(players_of_team, criteria)
    elif agg_method == 'variance':
        players_of_team = tm.get_variance_by(players_of_team, criteria)

    teams_subset = teams_subset.merge(players_of_team, left_on='Team', right_on='Team')

    return g.update_overview_team_graphs(teams_subset, criteria)


@app.callback(
    [
        Output('team-details-scatter', 'figure'),
        Output('team-details-distribution', 'children'),
    ],
    [
        Input('teams_overview', 'hoverData'),
        Input('player_position_filter', 'value'),
        Input('y_axis_condition', 'value'),
        Input('x_axis_condition', 'value'),
    ])
def update_detailed_team_graphs(hoverData, player_positions, criteria, other_criteria):
    team_name = hoverData['points'][0]['customdata'] if hoverData is not None else 'NSH'
    players = tm.get_team(df, team_name)
    players = players[players.Position.isin(player_positions)]
    title = v.team_detail_title(hoverData, criteria, other_criteria)

    scatter = g.update_detailed_team_graphs(players, other_criteria, criteria, title)

    return scatter, 'TODO: {0}'.format(team_name)


# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
