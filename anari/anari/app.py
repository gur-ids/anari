import dash
import dash_html_components as html
import hockey_player_model as hpm
import hockey_player_fun as hpf
import graphs as g
import view as v
import pandas as pd
import team_model as tm
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# initial pre-processing
df = hpm.pre_process('../data/nhl_2017-2018.csv')
teams = tm.pre_process('../data/team_stats_2017-2018.csv')

# handling pre-processed data
offenders = hpm.offenders(df)
defenders = hpm.defenders(df)
tm.is_beneficial_to_team(df)


top_players = hpf.filter_players_by_points(df, 50)

# produced view
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True
'''
app.layout=html.Div(children=[
    html.H4(children='NHL meik mani'),
    html.P('Here is a table of the top scorers'),
    html.P(children=v.top_players_gp_mean_text(top_players)),
    g.box_plot_by_points(offenders),
    g.scatter_plot_teams('test_id2', teams),
    g.scatter_plot_players('test_id', top_players)
])
'''
app.suppress_callback_exceptions=True
app.layout = html.Div([
    html.H1('Dash Tabs component demo'),
    dcc.Tabs(id="tabs-example", value='basic-info-tab', children=[
        dcc.Tab(label='Basic Info', value='basic-info-tab'),
        dcc.Tab(label='Make statistics great again', value='great-stat-tab'),
        dcc.Tab(label='test', value='test')
    ]),
    html.Div(id='tabs-content-example'),
    html.Div(id='render_team_stats')
])

@app.callback(Output('tabs-content-example', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'basic-info-tab':
        return html.Div(children=[
            html.H4(children='NHL meik mani'),
            html.P('Here is a table of the top scorers'),
            html.P(children=v.top_players_gp_mean_text(top_players)),
            g.box_plot_by_points(offenders),
            g.scatter_plot_teams('test_id2', teams),
            g.scatter_plot_players('test_id', top_players)
        ])
    elif tab == 'great-stat-tab':
        return html.Div([
            html.H3('Tab content 2'),
            dcc.Graph(
                id='graph-2-tabs',
                figure={
                    'data': [{
                        'x': teams['Team'],
                        'y': teams['Points'],
                        'type': 'bar'
                    }]
                }
            )
        ])        

def top_bottom_teams(teams):
    teams = teams.sort_values(by = 'Points', ascending = False)
    df = teams.head(5)
    df = df.append(teams.tail(5))
    return df

position_filter_data = [
    {'label': 'center', 'value': 'C'},
    {'label': 'defender', 'value': 'D'},
    {'label': 'left', 'value': 'LW'},
    {'label': 'right', 'value': 'RW'}
]
position_agg_method = [
    {'label': 'Mean', 'value': 'mean'},
    {'label': 'Variance', 'value': 'variance'}
]

y_available_criterias = ['+/-', 'Age', 'Salary']
x_available_criterias = ['+/-', 'Age', 'PTS']

@app.callback(Output('render_team_stats', 'children'),
              [Input('tabs-example', 'value')])
def render_team_stats(tab):

    return html.Div([
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='y_axis_condition',
                    options=[{'label': i, 'value': i} for i in y_available_criterias],
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
                    options=[{'label': i, 'value': i} for i in x_available_criterias],
                    value='PTS')
            ], className="six columns")
        ], className="row"),
        html.Div([
            html.Div([
                dcc.Graph(id='teams_overview'),
            ], className="six columns"),

            html.Div([
                dcc.Graph(id='team_details')
            ], className="six columns")
        ], className="row")

    ],style={'display': 'none' if tab != 'test' else 'block'})

@app.callback(
    dash.dependencies.Output('teams_overview', 'figure'),
    [dash.dependencies.Input('player_position_filter', 'value'),
    dash.dependencies.Input('y_axis_condition', 'value'),
    dash.dependencies.Input('agg_method', 'value')])
def update_overview_team_graphs(player_positions, criteria, agg_method):
    teams_subset = top_bottom_teams(teams)
    players_of_team = tm.get_teams(df, teams_subset['Team'])
    players_of_team = players_of_team[players_of_team.Position.isin(player_positions)]
    if agg_method == 'mean':
        players_of_team = players_of_team.groupby('Team', as_index=False)[criteria].mean()
    elif agg_method == 'variance':
        players_of_team = players_of_team.groupby('Team', as_index=False)[criteria].var()

    teams_subset=teams_subset.merge(players_of_team, left_on='Team', right_on='Team')
    return {
        'data': [go.Scatter(
                    x=teams_subset['Points'],
                    y=teams_subset[criteria],
                    text=teams_subset['Team Name'],
                    customdata=teams_subset['Team'],
                    mode='markers',
                    marker={
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                )],
                'layout': go.Layout(
                    xaxis={
                        'title': 'Team points',
                        'type': 'linear'
                    },
                    yaxis={
                        'title': 'avg ' + criteria,
                        'type': 'linear'
                    },
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }

@app.callback(
    dash.dependencies.Output('team_details', 'figure'),
    [dash.dependencies.Input('teams_overview', 'hoverData'),
    dash.dependencies.Input('player_position_filter', 'value'),
    dash.dependencies.Input('y_axis_condition', 'value'),
    dash.dependencies.Input('x_axis_condition', 'value')])
def update_detailed_team_graphs(hoverData, player_positions, criteria, other_criteria):
    team_name = hoverData['points'][0]['customdata'] if hoverData != None else 'NSH'
    players = tm.get_team(df, team_name)
    players = players[players.Position.isin(player_positions)]
    title = '<b>{}</b><br>{}'.format(
        hoverData['points'][0]['text'] if hoverData != None else 'Nashville Predators',
        other_criteria + ',' + criteria)
    return {
        'data': [
            go.Scatter(
                x=players[players['Position'] == i][other_criteria],
                y=players[players['Position'] == i][criteria],
                text=players[players['Position'] == i]['Last Name'],
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name=i
            ) for i in players.Position.unique()
        ],
        'layout': go.Layout(
            xaxis={
                'title': other_criteria,
                'type': 'linear'
            },
            yaxis={
                'title': criteria,
                'type': 'linear'
            },
            legend={'x': 0, 'y': 1},
            hovermode='closest',
            title=title
        )
    }

# run webapp if main
if __name__ == '__main__':
    app.run_server(debug=True, port=4200)
