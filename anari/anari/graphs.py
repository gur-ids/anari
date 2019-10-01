import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


def box_plot_by_points(players):
    return dcc.Graph(figure={'data': [go.Box(y=players['PTS'])]})


def scatter_plot_players(plot_id, players):
    return dcc.Graph(
        id=plot_id,
        figure={
            'data': [
                go.Scatter(
                    x=players[players['Position'] == i]['GP'],
                    y=players[players['Position'] == i]['PTS'],
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
                xaxis={'type': 'log', 'title': 'Games played'},
                yaxis={'title': 'Points scored'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )


def cap_hit_distribution(df):
    team_trace_last_in = go.Histogram(
        x=df['Cap Hit'],
    )

    return (
        dcc.Graph(
            figure={
                'data': [team_trace_last_in],
                'layout': {
                    'title': 'Cap Hit distribution',
                },
            }
        )
    )


def scatter_plot_teams(plot_id, teams):
    return dcc.Graph(
        id=plot_id,
        figure={
            'data': [
                go.Scatter(
                    x=teams[teams['Team'] == i]['Rank'],
                    y=teams[teams['Team'] == i]['Team'],
                    text=teams[teams['Team'] == i]['Team'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                    name=i
                ) for i in teams.Team.unique()
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': 'avg pts'},
                yaxis={'title': 'team name'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
